import threading
from app.models.hf_wrapper import ImageCaptionWrapper, SentimentWrapper


class ModelController:
    def __init__(self):
        self.image_wrapper = ImageCaptionWrapper()
        self.sentiment_wrapper = SentimentWrapper()

    def run_image_caption(self, image_input, callback):
        def worker():
            try:
                res = self.image_wrapper.process(image_input)
                callback(None, res)
            except Exception as e:
                callback(e, None)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def run_sentiment(self, text, callback):
        def worker():
            try:
                res = self.sentiment_wrapper.process(text)
                callback(None, res)
            except Exception as e:
                callback(e, None)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
