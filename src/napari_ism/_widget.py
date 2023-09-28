import numpy as np

import napari
from napari.layers import Shapes, Image
from napari.types import LayerDataTuple

from brighteyes_ism.analysis.APR_lib import APR
from brighteyes_ism.analysis.Deconv_lib import MultiImg_RL_FFT
from brighteyes_ism.analysis.FocusISM_lib import focusISM
from brighteyes_ism.analysis.FRC_lib import timeFRC, plotFRC

from brighteyes_ism.analysis.Graph_lib import PlotShiftVectors, ShowFingerprint
from brighteyes_ism.analysis.Tools_lib import fingerprint

import brighteyes_ism.simulation.PSF_sim as ism

from matplotlib.backends.backend_qt5agg import FigureCanvas
from qtpy import QtWidgets

from magicgui import magic_factory

# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.

def Focus_ISM(img_layer: Image, shape_layer: Shapes, sigma_B_bound: float = 2,
              threshold: int = 25) -> LayerDataTuple:
    '''

    Parameters
    ----------
    img_layer : Image
        Raw ISM dataset to be processed.
    shape_layer : Shapes
        Rectangular shape selecting the calibration ROI of the dataset.
    sigma_B_bound : float
        Lower bound of the standard deviation of the out-of-focus microimage (units: sigma_A).
    threshold : int
        Minimum photon counts per microimage needed to start the fitting.
        If lower, the pixel is classified as background.
    Returns
    -------
    focus_ISM : napari.types.LayerDataTuple
        Image layer with the processed image.

    '''
    data = img_layer.data_raw
    scale = img_layer.scale
    
    sz = data.shape
    
    rect = shape_layer.data[0][:,:-1]

    scalenew = [ scale[0], scale[1] ]
    
    min_val = rect.min(axis=0).astype(int)
    max_val = rect.max(axis=0).astype(int)
    
    calib = data[min_val[0]: max_val[0], min_val[1]: max_val[1], :]
    
    sig, bkg, ism = focusISM(data, sigma_B_bound = sigma_B_bound, threshold = threshold, calibration = calib)
    
    # replicate results to match input dimensions
    
    result = np.expand_dims(sig, axis = -1)
    result = np.repeat(result, sz[-1], axis = -1)
    scalenew.append(1)
    
    # create layer
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Focus-ISM'}
    
    layer_type = "image"  # optional, default is "image"
    
    return [(result, add_kwargs, layer_type)]

def integrateDims(img_layer: Image, dim = (0, 1, 4) ) -> LayerDataTuple:
    '''

    Parameters
    ----------
    img_layer : napari.layers.Image
        Raw ISM dataset to be processed
    dim : tuple
        Indices of the dimensions to be summed.
        0: Repetition, 1: Z, 2: X, 3: Y, 4: Time, 5: Channel

    Returns
    -------
    compressed : LayerDataTuple
        Compressed ISM dataset
    '''

    dim = tuple(dict.fromkeys(dim))
    
    data = img_layer.data_raw
    scale = img_layer.scale

    scalenew = [element for i, element in enumerate(scale) if i not in dim]

    sumdata = np.sum(data, axis = dim) # sum over repetion and time
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Compressed'}
    
    layer_type = "image"  # optional, default is "image"

    return [(sumdata, add_kwargs, layer_type)]

def MultiImgDeconvolution(psf_layer: Image, img_layer: Image, iterations: int = 5) -> LayerDataTuple:
    '''

    Parameters
    ----------
    psf_layer : Image
        ISM point spread functions.
    img_layer : Image
        Raw ISM dataset to be processed.
    iterations : int
        Number of iterations to perform.

    Returns
    -------
    deconvolved : LayerDataTuple
        deconvolved and fused ISM image.
    '''
    psf = psf_layer.data_raw
    img = img_layer.data_raw
    
    scale = img_layer.scale
    
    scalenew = [ scale[0], scale[1] ]
    
    sz = img.shape
    
    deconv = MultiImg_RL_FFT( psf, img, max_iter = iterations )
    
    # replicate results to match input dimensions
    
    result = np.expand_dims(deconv, axis = -1)
    result = np.repeat(result, sz[-1], axis = -1)
    scalenew.append(1)
    
    # create layer
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Deconvolved'}

    layer_type = "image"  # optional, default is "image"
    
    return [(result, add_kwargs, layer_type)]

def SimulatePSFs(img_layer: Image, Nx: int = 201, pxdim: float = 50, pxpitch: float = 75, M: float = 450,
                 exWl: float = 640, emWl: float = 660) -> LayerDataTuple:
    '''

    Parameters
    ----------
    img_layer : Image
        ISM dataset, whose pixel size is the target of the simulation.
    Nx : int
        Number of pixels.
    pxdim : float
        Width of the active area of the individual SPAD element (microns).
    pxpitch : float
        Distance between adjacent SPAD elements of the detector (microns).
    M : float
        Total magnification of the ISM microscope.
    exWl : float
        Excitation wavelength.
    emWl : float
        Emission wavelength.

    Returns
    -------
    psfs : LayerDataTuple
        ISM point spread functions.
    '''

    img = img_layer.data_raw
    scale = img_layer.scale

    sz = img.shape
    
    # simulation parameters

    grid = ism.GridParameters()
    grid.N = int(np.sqrt(sz[-1]))
    grid.Nx = Nx
    grid.pxsizex = scale[0]
    grid.pxdim = pxdim*1e3
    grid.pxpitch = pxpitch*1e3
    grid.M = M
    
    exPar = ism.simSettings()
    exPar.wl = exWl # excitation wavelength (nm)
    exPar.mask_sampl = 31
    
    emPar = exPar.copy()
    emPar.wl = emWl # emission wavelength (nm)
    
    z_shift = 0 #nm
    
    # generate PSFs
    
    PSF, detPSF, exPSF = ism.SPAD_PSF_2D(grid, exPar, emPar, z_shift=z_shift)
    
    # create layer
    
    add_kwargs = {'colormap': 'magma', 'scale': scale, 'name': 'PSFs'}

    layer_type = "image"  # optional, default is "image"
    
    return [(PSF, add_kwargs, layer_type)]


def Fingerprint(img_layer: Image):
    '''

    Parameters
    ----------
    img_layer : Image
        ISM dataset used for the fingerprint calculation.
    '''
    viewer = napari.current_viewer()
    data = img_layer.data_raw

    fig, ax = ShowFingerprint(data)

    canvas = FigureCanvas(fig)

    viewer.window.add_dock_widget(canvas, name='Fingerprint', area='right')

    screen = QtWidgets.QDesktopWidget().screenGeometry()
    width = screen.width()

    canvas.setMinimumHeight(int(width / 6))
    canvas.setMinimumWidth(int(width / 6))

def APR_stack(img_layer: Image, usf = 10, ref = 12) -> LayerDataTuple:
    '''

    Parameters
    ----------
    img_layer : napari.layers.Image
        Raw ISM dataset to be processed. It can be a stack of datasets.
    usf :
        Upsampling factor used to achieve subpixel precision.
    ref :
        Reference image used for registration.
        It should the one generated by the central element of the detector array.

    Returns
    -------
    reassigned : LayerDataTuple
        Reassigned image or stack.
    '''
    data = img_layer.data_raw
    scale = img_layer.scale
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
        scalenew = [ scale[0], scale[1] ]
    else:
        scalenew = [ 1, scale[0], scale[1] ]
        
    sz = data.shape
    
    data2 = np.empty(sz)
    shifts = np.empty( [sz[0], sz[-1], 2] )
    
    for n in range(sz[0]):
        shifts[n], data2[n] = APR(data[n], usf, ref)

    shifts = np.squeeze(shifts)
    data_apr = np.squeeze(data2.sum(axis=-1))
    data_apr[data_apr < 0] = 0

    # Plot shift vectors

    if sz[0] < 2:
        viewer = napari.current_viewer()

        fing = fingerprint(data)
        fig, ax = PlotShiftVectors( shifts, color = fing )

        canvas = FigureCanvas(fig)

        viewer.window.add_dock_widget(canvas, name='Shift Vectors', area='right')

        screen = QtWidgets.QDesktopWidget().screenGeometry()
        width = screen.width()

        canvas.setMinimumHeight(int(width/6))
        canvas.setMinimumWidth(int(width/6))

    # replicate results to match input dimensions
    
    result = np.expand_dims(data_apr, axis = -1)
    result = np.repeat(result, sz[-1], axis = -1)
    scalenew.append(1)
    
    # create layer
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'APR'}

    layer_type = "image"  # optional, default is "image"

    return [(result, add_kwargs, layer_type)]


def SumSPAD(img_layer: Image) -> LayerDataTuple:
    '''

    Parameters
    ----------
    img_layer : Image
        Raw ISM dataset to be summed along the channel dimension.

    Returns
    -------
    summed : LayerDataTuple
        Reassigned image or stack.
    '''

    data = img_layer.data_raw
    scale = img_layer.scale
    
    if data.ndim < 4:
        data = np.expand_dims(data, axis=0)
        scalenew = [ scale[0], scale[1] ]
    else:
        scalenew = [ 1, scale[0], scale[1] ]
        
    sz = data.shape
    
    data_sum = np.squeeze( np.sum(data, axis = 3) )
    
    # replicate results to match input dimensions
    
    result = np.expand_dims(data_sum, axis = -1)
    result = np.repeat(result, sz[-1], axis = -1)
    scalenew.append(1)
    
    # create layer
    
    add_kwargs = {'colormap': 'magma', 'scale': scalenew, 'name': 'Sum'}

    layer_type = "image"  # optional, default is "image"
    
    return [(result, add_kwargs, layer_type)]


@magic_factory(
    call_button = "Calculate",
    img_layer = {"label": "Images:"},
    method = {"choices": ['fixed', '3sigma', '5sgigma'], "label": "Threshold:"},
    smoothing = {"choices": ['fit', 'lowess'], "label": "Smoothing method:"}
)
def FRC(img_layer: Image, method: str = 'fixed', smoothing: str = 'fit'):
    '''

    Parameters
    ----------
    img_layer : Image
        Time series of images (X x Y x Time).
    method :
        Thresholding criterion for the FRC curve.
    smoothing :
        Smoothing method for the FRC curve.
    '''
    viewer = napari.current_viewer()
    data = img_layer.data_raw

    scale = img_layer.scale

    frc_result = timeFRC(data, px = scale[0]*1e-3, method = method, smoothing = smoothing)

    fig, ax = plotFRC(*frc_result)

    canvas = FigureCanvas(fig)

    viewer.window.add_dock_widget(canvas, name='Fourier Ring Correlation', area='right')

    screen = QtWidgets.QDesktopWidget().screenGeometry()
    width = screen.width()

    canvas.setMinimumHeight(int(width / 6))
    canvas.setMinimumWidth(int(width / 6))