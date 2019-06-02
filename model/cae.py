import os
import numpy as np
import yaml

from keras.models import Sequential, Model
from keras.layers import Input, Dense, Flatten, Reshape, InputLayer
from keras.layers import MaxPooling2D, UpSampling2D, Conv2D, Conv2DTranspose
from keras.callbacks import BaseLogger

class CAE:

    def __init__(self, input_shape=(128,128,3), latent_features=512, 
                 filters=[8, 16, 32], kernel=(3,3), stride=1, pool=(2,2), 
                 optimizer="adamax", lossfn="mse", path=None, load=False):
        
        self.path = path if path else os.getcwd()
        
        if load:
            self._load()
        else:
            self.input_shape = input_shape
            self.latent_features = latent_features
            self.filters = filters
            self.kernel = kernel
            self.stride = stride
            self.pool = pool
            self.optimizer = optimizer
            self.lossfn = lossfn
            self._compile()
        
    def _compile(self):
        
        # define encoder architecture
        self.encoder = Sequential()
        self.encoder.add(InputLayer(self.input_shape))  
        
        conv_shape = self.input_shape
        for filt in self.filters:
            self.encoder.add(Conv2D(filters=filt, kernel_size=self.kernel, 
                                    strides=self.stride, activation='relu', padding='same'))
            self.encoder.add(MaxPooling2D(pool_size=self.pool))
            conv_shape = (int(conv_shape[0]/self.pool[0]), int(conv_shape[1]/self.pool[1]), filt)
        
        # Fully conected layer
        if self.latent_features:
            self.encoder.add(Flatten())
            self.encoder.add(Dense(self.latent_features, activation='relu'))
        
        # define decoder architecture
        self.decoder = Sequential()
        
        if self.latent_features:
            self.decoder.add(InputLayer((self.latent_features,)))
            self.decoder.add(Dense(np.prod(conv_shape), activation='relu'))
            self.decoder.add(Reshape(conv_shape))
        else:
            self.decoder.add(InputLayer(conv_shape))
        
        for filt in self.filters[-2::-1]:
            self.decoder.add(UpSampling2D(size=self.pool))
            self.decoder.add(Conv2D(filters=filt, kernel_size=self.kernel, 
                                    strides=self.stride, activation='relu', padding='same'))
        
        self.decoder.add(UpSampling2D(size=self.pool))
        self.decoder.add(Conv2D(filters=self.input_shape[2], kernel_size=self.kernel, 
                                strides=self.stride, activation='sigmoid', padding='same'))

        # compile model
        inputs = Input(self.input_shape)
        encoded = self.encoder(inputs)
        reconstructed = self.decoder(encoded)

        self.model = Model(inputs=inputs, outputs=reconstructed)
        self.model.compile(optimizer=self.optimizer, loss=self.lossfn)
    
    
    def _load(self):
        
        with open(os.path.join(self.path, 'params.yaml'), 'r') as f:
            params = yaml.load(f)

        self.input_shape = params['input_shape']
        self.latent_features = params['latent_features']
        self.filters = params['filters']
        self.kernel = params['kernel']
        self.stride = params['stride']
        self.pool = params['pool']
        self.optimizer = params['optimizer']
        self.lossfn = params['lossfn']
        
        self._compile()
        
        self.encoder.load_weights(os.path.join(self.path, "encoder.h5"))
        self.decoder.load_weights(os.path.join(self.path, "decoder.h5"))


    def save(self):
        
        if not os.path.exists(self.path):
            os.mkdir(self.path)
            
        params = {'input_shape': self.input_shape, 
                  'latent_features': self.latent_features,
                  'filters': self.filters,
                  'kernel': self.kernel,
                  'stride': self.stride,
                  'pool': self.pool,
                  'optimizer': self.optimizer,
                  'lossfn': self.lossfn}
    
        with open(os.path.join(self.path, 'params.yaml'), 'w') as f:
            yaml.dump(params, f)
            
        self.encoder.save_weights(os.path.join(self.path, "encoder.h5"))
        self.decoder.save_weights(os.path.join(self.path, "decoder.h5"))
    
    
    def fit(self, x, y, epochs=25, callbacks=[BaseLogger()], validation_split=0.1):

        self.model.fit(x=x, y=y, epochs=epochs, validation_split=validation_split,
                       callbacks=callbacks)

        
    def encode(self, inputs):
        return self.encoder.predict(inputs)

    
    def decode(self, codes):
        return self.decoder.predict(codes)