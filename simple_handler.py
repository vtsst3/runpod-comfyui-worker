import runpod
import asyncio
import json
import aiohttp
import uuid
import base64
from urllib.parse import urlencode

# コンテナ内で動いているComfyUIのアドレス
COMFYUI_ADDR = "127.0.0.1:8188"
CLIENT_ID = str(uuid.uuid4())

async def get_image_data(session, filename, subfolder, folder_type):
    """ComfyUIの/viewエンドポイントから画像データを取得する"""
    params = urlencode({'filename': filename, 'subfolder': subfolder, 'type': folder_type})
    async with session.get(f"http://{COMFYUI_ADDR}/view?{params}") as response:
        if response.status == 200:
            return await response.read()
    return None

async def get_history(session, prompt_id):
    """特定のprompt_idの実行結果を取得する"""
    async with session.get(f"http://{COMFYUI_ADDR}/history/{prompt_id}") as response:
        if response.status == 200:
            return await response.json()
    return {}

async def send_workflow_to_comfyui(workflow):
    """WebSocket経由でワークフローを送信し、結果の画像を取得する"""
    prompt_id = str(uuid.uuid4())
    prompt_data = {"prompt": workflow, "client_id": CLIENT_ID, "prompt_id": prompt_id}
    
    final_output = {"images": []}

    async with aiohttp.ClientSession() as session:
        # WebSocketに接続
        async with session.ws_connect(f"ws://{COMFYUI_ADDR}/ws?clientId={CLIENT_ID}") as ws:
            # ワークフローを送信
            await ws.send_str(json.dumps(prompt_data))

            # 完了メッセージを待つ
            while True:
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    # 自分の投げたプロンプトが完了したかチェック
                    if data.get("type") == "executed" and data.get("data", {}).get("prompt_id") == prompt_id:
                        break # ループを抜けて画像取得処理へ
                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                    return {"error": "WebSocket connection failed during execution."}

        # ワークフロー完了後、/historyエンドポイントから出力情報を取得
        history = await get_history(session, prompt_id)
        history_data = history.get(prompt_id, {})
        outputs = history_data.get("outputs", {})

        # 出力ノードをループして画像を探す
        for node_id, node_output in outputs.items():
            if 'images' in node_output:
                for image_info in node_output['images']:
                    if image_info.get("type") == "temp": # PreviewImageはtempタイプで出力する
                        # 画像データを取得
                        image_bytes = await get_image_data(
                            session, 
                            image_info['filename'], 
                            image_info['subfolder'], 
                            image_info['type']
                        )
                        if image_bytes:
                            # Base64にエンコードして最終結果に追加
                            img_b64 = base64.b64encode(image_bytes).decode('utf-8')
                            final_output["images"].append({
                                "type": "base64",
                                "data": img_b64
                            })

    if not final_output["images"]:
        return {"error": "Job completed, but no images were generated or retrieved.", "details": history}

    return final_output

async def handler(job):
    job_input = job.get("input", {})
    workflow = job_input.get("workflow")

    if not workflow:
        return {"error": "Workflow is missing from the job input."}

    try:
        result = await send_workflow_to_comfyui(workflow)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

runpod.serverless.start({
    "handler": handler,
    "concurrency_modifier": lambda x: 1
})