
import sys
import os
import numpy as np
import onnxruntime as ort
from PIL import Image

MODEL = "models/u2netp.onnx"

def remove_background(input_path):
    print("KING AI: Fotoğraf analiz ediliyor...")

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL

    session = ort.InferenceSession(
        MODEL,
        sess_options=options,
        providers=["CPUExecutionProvider"]
    )

    image = Image.open(input_path).convert("RGB")
    original_size = image.size

    resized = image.resize((320, 320), Image.Resampling.BILINEAR)
    array = np.asarray(resized, dtype=np.float32) / 255.0

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    array = (array - mean) / std
    array = np.transpose(array, (2, 0, 1))[None, ...]

    print("KING AI: Nesneler algılanıyor...")

    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: array})[0]

    mask = output[0, 0]
    mask = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)

    mask_image = Image.fromarray(
        np.uint8(mask * 255)
    ).resize(original_size, Image.Resampling.BILINEAR)

    result = Image.open(input_path).convert("RGBA")
    result.putalpha(mask_image)

    name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"static/edited/{name}_AI.png"

    result.save(output_path, "PNG")

    print("ISLEM TAMAMLANDI!")
    print("DOSYA:", output_path)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanim: python ai_engine.py FOTOĞRAF_YOLU")
        sys.exit(1)

    remove_background(sys.argv[1])

