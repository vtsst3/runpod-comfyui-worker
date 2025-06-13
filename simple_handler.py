import runpod
import asyncio
import json
import aiohttp
import uuid

# コンテナ内で動いているComfyUIのアドレス
COMFYUI_ADDR = "127.0.0.1:8188"

# WebSocket経由でComfyUIにワークフローを送信し、結果を待つ非同期関数
async def send_workflow_to_comfyui(workflow):
    # ユニークなプロンプトIDを生成
    prompt_id = str(uuid.uuid4())
    
    # ComfyUIに送信するデータを作成
    prompt_data = {"prompt": workflow, "client_id": "runpod_client", "prompt_id": prompt_id}

    # aiohttpセッションを開始
    async with aiohttp.ClientSession() as session:
        # ComfyUIのWebSocketエンドポイントに接続
        # clientIdは任意だが、デバッグのために設定しておくと便利
        async with session.ws_connect(f"ws://{COMFYUI_ADDR}/ws?clientId=runpod_client") as ws:
            
            # 作成したプロンプトデータをJSON形式で送信
            await ws.send_str(json.dumps(prompt_data))
            
            # ComfyUIからのメッセージを待ち受けるループ
            while True:
                msg = await ws.receive()
                
                # テキストメッセージの場合
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    
                    # 自分の投げたプロンプトが完了したことを示すメッセージかチェック
                    if data.get("type") == "executed" and data.get("data", {}).get("prompt_id") == prompt_id:
                        # 完了した場合、出力データ（画像情報など）を返す
                        return data.get("data", {}).get("output", {})
                
                # WebSocketが閉じたか、エラーが発生した場合はループを抜ける
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    break

    # WebSocket接続に失敗した場合や、結果が返ってこなかった場合
    return {"error": "Failed to get result from ComfyUI via WebSocket"}

# RunPodがジョブを受け取ったときに呼び出すメインのハンドラ関数
async def handler(job):
    # ジョブの入力データを取得
    job_input = job.get("input", {})
    
    # 入力データからワークフローを取得
    workflow = job_input.get("workflow")
    
    # ワークフローがない場合はエラーを返す
    if not workflow:
        return {"error": "Workflow is missing from the job input."}
    
    try:
        # ComfyUIにワークフローを送信し、結果を取得
        result = await send_workflow_to_comfyui(workflow)
        # 取得した結果をRunPodに返す
        return result
    except Exception as e:
        # 途中で何らかの例外が発生した場合、エラーメッセージを返す
        print(f"An error occurred: {e}")
        return {"error": str(e)}

# RunPodのサーバーレスフレームワークを開始する
# `handler`関数を非同期で実行するように設定
runpod.serverless.start({
    "handler": handler,
    "concurrency_modifier": lambda x: 1 # 同時に処理するジョブは1つに制限
})