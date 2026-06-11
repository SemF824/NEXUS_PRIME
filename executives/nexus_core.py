# nexus_core.py
import torch
from sklearn.base import BaseEstimator, TransformerMixin
from sentence_transformers import SentenceTransformer

class TextEncoder(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='paraphrase-multilingual-mpnet-base-v2'):
        self.model_name = model_name
        self._encoder = None

    def fit(self, X, y=None):
        self._get_encoder()
        return self

    def transform(self, X):
        encoder = self._get_encoder()
        return encoder.encode(list(X), show_progress_bar=False, batch_size=64)

    def _get_encoder(self):
        if not hasattr(self, '_encoder') or self._encoder is None:
            # Détection automatique et allocation sur la puce NVIDIA L4
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"⚙️ Allocation de l'encodeur sémantique sur le périphérique : {device.upper()}")
            self._encoder = SentenceTransformer(self.model_name, device=device)
        return self._encoder

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_encoder'] = None
        return state