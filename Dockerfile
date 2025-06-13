# STEP 1: クリーンな開発環境から始める
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# STEP 2: 不要な巨大ファイルを削除
RUN rm -rf /workspace/* /root/.cache/*

# STEP 3: ツールとComfyUI本体をインストール
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git wget
WORKDIR /
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# STEP 4: ComfyUIのPythonを使って、全ての依存関係をインストールする
# これが最も重要で、確実な方法
WORKDIR /ComfyUI
# まずComfyUI自身のrequirements.txtを、ComfyUIのPythonでインストール
RUN python3 -m pip install --no-cache-dir -r requirements.txt
# 次に、我々が必要とする全ての追加ライブラリを、ComfyUIのPythonでインストール
RUN python3 -m pip install --no-cache-dir \
    "numpy<2.0" \
    "opencv-python-headless" \
    "scikit-image" \
    "piexif" \
    "segment-anything" \
    "transformers" \
    "scipy>=1.11.4" \
    "dill" \
    "matplotlib"

# STEP 5: カスタムノードをインストール
WORKDIR /ComfyUI/custom_nodes
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
RUN git clone https://github.com/rgthree/rgthree-comfy.git

# STEP 6: Network VolumeをComfyUIに認識させる
RUN rm -rf /ComfyUI/models && \
    ln -s /workspace/models /ComfyUI/models

# STEP 7: 我々の起動スクリプトとハンドラを配置
WORKDIR /
COPY simple_handler.py .
COPY start.sh . 
RUN python3 -m pip install --no-cache-dir aiohttp runpod requests websocket-client

# STEP 8: 起動コマンドを設定
RUN chmod +x /start.sh
CMD ["/start.sh"]