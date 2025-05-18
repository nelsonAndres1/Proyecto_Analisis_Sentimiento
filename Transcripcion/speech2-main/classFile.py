import re
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
import nltk
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

jerga_dict_es = {
    "pa'": "para",
    "pana": "amigo"
}

class ReemplazarJergas(BaseEstimator, TransformerMixin):
    def __init__(self, diccionario=jerga_dict_es):
        self.diccionario = diccionario

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self._reemplazar(texto) for texto in X]

    def _reemplazar(self, texto):
        palabras = texto.split()
        palabras_reemplazadas = [self.diccionario.get(p, p) for p in palabras]
        return ' '.join(palabras_reemplazadas)

class LimpiarTexto(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [self._limpiar(texto) for texto in X]

    def _limpiar(self, texto):
        texto = texto.lower()
        texto = self._quitar_acentos(texto)  # Quitar acentos
        texto = re.sub(r'[^a-zñ\s]', '', texto)  # Eliminar caracteres especiales y números
        texto = re.sub(r'\s+', ' ', texto).strip()  # Eliminar espacios extra
        return texto

    def _quitar_acentos(self, texto):
        # Diccionario de reemplazo de acentos
        acentos_dict = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        # Reemplazar los caracteres acentuados
        for acentuada, sin_acento in acentos_dict.items():
            texto = texto.replace(acentuada, sin_acento)
        return texto

class TokenizarYLematizar(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('spanish'))  # Cambiar a español

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [' '.join(self._tokenizar_lemmatizar(texto)) for texto in X]

    def _tokenizar_lemmatizar(self, texto):
        tokens = word_tokenize(texto)
        tokens = [word for word in tokens if word not in self.stop_words]  # Eliminar stopwords
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]  # Lematización
        return tokens

class Word2VecTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, vector_size=100, window=5, min_count=1):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.model = None

    def fit(self, X, y=None):
        # Tokenizamos el texto para entrenar el modelo Word2Vec
        tokenized_texts = [texto.split() for texto in X]
        self.model = Word2Vec(sentences=tokenized_texts, vector_size=self.vector_size, window=self.window, min_count=self.min_count, workers=4)
        return self

    def transform(self, X):
        # Convertimos cada texto en un vector promedio
        tokenized_texts = [texto.split() for texto in X]
        vectors = []
        for tokens in tokenized_texts:
            if not tokens:  # Manejar textos vacíos
                vectors.append(np.zeros(self.vector_size))
            else:
                vec = np.mean([self.model.wv[token] for token in tokens if token in self.model.wv], axis=0)
                vectors.append(vec)
        return np.array(vectors)
