# 動作実績のあるコミュニティテンプレートをベースにする
FROM runpod/worker-comfyui:5.1.0-sdxl

# --- ▼▼▼ ここに、我々が追加したいカスタムノードだけを記述する ▼▼▼ ---

# ComfyUIのカスタムノードディレクトリに移動する
# (このテンプレートでは /app/ComfyUI にインストールされています)
WORKDIR /app/ComfyUI/custom_nodes

# Impact Packを追加 (テンプレートに含まれていない場合)
RUN git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git && \
    pip install --no-cache-dir -r ComfyUI-Impact-Pack/requirements.txt

# rgthree-comfy を追加
RUN git clone https://github.com/rgthree/rgthree-comfy.git

# ... 他に追加したいノードがあれば、ここに `RUN git clone ...` を追記 ...
# 例: RUN git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git && \
#        pip install --no-cache-dir -r ComfyUI-AnimateDiff-Evolved/requirements.txt


# --- ▲▲▲ カスタマイズはここまで ▲▲▲ ---

# 起動スクリプトやハンドラはベースイメージのものをそのまま使うので、
# これ以上何も記述する必要はありません。