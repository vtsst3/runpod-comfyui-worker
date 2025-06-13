#!/bin/bash

# ComfyUIをバックグラウンドで起動
# --listen オプションで、コンテナ外からのアクセスを許可する
# --port 8188 でポートを指定
python -u /ComfyUI/main.py --listen --port 8188 &

# ComfyUIが起動してリクエストを受け付ける準備ができるまで待機する
echo "Waiting for ComfyUI to start..."

# 最大5分（300秒）待つ。それ以上かかったら異常と判断して終了する
timeout 300 bash -c '
# ComfyUIのAPIエンドポイントにアクセスできるか、1秒ごとにチェックし続ける
# curl -s でサイレントモード、-f でエラー時に失敗ステータスを返す
until curl -s -f http://127.0.0.1:8188/history/1 > /dev/null; do
    echo -n "."
    sleep 1
done'

# 待機ループがタイムアウトで終了したかチェック
if [ $? -ne 0 ]; then
    echo "ComfyUI failed to start within 300 seconds. Exiting."
    # 失敗したことを示すステータスコードで終了
    exit 1
fi

# ComfyUIが無事に起動したことをログに出力
echo "ComfyUI started successfully."

# 最後に、RunPodのハンドラースクリプトをフォアグラウンドで実行する
# exec を使うことで、このスクリプトのプロセスがhandlerのプロセスに置き換わる
exec python -u /simple_handler.py