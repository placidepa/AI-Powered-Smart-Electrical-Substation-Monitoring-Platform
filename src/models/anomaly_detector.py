import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout
from sklearn.ensemble import IsolationForest

class SubstationAutoencoder(Model):
    '''
    Deep Learning Autoencoder for unsupervised anomaly detection.
    Minimizes Reconstruction Error: L(x, x_hat) = ||x - x_hat||^2
    '''
    def __init__(self, input_dim):
        super(SubstationAutoencoder, self).__init__()
        self.encoder = tf.keras.Sequential([
            Dense(32, activation='relu'),
            Dropout(0.1),
            Dense(16, activation='relu'),
            Dense(8, activation='relu')
        ])
        self.decoder = tf.keras.Sequential([
            Dense(16, activation='relu'),
            Dense(32, activation='relu'),
            Dense(input_dim, activation='linear')
        ])

    def call(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def get_reconstruction_error(self, x):
        reconstructions = self.predict(x)
        mse = np.mean(np.power(x - reconstructions, 2), axis=1)
        return mse

class IsolationForestDetector:
    '''Tree-based fallback for baseline comparisons.'''
    def __init__(self, contamination=0.02):
        self.model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
        
    def fit(self, X):
        self.model.fit(X)
        
    def predict(self, X):
        preds = self.model.predict(X)
        return np.where(preds == -1, 1, 0)