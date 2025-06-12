# 動作実績のあるコミュニティテンプレートをベースにする
FROM runpod/worker-comfyui:5.1.0-sdxl

# --- ▼▼▼【重要】キャッシュバスティングのためのARG命令▼▼▼ ---
# ビルド時に毎回変わる値をARGとして定義する。
# これにより、このARGに依存するRUN命令はキャッシュが使われなくなる。
ARG CACHE_BUSTER=none
# --- ▲▲▲ここまで▲▲▲ ---

# --- ▼▼▼ カスタムノードの追加 ▼▼▼ ---

WORKDIR /app/ComfyUI/custom_nodes

RUN set -e && \
    # 上で定義したARGをENVとして設定。この行があることで、RUN命令がCACHE_BUSTERに依存するようになる。
    echo "Cache Buster: ${CACHE_BUSTER}" && \
    apt-get -y -qq update && \
    apt-get -y -qq install git && \
    \
    echo "--- Starting custom node installation ---" && \
    \
    echo "Cloning Impact Pack..." && \
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    pip install --no-cache-dir -r ComfyUI-Impact-Pack/requirements.txt && \
    \
    echo "Cloning rgthree-comfy..." && \
    git clone https://github.com/rgthree/rgthree-comfy.git && \
    \
    echo "--- Installation finished. Verifying directory contents: ---" && \
    ls -l && \
    \
    echo "--- Custom node setup complete. ---"

# --- ▲▲▲ カスタマイズはここまで ▲▲▲ ---

WORKDIR /