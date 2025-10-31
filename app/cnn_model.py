import io
import json
from typing import List, Tuple, Optional
import numpy as np
from PIL import Image
import tensorflow as tf

IMAGE_SIZE: Tuple[int, int] = (224, 224)

class RandomInvert(tf.keras.layers.Layer):
    def __init__(self, p=0.5, **kwargs):
        super().__init__(**kwargs)
        self.p = p

    def call(self, x, training=None):
        training = tf.constant(False) if training is None else tf.cast(training, tf.bool)

        def do_aug():
            batch = tf.shape(x)[0]
            mask = tf.random.uniform([batch, 1, 1, 1]) < self.p
            return tf.where(mask, 1.0 - x, x)

        return tf.cond(training, do_aug, lambda: x)

    def get_config(self):
        config = super().get_config()
        config.update({"p": self.p})
        return config

class SignModel:
    def __init__(self, model_path: str, classes_path: Optional[str] = None):
        self.model = tf.keras.models.load_model(
            model_path,
            custom_objects={"RandomInvert": RandomInvert}
        )
        if classes_path:
            with open(classes_path, "r") as f:
                self.class_names: List[str] = json.load(f)
        else:
            num = self.model.output_shape[-1]
            self.class_names = [str(i) for i in range(num)]

        @tf.function
        def _infer(x):
            return self.model(x, training=False)
        self._infer = _infer

    def _preprocess(self, img: Image.Image) -> tf.Tensor:
        img = img.convert("RGB").resize(IMAGE_SIZE, Image.BILINEAR)
        arr = np.asarray(img, dtype=np.uint8)

        arr = np.expand_dims(arr, axis=0)
        return tf.convert_to_tensor(arr)

    def predict_from_bytes(self, image_bytes: bytes, topk: int = 3):
        img = Image.open(io.BytesIO(image_bytes))
        x = self._preprocess(img)
        preds = self._infer(x).numpy()[0]
        top_indices = preds.argsort()[-topk:][::-1]
        top = [
            {"class": self.class_names[i], "score": float(preds[i])}
            for i in top_indices
        ]
        return {
            "top1": top[0],
            "topk": top,
            "all": preds.tolist(),
        }
