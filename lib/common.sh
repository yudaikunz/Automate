#!/usr/bin/env bash
# common.sh — auto-review-loop の共通処理（ログ・CLI検出・Claude呼び出し・verdict解析）
# review-loop.sh から source される前提。単体実行はしない。

# ---- ログ -------------------------------------------------------------------
c_reset='\033[0m'; c_dim='\033[2m'; c_blue='\033[34m'; c_green='\033[32m'
c_yellow='\033[33m'; c_red='\033[31m'; c_bold='\033[1m'

log()   { printf "${c_dim}%s${c_reset} %b\n" "[$(date +%H:%M:%S)]" "$*"; }
info()  { printf "${c_blue}▶${c_reset} %b\n" "$*"; }
ok()    { printf "${c_green}✔${c_reset} %b\n" "$*"; }
warn()  { printf "${c_yellow}⚠${c_reset} %b\n" "$*"; }
err()   { printf "${c_red}x${c_reset} %b\n" "$*" >&2; }
die()   { err "$*"; exit 1; }
rule()  { printf "${c_dim}%s${c_reset}\n" "────────────────────────────────────────────────────────"; }

# ---- Claude Code CLI 検出 ---------------------------------------------------
# PATH と代表的なインストール先を探す。見つかれば CLAUDE_BIN にセット。
detect_claude() {
  if [ -n "${CLAUDE_BIN:-}" ] && command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
    return 0
  fi
  local p
  for p in claude "$HOME/.local/bin/claude" "$HOME/.claude/local/claude" \
           /usr/local/bin/claude /opt/homebrew/bin/claude "$HOME/.npm-global/bin/claude"; do
    if command -v "$p" >/dev/null 2>&1 || [ -x "$p" ]; then
      CLAUDE_BIN="$p"; return 0
    fi
  done
  return 1
}

require_claude() {
  if [ "${DRY_RUN:-0}" = "1" ]; then return 0; fi
  detect_claude || die "Claude Code CLI が見つかりません。'./setup.sh' を実行して導入してください。\n  （配線だけ試すなら DRY_RUN=1 を付けて実行できます）"
  log "Claude CLI: ${c_bold}${CLAUDE_BIN}${c_reset}"
}

# ---- コーダー役 Claude 呼び出し ---------------------------------------------
# 引数: $1=プロンプト本文  $2=出力ログのパス
# プロジェクト内のファイルを直接編集させる（headless / 自動承認）。
run_coder() {
  local prompt="$1" outlog="$2"
  if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "[DRY_RUN] coder skipped (no edits made)" | tee "$outlog"
    return 0
  fi
  ( cd "$PROJECT_DIR" && "$CLAUDE_BIN" -p "$prompt" \
      --append-system-prompt "$(cat "$CODER_PROMPT")" \
      --permission-mode "${CLAUDE_PERMISSION_MODE:-acceptEdits}" \
      --add-dir "$PROJECT_DIR" \
      --model "${CODER_MODEL:-sonnet}" \
      ${CLAUDE_EXTRA_ARGS:-} ) 2>&1 | tee "$outlog"
}

# ---- レビュアー役 Claude 呼び出し -------------------------------------------
# 引数: $1=プロンプト本文(diff込み)  $2=出力ログのパス
# 標準出力（=レビュー全文）を返す。末尾の VERDICT 行を後で解析する。
run_reviewer() {
  local prompt="$1" outlog="$2"
  if [ "${DRY_RUN:-0}" = "1" ]; then
    # 配線確認用スタブ: 直近のゲートが通っていれば承認、ダメなら差し戻し。
    if [ "${GATE_PASSED:-0}" = "1" ]; then
      printf 'DRY_RUN stub review: gate passed, nothing to flag.\nVERDICT: APPROVED\n' | tee "$outlog"
    else
      printf 'DRY_RUN stub review: gate failed.\nVERDICT: CHANGES_REQUESTED\n' | tee "$outlog"
    fi
    return 0
  fi
  ( cd "$PROJECT_DIR" && "$CLAUDE_BIN" -p "$prompt" \
      --append-system-prompt "$(cat "$REVIEWER_PROMPT")" \
      --permission-mode "${CLAUDE_REVIEW_PERMISSION_MODE:-plan}" \
      --add-dir "$PROJECT_DIR" \
      --model "${REVIEWER_MODEL:-opus}" \
      ${CLAUDE_EXTRA_ARGS:-} ) 2>&1 | tee "$outlog"
}

# ---- verdict 解析 -----------------------------------------------------------
# レビュー全文ファイルから最後の "VERDICT: X" を取り出す。
# 見つからなければ安全側に倒して CHANGES_REQUESTED 扱い。
parse_verdict() {
  local file="$1" v
  v=$(grep -oiE '^[[:space:]]*VERDICT:[[:space:]]*(APPROVED|CHANGES_REQUESTED)' "$file" 2>/dev/null \
        | tail -n1 | grep -oiE '(APPROVED|CHANGES_REQUESTED)' | tr '[:lower:]' '[:upper:]')
  if [ -z "$v" ]; then echo "CHANGES_REQUESTED"; else echo "$v"; fi
}
