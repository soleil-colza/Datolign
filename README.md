# Datolign

## 概要

Datolign（デイトライン）は、同一サーバー内のユーザー間での日程調整をお手軽にするDiscordボットです。
外部サイトなどに依存することなくすべての機能がDiscord上で完結します。
コマンドを一切使用することなく、コンピューターに不慣れなユーザーも直感的に利用できます。
類似サービスと比較しても、親しみやすい言葉遣いやGUIを採用していることが特異な点です。

## 機能

- Googleカレンダーからイベントを取得
- ユーザーの入力に基づいて空き時間を計算
- 検索から特定の時間帯（23:00-08:00)を除外
- 検索の開始日と終了日の指定
- 空き時間の間隔の指定
- 表示する空き時間の数の指定
- リアクションを利用したBOTとユーザー間のインタラクション

## 使い方

1. Datolignを導入し、サーバー内でメンションします（例： @Datolign）。すると、Datolignは以下を指定するように求めます：
    - 検索の開始日時（例：2023-08-01 12:00）
    - 検索の終了日時（例：2023-08-03 12:00）
    - 検索から除外する開始時間（例：00:00）
    - 検索から除外する終了時間（例：09:00）
    - 空き時間の間隔（分）（例：60）
    - 表示する空き時間の数（例：5）

2. ボットはその後、空き時間を計算し、チャットに表示します。各空き時間は別々のメッセージとして表示されます。

3. 以下の絵文字で空き時間のメッセージにリアクションできます：
    - 🎉：第1希望
    - 👍：第2希望
    - 👀：第３希望
   各絵文字には重さの差をつけているため、全員の希望に最も合致する日程を抽出することが可能になりました。

## 環境要件

- Python 3.6以上
- discord.pyライブラリ
- GoogleカレンダーAPI用のgoogle-auth、google-auth-oauthlib、google-auth-httplib2、google-api-python-clientライブラリ
- GoogleカレンダーAPIが有効になっているGoogleアカウント
- Discordのボットトークン

## セットアップ

1. リポジトリをクローンし、必要なPythonライブラリをインストール

2. GoogleアカウントのGoogleカレンダーAPIを有効にし、`token.json`ファイルをダウンロード

3. Discordのボットを作成し、ボットトークンを取得

4. ボットトークンを`TOKEN`という名前の環境変数として設定

5. ボットのスクリプトを実行

## 注意

このボットはJST（日本標準時）のタイムゾーンを使用しています。そのため別のタイムゾーンを使用したい場合は、スクリプトのタイムゾーンを変更する必要があります。
