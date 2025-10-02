# OOP wrappers showing multiple inheritance, decorators, encapsulation, polymorphism, overriding
import functools, time, os
from abc import ABC, abstractmethod
from transformers import pipeline
from PIL import Image
import torch


def get_device_for_transformers():
    # Prefer CPU on non-CUDA machines
    return -1 if not torch.cuda.is_available() else 0


def timing(func):
    @functools.wraps(func)
    def wrapper(*a, **kw):
        t0 = time.time()
        result = func(*a, **kw)
        elapsed = time.time() - t0
        try:
            a[0]._last_time = elapsed
        except Exception:
            pass
        return result
    return wrapper


def simple_cache(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*a, **kw):
        key = (func.__name__, str(a[1]) if len(a) > 1 else None, tuple(sorted(kw.items())))
        if key in cache:
            return cache[key]
        res = func(*a, **kw)
        cache[key] = res
        return res

    return wrapper


class LoggingMixin:
    def log(self, msg):
        print("[LOG]", msg)


class PreprocessMixin:
    def pil_to_rgb(self, pil_image):
        return pil_image.convert("RGB")


class BaseModelWrapper(ABC, LoggingMixin):
    def __init__(self, model_name):
        self._model_name = model_name  # encapsulated
        self._pipeline = None
        self._loaded = False
        self._last_time = None

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def process(self, data):
        pass

    def info(self):
        return {
            "model_name": self._model_name,
            "loaded": self._loaded,
            "last_time": self._last_time,
        }


class ImageCaptionWrapper(BaseModelWrapper, PreprocessMixin):
    def __init__(self, model_name="nlpconnect/vit-gpt2-image-captioning"):
        super().__init__(model_name)
        self._device = get_device_for_transformers()

    def load(self):
        if self._loaded:
            return
        self.log(f"Loading image model {self._model_name} (may download weights)...")
        self._pipeline = pipeline("image-to-text", model=self._model_name, device=self._device)
        self._loaded = True

    @timing
    @simple_cache
    def process(self, image_input):
        if not self._loaded:
            self.load()
        if isinstance(image_input, str):
            pil = Image.open(image_input)
        else:
            pil = image_input
        pil = self.pil_to_rgb(pil)
        out = self._pipeline(pil)
        return out


class SentimentWrapper(BaseModelWrapper):
    def __init__(self, model_name="tabularisai/multilingual-sentiment-analysis"):
        super().__init__(model_name)
        self._device = get_device_for_transformers()

    def load(self):
        if self._loaded:
            return
        self.log(f"Loading text model {self._model_name} ...")
        self._pipeline = pipeline("text-classification", model=self._model_name, device=self._device)
        self._loaded = True

    @timing
    def process(self, text):
        if not self._loaded:
            self.load()
        return self._pipeline(text)
