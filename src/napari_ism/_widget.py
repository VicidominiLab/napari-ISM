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

from brighteyes_ism.analysis.APR_lib import APR
from brighteyes_ism.analysis.Deconv_lib import MultiImg_RL_FFT
from brighteyes_ism.analysis.FocusISM_lib import focusISM

import brighteyes_ism.simulation.PSF_sim as ism

# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.

def integrateDims(img_layer: "napari.layers.Image", dim = (0, 4) ) -> "napari.types.ImageData":
    
    data = img_layer.data_raw
    
    sdata = np.sum(data, axis = dim  ) # sum over repetion and time
    
    return 

def MultiImgDeconvolution(psf_layer: "napari.layers.Image", img_layer: "napari.layers.Image", iterations = 5) -> "napari.types.ImageData":

    psf = psf_layer.data_raw
    img = img_layer.data_raw
    
    result = MultiImg_RL_FFT( psf, img, max_iter = iterations )
    
    return result

def SimulatePSFs(img_layer: "napari.layers.Image", pxsizex = 25, pxdim = 50, pxpitch = 75, M = 500, exWl = 640, emWl = 660) -> "napari.types.ImageData":
    """Generates an image"""
    
    img = img_layer.data_raw
    sz = img.shape
    
    N = int( np.sqrt(sz[-1]) ) # number of detector elements in each dimension
    Nx = sz[0] # number of pixels of the simulation space
    pxsizex = pxsizex # pixel size of the simulation space (nm)
    pxdim = pxdim*1e3 # detector element size in real space (nm)
    pxpitch = pxpitch*1e3 # detector element pitch in real space (nm)
    M = M # total magnification of the optical system (e.g. 100x objective follewd by 5x telescope)
    
    
    exPar = ism.simSettings()
    exPar.wl = exWl # excitation wavelength (nm)
    exPar.mask_sampl = 31
    
    emPar = exPar.copy()
    emPar.wl = emWl # emission wavelength (nm)
    
    z_shift = 0 #nm
    
    ###
    
    PSF, detPSF, exPSF = ism.SPAD_PSF_2D(N, Nx, pxpitch, pxdim, pxsizex, M, exPar, emPar, z_shift=z_shift)
    PSF /= np.max(PSF)

    return PSF

def gauss2d(X, Y, mux, muy, sigma):
    
    # R = np.sqrt(X**2 + Y**2)
    g = np.exp( -( (X - mux)**2 + (Y - muy)**2)/(2*sigma**2) )
    
    return g / np.sum(g)


def APR_stack(img_layer: "napari.layers.Image", usf = 10, ref = 12) -> "napari.types.ImageData":

    data = img_layer.data_raw
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
    
    sz = data.shape
    
    data2 = np.empty( sz )
    
    for n in range(sz[0]):
        data2[n,:,:,:] = APR(data[n,:,:,:], usf, ref)[1]
    
    data_apr = np.squeeze( np.sum(data2, axis = -1) )
    
    data_apr[data_apr<0] = 0
    
    # return data_apr
    
    result = np.expand_dims(data_apr, axis = -1)
    
    # # result = np.repeat(result, sz[-1], axis = -1)
    
    return result

def SumSPAD(img_layer: "napari.layers.Image") -> "napari.types.ImageData":
    
    data = img_layer.data_raw
    sz = data.shape
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
    
    data_sum = np.squeeze( np.sum(data, axis = 3) )
    
    result = np.expand_dims(data_sum, axis = data_sum.ndim)
    
    result = np.repeat(result, sz[-1], axis = data_sum.ndim )
    
    return result