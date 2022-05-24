"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
# import napari
import numpy as np
from scipy.ndimage import fourier_shift
from skimage.registration import phase_cross_correlation

# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.

def APR_stack(img_layer: "napari.layers.Image", usf = 10, ref = 12) -> "napari.types.ImageData":

    data = img_layer.data_raw
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
    
    sz = data.shape
    
    data2 = np.empty( sz )
    
    for n in range(sz[0]):
        data2[n,:,:,:] = APR(data[n,:,:,:], usf, ref)
    
    data_apr = np.squeeze( np.sum(data2, axis = 3) )
    
    # data2[np.where(data2)<0] = 0
    
    # viewer.add_image(data2, colormap='magma')
    
    result = np.expand_dims(data_apr, axis = data_apr.ndim)
    
    result = np.repeat(result, sz[-1], axis = data_apr.ndim)
    
    print(sz)
    print(result.shape)


def APR(dset, usf = 10, ref = 12):
    
    sz = dset.shape
    
    shift = np.empty( (sz[-1], 2) )
    error = np.empty( (sz[-1], 2) )
    result_ism_pc = np.empty( sz )
    
    for i in range( sz[-1] ):
        
        shift[i,:], error[i,:], diffphase = phase_cross_correlation(dset[:,:, ref], dset[:,:,i],upsample_factor=usf, normalization=None)
        
        offset  = fourier_shift(np.fft.fftn(dset[:,:,i]), (shift[i,:]))
        result_ism_pc[:,:,i]  = np.real( np.fft.ifftn(offset) )
    
    return result_ism_pc

def SumSPAD(img_layer: "napari.layers.Image") -> "napari.types.ImageData":
    
    data = img_layer.data_raw
    sz = data.shape
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
    
    data_sum = np.squeeze( np.sum(data, axis = 3) )
    
    result = np.expand_dims(data_sum, axis = data_sum.ndim)
    
    result = np.repeat(result, sz[-1], axis = data_sum.ndim )
    
    print(sz)
    print(result.shape)
    
    return result