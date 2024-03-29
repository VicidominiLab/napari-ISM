# napari-ISM

[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-ISM)](https://napari-hub.org/plugins/napari-ISM)
[![License](https://img.shields.io/pypi/l/napari-ISM.svg?color=green)](https://github.com/VicidominiLab/napari-ISM/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-ISM.svg?color=green)](https://pypi.org/project/napari-ISM)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-ISM.svg?color=green)](https://python.org)


This plugin is built upon the python package [BrightEyes-ISM]. Napari-ISM enables the simulation, loading, and analysis of ISM datasets.
More in detail, it performs:

* Loading and compression of .h5 files generated by the [MCS software].
* Simulation of a realistic dataset of tubulin filaments.
* Simulation of realistic ISM Point Spread Functions.
* Summing over the detector array dimension
* Adaptive Pixel Reassignment
* Multi-image deconvolution
* Focus-ISM

----------------------------------

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/plugins/index.html
-->

## Installation

You can install `napari-ISM` via [PyPI]:

    pip install napari-ISM
    
or by using [napari hub].

It requires the following Python packages

    numpy
    scipy
    h5py
    qtpy
    matplotlib
    napari
    napari-plugin-engine
    brighteyes-ism>=1.2.2

## Documentation

To generate a simulated dataset, go to `File > Open Sample > ISM dataset`. 

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/sample.png)

To acces the plugin list, go to `Plugins > Napari-ISM`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/plugin_list.png)

To open a .h5 file, go to `File > Open `.
You can then sum over the dimensions that are not needed, using the command `integrateDims`.
The default axes are 0 (repetition), 1 (axial position), and 4 (time).

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/file.png)

Note that all the analysis commands expect an input with size `X x Y X Ch`.

To see the result of summing over the SPAD dimensions `Ch`, use the plugin command `Sum`. Then, press `Run`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/sum.png)

To see the result of Adaptive Pixel Reassignment, use the plugin command `APR_stack`.
Select as reference image (`ref`) the central one. Select an upsampling factor (`usf`), 
which corresponds to the sub-pixel precision of the shift-vector estimation. Then, press `Run`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/apr.png)

To generate the PSFs, use the plugin command `PSFs`. Select an image layer (`img layer`), 
it will be used to determine the number of pixels and the pixel size.
Then, select the detector pixel size (`pxsize`) and pixel pitch (`pxpitch`) in microns.
Select the magnification of the system (`M`). Select the excitation (`exWl`) and emission wavelength (`emWl`) in nanometers.
Then, press `Run`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/PSF.png)

To see the result of multi-image deconvolution, use the plugin command `Deconvolution`.
Select an image layer (`img layer`) containing the ISM dataset to deconvolve and another image layer (`psf layer`) containing the PSFs, either simulated or experimental.
Then, press `Run`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/deconv.png)

To use Focus-ISM, first select a region on the input dataset using a `shapes` layer.
Select a rectangle containing mainly in-focus emitters. It will be used as a calibration.
Then, use the plugin command `Focus-ISM`. Select an image layer (`img layer`) containing the ISM dataset and a shape layer (`shape layer`) defining the calibration region.
Select a lower bound for the standard deviation of the out-of-focus curve (`sigma B bound`) in units of standard deviations of the in-focus term. We suggest to never select a value below 2.
Select a threshold (`threshold`) in units of photon counts. Scan coordinates with less photons than the threshold will be skipped in the analysis and classified as background. Then, press `Run`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/shapes.png)

To use FRC, prepare the dataset to be in the shape `xyt`.
Select the theshodling method (`method`) and smoothing method (`smoothing`) among those available.
Then, press `Calculate`.

![](https://github.com/VicidominiLab/napari-ISM/raw/main/docs/frc.png)

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [GNU LGPL v3.0] license,
"napari-ISM" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/VicidominiLab/napari-ISM/issues

[napari hub]: https://www.napari-hub.org/plugins/napari-ISM
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/project/napari-ISM/

[BrightEyes-ISM]: https://github.com/VicidominiLab/BrightEyes-ISM
[MCS software]: https://github.com/VicidominiLab/BrightEyes-MCS