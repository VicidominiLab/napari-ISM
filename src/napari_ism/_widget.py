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

from magicgui import magic_factory
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")


@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")


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
    
    data_apr = np.sum(data2, axis = 3)
    
    # data2[np.where(data2)<0] = 0
    
    # viewer.add_image(data2, colormap='magma')
    
    result = np.expand_dims(np.squeeze(data_apr), axis = data_apr.ndim)
    
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
    
    data_sum = np.sum(data, axis = 3)
    
    result = np.expand_dims(np.squeeze(data_sum), axis = data_sum.ndim)
    
    result = np.repeat(result, sz[-1], axis = data_sum.ndim )
    
    print(sz)
    print(result.shape)
    
    return result