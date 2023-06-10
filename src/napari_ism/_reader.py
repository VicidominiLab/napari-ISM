import numpy as np
import h5py
    
import brighteyes_ism.dataio.mcs as mcs

def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        path = path[0]
        # show_info(path)
        
    # if we know we cannot read the file, we immediately return None.
    if path.endswith(".h5"):
        return reader_h5
    elif path.endswith(".npy"):
        return reader_npy
    else:
        return None

def reader_h5(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    
    # Load data

    try:
        data, meta = mcs.load(paths[0])
    except:
        data, meta = mcs.load(paths[0], key = 'data_analog')

    if meta.dz == 0:
        dz = 1
    else:
        dz = meta.dz*1e3
    
    dx = meta.dx * 1e3
    dy = meta.dy * 1e3
    
    scale = (1, dz, dx, dy, meta.dt, 1)

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {'colormap': 'magma', 'scale': scale}

    layer_type = "image"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]


def reader_npy(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path
    
    # load all files into array
    arrays = [np.load(_path) for _path in paths]
    # stack arrays into single array
    data = np.squeeze(np.stack(arrays))

    # optional kwargs for the corresponding viewer.add_* method
    add_kwargs = {'colormap': 'magma'}

    layer_type = "image"  # optional, default is "image"
    return [(data, add_kwargs, layer_type)]
