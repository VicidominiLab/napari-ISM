"""
This module is an example of a barebones writer plugin for napari.

It implements the Writer specification.
see: https://napari.org/plugins/guides.html?#writers

Replace code below according to your needs.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Sequence, Tuple, Union

import numpy as np
import h5py

if TYPE_CHECKING:
    DataType = Union[Any, Sequence[Any]]
    FullLayerData = Tuple[DataType, dict, str]


def write_single_image(path: str, data: Any, meta: dict):
    """Writes a single image layer"""
    if path.endswith(".h5"):
        f = h5py.File(path, "w")
        f.create_dataset("data", data = data)
        
        return [path]
    
    if path.endswith(".npy"):
        np.save(path, data)
        
        return [path]


def write_multiple(path: str, data: List[FullLayerData]):
    """Writes multiple layers of different types."""
