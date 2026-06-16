#!/usr/bin/env bash
# setup.sh — 依存チェックと Claude Code CLI 導入案内。
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF'
setup.sh — auto-review-loop の準備

  ./setup.sh            依存チェック & Claude CLI の有無を確認
  ./setup.sh --help     このヘルプ

── スケジュール登録（完全放置で定期実行したい場合）────────────────
launchd の例 (毎日 2:00 に実行):

  ~/Library/LaunchAgents/com.user.autoreviewloop.plist を作成し、
  ProgramArguments に
    /bin/bash -lc 'cd <このフォルダ> && ./review-loop.sh myproject.config.sh'
  を指定して `launchctl load` する。

cron の例:
  crontab -e で次を追加（毎日 2:00）:
  0 2 * * * cd <このフォルダ> && /bin/bash ./review-loop.sh myproject.config.sh >> logs/cron.log 2>&1
EOF
  exit 0
fi

rule
info "依存チェック"
miss=0
for t in git python3; do
  if command -v "$t" >/dev/null 2>&1; then ok "$t: $(command -v $t)"; else err "$t: 見つかりません"; miss=1; fi
done
command -v jq >/dev/null 2>&1 && ok "jq: $(command -v jq)" || warn "jq: 任意（無くても動作）"
command -v xcodebuild >/dev/null 2>&1 && ok "xcodebuild: あり（Xcode/iOSプロジェクト用）" || warn "xcodebuild: なし（Xcode案件で使うなら必要）"

rule
info "Claude Code CLI"
if detect_claude; then
  ok "検出: $CLAUDE_BIN"
  "$CLAUDE_BIN" --version 2>/dev/null | sed 's/^/    /' || true
else
  warn "Claude Code CLI が見つかりません。ループ本番には必須です。"
  cat <<'EOF'

  導入方法（いずれか）:
    • 公式インストーラ:
        curl -fsSL https://claude.ai/install.sh | bash
    • npm（Node が必要）:
        npm install -g @anthropic-ai/claude-code

  導入後、認証のため一度だけ対話起動してログインしてください:
        claude

  ※ Node/npm が未導入の場合は Homebrew 等で先に入れてください:
        brew install node
EOF
fi

rule
info "次のステップ"
cat <<EOF
  1) spec.md を編集:  Target / Build / Max と目標を書く
  2) 実行:            ./run.sh
  （Claude には「Automate の spec.md 読んで」と言うだけで自動実行されます）
EOF
[ "$miss" = "0" ]
