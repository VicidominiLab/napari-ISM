"""
This module is an example of a barebones sample data provider for napari.

It implements the "sample data" specification.
see: https://napari.org/plugins/guides.html?#sample-data

Replace code below according to your needs.
"""
# from __future__ import annotations

import numpy as np
from numpy.random import poisson, rand
from scipy.signal import convolve
# from scipy.ndimage import fourier_shift
# import matplotlib.pyplot as plt

def gauss2d(X, Y, mux, muy, sigma):
    
    # R = np.sqrt(X**2 + Y**2)
    g = np.exp( -( (X - mux)**2 + (Y - muy)**2)/(2*sigma**2) )
    
    return g / np.sum(g)


def make_sample_data():
    """Generates an image"""
    
    #object space
    
    N = 513
    
    x = np.arange(N) - N//2
    X, Y = np.meshgrid(x, x)
    
    obj = rand(N, N) // 0.9999
    
    #shift vectors
    
    Ndet = 5
    sigma = 3
    
    sx = ( np.arange(Ndet) - 5//2 )* 0.66*sigma
    SX, SY = np.meshgrid(sx, -sx)

    #psf and images
    
    signal = 5e3 * gauss2d(SX, SY, 0, 0, 2).ravel()

    data = np.empty( (N, N, Ndet**2 ) )
    h = np.empty( (N, N, Ndet**2 ) )
    
    for i in range( Ndet**2 ):
        h[:, :, i] = gauss2d(X, Y, SX.ravel()[i], SY.ravel()[i], sigma)
        data[:, :, i] = signal[i] * convolve(obj, h[:, :, i], mode='same') # convolve(obj, psf[:, :, i], mode='same')
        data[data<0] = 0
        
    img = poisson(lam = data)
    
    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {'colormap': 'viridis'}

    layer_type = "image"  # optional, default is "image"
    
    return [(img, add_kwargs, layer_type)]