import os
import numpy as np

from keras.models import Sequential, Model
from keras.layers import Input, Dense, Flatten, Reshape, InputLayer
from keras.layers import MaxPooling2D, UpSampling2D, Conv2D, Conv2DTranspose
from keras.callbacks import BaseLogger

class CAE:

    def __init__(self, input_shape, output_dim, 
                 filters=[8, 16, 32], kernel=(3,3), stride=1, pool=(2,2), 
                 optimizer="adamax", lossfn="mse", path=None):
        
        self.path = path if path else os.getcwd()
        self.input_shape = input_shape
        self.output_dim  = output_dim
        
        # define encoder architecture
        self.encoder = Sequential()
        self.encoder.add(InputLayer(input_shape))  
        
        conv_shape = input_shape
        for filt in filters:
            self.encoder.add(Conv2D(filters=filt, kernel_size=kernel, 
                                    strides=stride, activation='relu', padding='same'))
            self.encoder.add(MaxPooling2D(pool_size=pool))
            conv_shape = (int(conv_shape[0]/pool[0]), int(conv_shape[1]/pool[1]), filt)
            
        self.encoder.add(Flatten())
        self.encoder.add(Dense(output_dim, activation='relu'))
        
        # define decoder architecture
        self.decoder = Sequential()
        self.decoder.add(InputLayer((output_dim,)))
        self.decoder.add(Dense(np.prod(conv_shape), activation='relu'))
        self.decoder.add(Reshape(conv_shape))
        
        for filt in filters[-2::-1]:
            self.decoder.add(UpSampling2D(size=pool))
            self.decoder.add(Conv2D(filters=filt, kernel_size=kernel, 
                                    strides=stride, activation='relu', padding='same'))
        
        self.decoder.add(UpSampling2D(size=pool))
        self.decoder.add(Conv2D(filters=input_shape[2], kernel_size=kernel, 
                                strides=stride, activation='sigmoid', padding='same'))

        # compile model
        inputs = Input(input_shape)
        encoded = self.encoder(inputs)
        reconstructed = self.decoder(encoded)

        self.model = Model(inputs=inputs, outputs=reconstructed)
        self.model.compile(optimizer=optimizer, loss=lossfn)

        
    def fit(self, x, y, epochs=25, callbacks=[BaseLogger()], validation_split=0.1):

        self.model.fit(x=x, y=y, epochs=epochs, validation_split=validation_split,
                       callbacks=callbacks)


    def save_weights(self):
        self.encoder.save_weights(os.path.join(self.path, "encoder.h5"))
        self.decoder.save_weights(os.path.join(self.path, "decoder.h5"))


    def load_weights(self):
        self.encoder.load_weights(os.path.join(self.path, "encoder.h5"))
        self.decoder.load_weights(os.path.join(self.path, "decoder.h5"))


    def encode(self, inputs):
        return self.encoder.predict(inputs)

    
    def decode(self, codes):
        return self.decoder.predict(codes)