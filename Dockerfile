# STEP 1: 我々がコントロールできる、クリーンな開発環境から始める
FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

# STEP 2: ベースイメージに含まれる不要な巨大ファイルを根こそぎ削除し、イメージを軽量化する
RUN rm -rf /workspace/* /root/.cache/*

# STEP 3: 必要なツールとComfyUI本体をインストールする
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git wget
WORKDIR /
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# STEP 4: ComfyUIと、我々が使うカスタムノードの全ての依存関係を、我々の手で確実にインストールする
WORKDIR /ComfyUI
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "numpy<2.0" opencv-python scikit-image

# STEP 5: カスタムノードをインストールする
WORKDIR /ComfyUI/custom_nodes
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
RUN git clone https://github.com/rgthree/rgthree-comfy.git
# ... ここに、今後追加したいノードを追記していく ...

# STEP 6: ComfyUIがモデルを探す場所を、Network Volumeへの入り口に差し替える
# これにより、モデルはイメージに含まれず、起動が高速になる
RUN rm -rf /ComfyUI/models && \
    ln -s /runpod-volume /ComfyUI/models

# STEP 7: 我々が作った、確実に動作する起動スクリプトとハンドラを配置する
WORKDIR /
COPY simple_handler.py .
COPY start.sh . 
RUN pip install --no-cache-dir aiohttp runpod requests websocket-client

# STEP 8: 起動コマンドを設定する
RUN chmod +x /start.sh
CMD ["/start.sh"]