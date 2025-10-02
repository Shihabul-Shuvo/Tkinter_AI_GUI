# tests/test_image_model.py
from transformers import pipeline
from PIL import Image


def test_image_pipeline_run():
    # Create a tiny white image in-memory
    img = Image.new("RGB", (64, 64), color=(255, 255, 255))
    cap = pipeline("image-to-text", model="nlpconnect/vit-gpt2-image-captioning", device=-1)
    out = cap(img)
    assert isinstance(out, list) and len(out) > 0
