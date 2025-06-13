import requests
import time
import json
import base64

# --- ここを自分の情報に書き換えてください ---
RUNPOD_API_KEY = "YOUR_API_KEY"
ENDPOINT_ID = "6m16h30cxqgonp"
# -----------------------------------------

workflow = {
  # (ワークフローJSONは前回と同じなので省略)
  "3": {
    "inputs": {
      "seed": [
        "12",
        0
      ],
      "steps": 25,
      "cfg": 5,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "model": [
        "4",
        0
      ],
      "positive": [
        "6",
        0
      ],
      "negative": [
        "7",
        0
      ],
      "latent_image": [
        "5",
        0
      ]
    },
    "class_type": "KSampler",
    "_meta": {
      "title": "Kサンプラー"
    }
  },
  "4": {
    "inputs": {
      "ckpt_name": "HarmoniqMix_vPred_v3_SPO.safetensors"
    },
    "class_type": "CheckpointLoaderSimple",
    "_meta": {
      "title": "チェックポイントを読み込む"
    }
  },
  "5": {
    "inputs": {
      "width": 1024,
      "height": 1024,
      "batch_size": 1
    },
    "class_type": "EmptyLatentImage",
    "_meta": {
      "title": "空の潜在画像"
    }
  },
  "6": {
    "inputs": {
      "text": "1girl, angry, short_hair, lips, ",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIPテキストエンコード（プロンプト）"
    }
  },
  "7": {
    "inputs": {
      "text": "nose, nostrils, realistic, ",
      "clip": [
        "4",
        1
      ]
    },
    "class_type": "CLIPTextEncode",
    "_meta": {
      "title": "CLIPテキストエンコード（プロンプト）"
    }
  },
  "8": {
    "inputs": {
      "samples": [
        "3",
        0
      ],
      "vae": [
        "4",
        2
      ]
    },
    "class_type": "VAEDecode",
    "_meta": {
      "title": "VAEデコード"
    }
  },
  "11": {
    "inputs": {
      "images": [
        "8",
        0
      ]
    },
    "class_type": "PreviewImage",
    "_meta": {
      "title": "Preview Image"
    }
  },
  "12": {
    "inputs": {
      "seed": -1
    },
    "class_type": "Seed (rgthree)",
    "_meta": {
      "title": "Seed (rgthree)"
    }
  }
}


payload = { "input": { "workflow": workflow } }
headers = { "Authorization": f"Bearer {RUNPOD_API_KEY}" }

# 1. 非同期でジョブを投入 (/run)
run_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/run"
print("Submitting job...")
response = requests.post(run_url, headers=headers, json=payload)

if response.status_code != 200:
    print(f"Failed to submit job: {response.text}")
    exit()

job_data = response.json()
job_id = job_data.get("id")
print(f"Job submitted successfully. Job ID: {job_id}")

# 2. ステータスをポーリングして完了を待つ
status_url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/status/{job_id}"
print("Waiting for job to complete...")

while True:
    status_response = requests.get(status_url, headers=headers)
    status_data = status_response.json()
    status = status_data.get("status")
    
    print(f"Current status: {status}")

    if status == "COMPLETED":
        print("\n--- JOB COMPLETED ---")
        output = status_data.get("output", {})
        if "images" in output:
            for i, img_info in enumerate(output["images"]):
                if img_info.get("type") == "base64":
                    img_b64 = img_info.get("data")
                    img_bytes = base64.b64decode(img_b64)
                    filename = f"output_{job_id}_{i}.png"
                    with open(filename, "wb") as f:
                        f.write(img_bytes)
                    print(f"SUCCESS: Image saved as {filename}")
        else:
            print("Job completed, but no images found in output.")
            print(f"Full output: {json.dumps(output, indent=2)}")
        break
    elif status in ["FAILED", "CANCELLED"]:
        print(f"\n--- JOB FAILED ---")
        print(json.dumps(status_data, indent=2))
        break
    
    # 5秒待機して再確認
    time.sleep(5)