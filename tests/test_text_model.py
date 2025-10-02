# tests/test_text_model.py
from transformers import pipeline


def test_text_pipeline_run():
    nlp = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis", device=-1)
    out = nlp("I love this product!")
    assert isinstance(out, list) and len(out) > 0
