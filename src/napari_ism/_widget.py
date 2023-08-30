import numpy as np

import napari
from napari_plugin_engine import napari_hook_implementation

from brighteyes_ism.analysis.APR_lib import APR
from brighteyes_ism.analysis.Deconv_lib import MultiImg_RL_FFT
from brighteyes_ism.analysis.FocusISM_lib import focusISM
from brighteyes_ism.analysis.FRC_lib import timeFRC, plotFRC

from brighteyes_ism.analysis.Graph_lib import PlotShiftVectors, ShowFingerprint
from brighteyes_ism.analysis.Tools_lib import fingerprint

import brighteyes_ism.simulation.PSF_sim as ism

from matplotlib.backends.backend_qt5agg import FigureCanvas
from PyQt5 import QtWidgets

from magicgui import magicgui

# Uses the `autogenerate: true` flag in the plugin manifest
# to indicate it should be wrapped as a magicgui to autogenerate
# a widget.

def Focus_ISM(img_layer: "napari.layers.Image", shape_layer: "napari.layers.Shapes", sigma_B_bound = 2, threshold = 25) -> "napari.types.LayerDataTuple":
    
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

def SimulatePSFs(img_layer: "napari.layers.Image", Nx = 201, pxdim = 50, pxpitch = 75, M = 500, exWl = 640, emWl = 660) -> "napari.types.LayerDataTuple":# -> "napari.types.ImageData":
    
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


def Fingerprint(img_layer: "napari.layers.Image"):

    viewer = napari.current_viewer()
    data = img_layer.data_raw

    fig, ax = ShowFingerprint(data)

    canvas = FigureCanvas(fig)

    viewer.window.add_dock_widget(canvas, name='Fingerprint', area='right')

    screen = QtWidgets.QDesktopWidget().screenGeometry()
    width = screen.width()

    canvas.setMinimumHeight(int(width / 6))
    canvas.setMinimumWidth(int(width / 6))

def APR_stack(img_layer: "napari.layers.Image", usf = 10, ref = 12) -> "napari.types.LayerDataTuple":

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


def SumSPAD(img_layer: "napari.layers.Image") -> "napari.types.LayerDataTuple":
    
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


@napari_hook_implementation
def FRC():
   return _timeFRC

@magicgui(
    call_button="Calculate",
    method = {"choices": ['fixed', '3sigma', '5sgigma']},
    smoothing = {"choices": ['fit', 'lowess']},
)
def _timeFRC(img_layer: "napari.layers.Image", method: str = 'fixed', smoothing: str = 'fit'):

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