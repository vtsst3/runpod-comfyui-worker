# 動作実績のあるコミュニティテンプレートをベースにする
FROM runpod/worker-comfyui:5.1.0-sdxl

# --- ▼▼▼ カスタムノードの追加 ▼▼▼ ---

# ComfyUIのカスタムノードディレクトリに移動する
WORKDIR /app/ComfyUI/custom_nodes

# 全てのインストール作業を一つのRUN命令にまとめる。
# 'set -e' を使うことで、シェルスクリプトの途中でコマンドが失敗したら、即座にスクリプト全体がエラーで停止する。
# これにより、Dockerビルドも確実に失敗し、問題を見逃すことがなくなる。
# apt-getもより安定した書き方に修正。
RUN set -e && \
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

# ベースイメージの作業ディレクトリに戻しておく
WORKDIR /