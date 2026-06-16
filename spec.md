# 目標：（ここにやりたいことのタイトル）

<!--
このファイルに「目標」と「対象」を書いて保存し、Claudeに「Automateのspec.md読んで」
と言うだけで自動でループ（コード生成→ビルド→レビュー）が回ります。

先頭のメタ行（必須/任意）:
  Target: 対象コードの場所。ローカル絶対パス または GitHub URL。【必須】
  Build:  ビルド/テストのゲートコマンド（成功=exit 0）。省略可（自動判定）。
  Max:    反復上限。省略時 5。
メタ行より下の本文が「目標」としてコーダーに渡ります。
-->

Target: /Users/yudai/Documents/Claude/Projects/iOS写真整理アプリ開発/PhotoCurator
Build: /Users/yudai/.local/xcodegen/bin/xcodegen generate && xcodebuild -project PhotoCurator.xcodeproj -scheme PhotoCurator -destination 'platform=iOS Simulator,name=iPhone 17' build
Max: 5

## 目標

（例）各グループで「残す1枚」をユーザーが選んだら、それが一覧の一括削除にも
反映されるようにする。誤って残したい写真が削除されないこと。

## 受け入れ条件

- ゲート（Build）が成功すること。
- レビュアーが正しさ・退行・安全性の観点で承認（VERDICT: APPROVED）すること。

## 制約

- 変更は最小・焦点を絞る。無関係なリファクタや整形はしない。
- ビルド/テスト設定を目的のために緩めない。
