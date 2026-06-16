#!/usr/bin/env bash
# review-loop.sh — コード生成 → ビルド/テスト → レビュー を自動反復する本体。
#
# 使い方:   ./review-loop.sh <config.sh>
# 配線確認: DRY_RUN=1 ./review-loop.sh <config.sh>
#
# 終了条件: レビュー APPROVED かつ ゲート成功 / または MAX_ITERS 到達。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
source "$SCRIPT_DIR/lib/common.sh"

CODER_PROMPT="$SCRIPT_DIR/prompts/coder.md"
REVIEWER_PROMPT="$SCRIPT_DIR/prompts/reviewer.md"
LOOP_BRANCH="auto-review-loop"

# ── 設定読み込み ──────────────────────────────────────────────────
CONFIG="${1:-}"
[ -n "$CONFIG" ] || die "設定ファイルを指定してください:  ./review-loop.sh <config.sh>"
[ -f "$CONFIG" ] || die "設定ファイルが見つかりません: $CONFIG"
# shellcheck disable=SC1090
source "$CONFIG"

# 必須項目チェック / 既定値
: "${PROJECT_DIR:?PROJECT_DIR を config に設定してください}"
PROJECT_DIR="${PROJECT_DIR/#\~/$HOME}"          # 先頭の ~ を展開
[ -d "$PROJECT_DIR" ] || die "PROJECT_DIR が存在しません: $PROJECT_DIR"
SPEC_FILE="${SPEC_FILE:-}"
BUILD_CMD="${BUILD_CMD:-}"
MAX_ITERS="${MAX_ITERS:-5}"

require_claude

# ── ログ準備 ──────────────────────────────────────────────────────
RUN_ID="$(date +%Y%m%d-%H%M%S)"
RUN_DIR="$SCRIPT_DIR/logs/$RUN_ID"
mkdir -p "$RUN_DIR"
SUMMARY="$RUN_DIR/summary.md"
echo "# auto-review-loop run $RUN_ID" > "$SUMMARY"
{
  echo "- PROJECT_DIR: $PROJECT_DIR"
  echo "- BUILD_CMD:   ${BUILD_CMD:-(none)}"
  echo "- MAX_ITERS:   $MAX_ITERS"
  echo "- DRY_RUN:     ${DRY_RUN:-0}"
  echo ""
} >> "$SUMMARY"

# ── spec 読み込み ─────────────────────────────────────────────────
SPEC_TEXT="(no spec file provided)"
if [ -n "$SPEC_FILE" ]; then
  # config からの相対パスも解決
  case "$SPEC_FILE" in
    /*) : ;;
    *)  [ -f "$SPEC_FILE" ] || SPEC_FILE="$(cd "$(dirname "$CONFIG")" && pwd)/$SPEC_FILE" ;;
  esac
  [ -f "$SPEC_FILE" ] && SPEC_TEXT="$(cat "$SPEC_FILE")" || warn "SPEC_FILE が見つかりません: $SPEC_FILE （spec なしで続行）"
fi

# ── git 準備（専用ブランチで作業）────────────────────────────────
setup_git() {
  if ! git -C "$PROJECT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
    warn "PROJECT_DIR は git リポジトリではありません。差分追跡のため初期化します。"
    git -C "$PROJECT_DIR" init -q
    git -C "$PROJECT_DIR" add -A
    git -C "$PROJECT_DIR" commit -q -m "auto-review-loop: baseline" || true
  fi
  # 未コミットの変更があればベースラインとして退避コミット
  if [ -n "$(git -C "$PROJECT_DIR" status --porcelain)" ]; then
    git -C "$PROJECT_DIR" add -A
    git -C "$PROJECT_DIR" commit -q -m "auto-review-loop: snapshot before run $RUN_ID" || true
  fi
  git -C "$PROJECT_DIR" checkout -q -B "$LOOP_BRANCH"
  log "作業ブランチ: ${c_bold}$LOOP_BRANCH${c_reset}"
}

# ── ゲート実行 ────────────────────────────────────────────────────
# 成功: GATE_PASSED=1 / 失敗: GATE_PASSED=0、出力を $1 に保存
run_gate() {
  local gatelog="$1"
  if [ -z "$BUILD_CMD" ]; then
    echo "(BUILD_CMD 未設定: ゲートをスキップし成功扱い)" | tee "$gatelog"
    GATE_PASSED=1; return 0
  fi
  info "ゲート実行: ${c_dim}$BUILD_CMD${c_reset}"
  if ( cd "$PROJECT_DIR" && eval "$BUILD_CMD" ) >"$gatelog" 2>&1; then
    ok "ゲート成功"; GATE_PASSED=1
  else
    warn "ゲート失敗（出力は次のコーダーへフィードバック）"; GATE_PASSED=0
  fi
  tail -n 20 "$gatelog" | sed 's/^/    /'
}

# ── メインループ ──────────────────────────────────────────────────
setup_git

FEEDBACK=""          # 前回のレビュー指摘 / ゲートエラー
FINAL="MAX_ITERS_REACHED"

for (( iter=1; iter<=MAX_ITERS; iter++ )); do
  rule
  info "${c_bold}反復 $iter / $MAX_ITERS${c_reset}"
  ITER_DIR="$RUN_DIR/iter-$iter"; mkdir -p "$ITER_DIR"

  # ① コーダー
  CODER_INPUT="## Spec
$SPEC_TEXT
"
  if [ -n "$FEEDBACK" ]; then
    CODER_INPUT="$CODER_INPUT
## Feedback to address (from previous build/review — fix these)
$FEEDBACK
"
  fi
  info "コーダー実行..."
  run_coder "$CODER_INPUT" "$ITER_DIR/coder.log" >/dev/null

  # コミット（diff 追跡用）
  git -C "$PROJECT_DIR" add -A
  git -C "$PROJECT_DIR" commit -q -m "auto-review-loop: iter $iter" || true
  git -C "$PROJECT_DIR" diff "HEAD~1" HEAD > "$ITER_DIR/diff.patch" 2>/dev/null || \
    git -C "$PROJECT_DIR" show HEAD > "$ITER_DIR/diff.patch" 2>/dev/null || true

  # ② ゲート
  run_gate "$ITER_DIR/gate.log"

  if [ "$GATE_PASSED" != "1" ]; then
    # ゲート失敗 → レビューせず、エラーをフィードバックして次反復
    FEEDBACK="The build/test gate FAILED. Fix this first. Last output:
$(tail -n 60 "$ITER_DIR/gate.log")"
    echo "- iter $iter: gate FAILED" >> "$SUMMARY"
    continue
  fi

  # ③ レビュー
  DIFF_TEXT="$(cat "$ITER_DIR/diff.patch" 2>/dev/null)"
  [ -n "$DIFF_TEXT" ] || DIFF_TEXT="(no diff — the coder made no changes)"
  REVIEW_INPUT="## Spec
$SPEC_TEXT

## Diff to review
\`\`\`diff
$DIFF_TEXT
\`\`\`
"
  info "レビュアー実行..."
  run_reviewer "$REVIEW_INPUT" "$ITER_DIR/review.log" >/dev/null
  VERDICT="$(parse_verdict "$ITER_DIR/review.log")"

  # ④ 判定
  if [ "$VERDICT" = "APPROVED" ]; then
    ok "${c_green}${c_bold}APPROVED${c_reset} — ゲート成功 & レビュー承認"
    echo "- iter $iter: gate OK, review APPROVED" >> "$SUMMARY"
    FINAL="APPROVED"
    break
  else
    warn "CHANGES_REQUESTED — 指摘を次反復へ"
    echo "- iter $iter: gate OK, review CHANGES_REQUESTED" >> "$SUMMARY"
    # VERDICT 行を除いた本文をフィードバックに
    FEEDBACK="$(grep -viE '^[[:space:]]*VERDICT:' "$ITER_DIR/review.log")"
  fi
done

# ── まとめ ────────────────────────────────────────────────────────
rule
{
  echo ""
  echo "## 結果: $FINAL"
} >> "$SUMMARY"

if [ "$FINAL" = "APPROVED" ]; then
  ok "完了: レビュー承認で終了しました。"
else
  warn "上限 $MAX_ITERS 回に到達。承認には至りませんでした。最後の指摘は logs を参照。"
fi
echo
log "ブランチ ${c_bold}$LOOP_BRANCH${c_reset} に成果がコミットされています。"
log "ログ: ${c_bold}$RUN_DIR${c_reset}"
[ "$FINAL" = "APPROVED" ]
