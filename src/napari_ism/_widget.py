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

def Focus_ISM(img_layer: "napari.layers.Image", shape_layer: "napari.layers.Shapes", sigma_B_bound = 2, threshold = 25) -> "napari.types.LayerDataTuple":
    
    data = img_layer.data_raw
    scale = img_layer.scale
    
    rect = shape_layer.data[0][:,:-1]

    scalenew = (scale[0], scale[1])
    
    min_val = rect.min(axis=0).astype(int)
    max_val = rect.max(axis=0).astype(int)
    # tl = np.array([min_val[0], min_val[1]])
    # br = np.array([max_val[0], max_val[1]])
    # box = np.round(np.array([tl, br])).astype(int)
    
    calib = data[min_val[0]: max_val[0], min_val[1]: max_val[1], :]
    
    
    sig, bkg, ism = focusISM(data, sigma_B_bound = sigma_B_bound, threshold = threshold, calibration = calib)
    
    ###
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Focus-ISM'}
    
    layer_type = "image"  # optional, default is "image"
    
    return [(sig, add_kwargs, layer_type)]

def integrateDims(img_layer: "napari.layers.Image", dim = (0, 1, 4) ) -> "napari.types.LayerDataTuple":
    
    dim = tuple(dict.fromkeys(dim))
    
    data = img_layer.data_raw
    scale = img_layer.scale

    scalenew = [element for i, element in enumerate(scale) if i not in dim]

    sumdata = np.sum(data, axis = dim) # sum over repetion and time
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Compressed'}
    
    layer_type = "image"  # optional, default is "image"
    
    return [(sumdata, add_kwargs, layer_type)]

def MultiImgDeconvolution(psf_layer: "napari.layers.Image", img_layer: "napari.layers.Image", iterations = 5) -> "napari.types.LayerDataTuple":

    psf = psf_layer.data_raw
    img = img_layer.data_raw
    
    scale = img_layer.scale
    
    result = MultiImg_RL_FFT( psf, img, max_iter = iterations )
    
    add_kwargs = {'colormap': 'magma', 'scale': (scale[0], scale[1]), 'name': 'Deconvolved'}

    layer_type = "image"  # optional, default is "image"
    
    return [(result, add_kwargs, layer_type)]

def SimulatePSFs(img_layer: "napari.layers.Image", pxdim = 50, pxpitch = 75, M = 500, exWl = 640, emWl = 660) -> "napari.types.LayerDataTuple":# -> "napari.types.ImageData":
    """Generates an image"""
    
    img = img_layer.data_raw
    scale = img_layer.scale

    sz = img.shape
    
    N = int( np.sqrt(sz[-1]) ) # number of detector elements in each dimension
    Nx = sz[0] # number of pixels of the simulation space
    pxsizex = scale[0] # pixel size of the simulation space (nm)
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
    
    add_kwargs = {'colormap': 'magma', 'scale': scale, 'name': 'PSFs'}

    layer_type = "image"  # optional, default is "image"
    
    return [(PSF, add_kwargs, layer_type)]


def APR_stack(img_layer: "napari.layers.Image", usf = 10, ref = 12) -> "napari.types.LayerDataTuple":

    data = img_layer.data_raw
    scale = img_layer.scale
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
        scale = (1, scale[0], scale[1])
    else:
        scale = (scale[0], scale[1])
        
    sz = data.shape
    
    data2 = np.empty( sz )
    
    for n in range(sz[0]):
        data2[n,:,:,:] = APR(data[n,:,:,:], usf, ref)[1]
    
    data_apr = np.squeeze( np.sum(data2, axis = -1) )
    
    data_apr[data_apr<0] = 0
    
    # result = np.expand_dims(data_apr, axis = -1)
    
    # # result = np.repeat(result, sz[-1], axis = -1)
    
    add_kwargs = {'colormap': 'magma', 'scale': scale, 'name': 'APR'}

    layer_type = "image"  # optional, default is "image"
    
    return [(data_apr, add_kwargs, layer_type)]

def SumSPAD(img_layer: "napari.layers.Image") -> "napari.types.ImageData":
    
    data = img_layer.data_raw
    sz = data.shape
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
    
    data_sum = np.squeeze( np.sum(data, axis = 3) )
    
    result = np.expand_dims(data_sum, axis = data_sum.ndim)
    
    result = np.repeat(result, sz[-1], axis = data_sum.ndim )
    
    add_kwargs = {'colormap': 'magma'}

    layer_type = "image"  # optional, default is "image"
    
    return [(result, add_kwargs, layer_type)]