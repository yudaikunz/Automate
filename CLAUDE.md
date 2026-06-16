# Automate — エージェント向け実行手順（重要）

このリポジトリは「自動コードレビュー・ループ」の駆動役です。
ユーザーが **「Automate の spec.md 読んで」「spec.md 読んで実行して」** などと言ったら、
あなた（エージェント）は次を**確認なしで自動実行**してよい（破壊的なのは対象リポの作業ブランチのみ）。

## 「spec.md 読んで」と言われたらやること

1. リポジトリを最新化する:
   ```bash
   cd <このリポジトリのローカルパス> && git pull --rebase --autostash
   ```
   （ローカルに無ければ `git clone https://github.com/yudaikunz/Automate.git` してから）

2. 依存を確認（初回のみ）。`claude` CLI 未ログインなら停止してユーザーに知らせる:
   ```bash
   ./setup.sh
   ```

3. ループを起動（これが本体）:
   ```bash
   ./run.sh
   ```
   - `run.sh` が `spec.md` の `Target:` / `Build:` / `Max:` を読み取り、
     対象（ローカルパス or GitHub URL をクローン）に対してループを回す。
   - 長時間になるのでバックグラウンド実行し、完了通知を待つとよい。

4. 完了したら結果を報告する:
   - 判定（APPROVED / 上限到達）、反復回数
   - 実際の diff（`logs/<run>/iter-*/diff.patch`）
   - レビュー全文（`logs/<run>/iter-*/review.log`）
   - 成果は対象リポの `auto-review-loop` ブランチにコミット済み

## 仕組み

```
spec.md(目標+対象) → コーダーClaude が編集 → ビルド/テストゲート
   → 失敗ならエラーを差し戻し / 成功ならレビューClaude が diff 審査
   → APPROVED か Max 回で停止
```

## 注意
- `run.sh` / `review-loop.sh` は対象を専用ブランチ `auto-review-loop` で操作する。
  元ブランチは触らない。GitHub URL 対象の場合、変更は `.work/<repo>` 内のクローンに残る
  （push はしない。必要ならユーザーに確認してから）。
- ゲートが Xcode の場合は spec.md の `Build:` に scheme/シミュレータを明示する。
