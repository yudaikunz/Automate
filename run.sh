#!/usr/bin/env bash
# run.sh — Automate の単一エントリ。
#   spec.md を読み、対象(Target)とゲート(Build)を判定して自動レビューループを回す。
#
# 使い方:   ./run.sh [spec.md]
#   引数なしならリポジトリ直下の spec.md を使う。
#
# spec.md の先頭に次のメタ行を書く（順不同・大文字小文字無視）:
#   Target: <ローカルの絶対パス> または <https://github.com/user/repo.git>
#   Build:  <ビルド/テストのゲートコマンド>   （省略時は自動判定）
#   Max:    <反復上限>                          （省略時 5）
# それ以降の本文が「目標」としてコーダーに渡る。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

SPEC="${1:-$SCRIPT_DIR/spec.md}"
[ -f "$SPEC" ] || die "spec.md が見つかりません: $SPEC"

# ── メタ行の抽出（"Key: value" 形式、本文より前のみ）────────────────
meta() { grep -iE "^[[:space:]]*$1[[:space:]]*:" "$SPEC" | head -n1 | sed -E "s/^[^:]*:[[:space:]]*//; s/[[:space:]]*$//"; }
TARGET="$(meta Target)"
BUILD="$(meta Build)"
MAX="$(meta Max)"
[ -n "$TARGET" ] || die "spec.md に 'Target:' 行がありません（対象のパス or GitHub URL を指定してください）"

info "Target: ${c_bold}$TARGET${c_reset}"

# ── 対象の解決（git URL ならクローン）──────────────────────────────
WORK_DIR=""
case "$TARGET" in
  http*://*|git@*:*.git)
    name="$(basename "$TARGET" .git)"
    WORK_DIR="$SCRIPT_DIR/.work/$name"
    if [ -d "$WORK_DIR/.git" ]; then
      log "既存クローンを更新: $WORK_DIR"
      git -C "$WORK_DIR" fetch -q --all && git -C "$WORK_DIR" reset -q --hard origin/HEAD 2>/dev/null || true
    else
      info "クローン中: $TARGET"
      mkdir -p "$SCRIPT_DIR/.work"
      git clone -q "$TARGET" "$WORK_DIR" || die "クローンに失敗: $TARGET"
    fi
    PROJECT_DIR="$WORK_DIR"
    ;;
  *)
    PROJECT_DIR="${TARGET/#\~/$HOME}"
    [ -d "$PROJECT_DIR" ] || die "対象ディレクトリが存在しません: $PROJECT_DIR"
    ;;
esac

# ── ゲートの自動判定（Build 未指定時）──────────────────────────────
if [ -z "$BUILD" ]; then
  if   [ -f "$PROJECT_DIR/Package.swift" ]; then BUILD="swift build"
  elif compgen -G "$PROJECT_DIR/*.xcodeproj" >/dev/null 2>&1 || [ -f "$PROJECT_DIR/project.yml" ]; then
    warn "Xcodeプロジェクトを検出。scheme/シミュレータが環境依存のため、spec.md に Build: 行で明示推奨。今回はゲート無しで実行します。"
    BUILD=""
  elif [ -f "$PROJECT_DIR/package.json" ]; then BUILD="npm test --silent"
  elif compgen -G "$PROJECT_DIR/*.py" >/dev/null 2>&1 || [ -f "$PROJECT_DIR/pyproject.toml" ]; then
    BUILD="python3 -m pytest -q 2>/dev/null || python3 -c 'import compileall,sys; sys.exit(0 if compileall.compile_dir(\".\",quiet=1) else 1)'"
  else
    warn "ゲートを自動判定できませんでした。ゲート無し（生成＋レビューのみ）で実行します。"
    BUILD=""
  fi
  [ -n "$BUILD" ] && log "自動判定ゲート: ${c_dim}$BUILD${c_reset}"
fi

# ── 一時設定を生成して review-loop.sh を起動 ───────────────────────
CFG="$(mktemp -t automate-config.XXXXXX.sh)"
trap 'rm -f "$CFG"' EXIT
{
  echo "PROJECT_DIR=\"$PROJECT_DIR\""
  echo "SPEC_FILE=\"$SPEC\""
  echo "BUILD_CMD=\"${BUILD//\"/\\\"}\""
  echo "MAX_ITERS=\"${MAX:-5}\""
  echo "CODER_MODEL=\"${CODER_MODEL:-sonnet}\""
  echo "REVIEWER_MODEL=\"${REVIEWER_MODEL:-opus}\""
} > "$CFG"

rule
exec "$SCRIPT_DIR/review-loop.sh" "$CFG"
