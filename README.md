# Automate

**spec.md に「目標」と「対象」を書いて、Claude に「spec.md 読んで」と言うだけ**で、
コード生成 → ビルド/テスト → レビュー → 修正 を人手なしで自動反復するツール。

```
spec.md(目標+対象)
   │
   ▼
 ① コーダーClaude がコードを書く
   ▼
 ② ビルド/テストゲート（失敗→エラーを差し戻して①へ）
   ▼
 ③ レビューClaude が diff を審査（APPROVED / CHANGES_REQUESTED）
   ▼
 ④ 承認 or 反復上限で停止
```

## 使い方（普段）

1. `spec.md` を編集して目標と対象を書く:
   ```
   Target: /path/to/project   ← または https://github.com/you/repo.git
   Build:  <ゲートコマンド>     ← 省略時は自動判定
   Max:    5

   ## 目標
   〇〇を実装/修正する …
   ```
2. Claude に **「Automate の spec.md 読んで」** と言う。あとは自動。

## 手動で回す場合

```bash
./setup.sh        # 初回: 依存チェック & claude CLI ログイン確認
./run.sh          # spec.md を読んでループ実行
./run.sh other.md # 別の spec ファイルを指定することも可
```

## 構成

| ファイル | 役割 |
|---|---|
| `spec.md` | 目標と対象を書く入口（ユーザーが編集） |
| `run.sh` | spec.md を解析し対象を解決してループ起動 |
| `review-loop.sh` | コード生成→ゲート→レビューの反復本体 |
| `prompts/` | コーダー / レビュアーのシステムプロンプト |
| `lib/common.sh` | 共通処理（CLI検出・Claude呼び出し・判定解析） |
| `CLAUDE.md` | 「読んで」と言われた時のエージェント手順 |
| `logs/` | 実行ログ（diff・ビルド・レビュー） |

## 前提
- `claude`（Claude Code CLI）にログイン済みであること（`./setup.sh` で確認）。
- ゲートに使うツール（xcodebuild / pytest / npm 等）が対象に応じて利用可能なこと。

## 動作確認（CLI不要）
```bash
DRY_RUN=1 ./run.sh    # Target をローカルの小さなプロジェクトにして配線確認
```
