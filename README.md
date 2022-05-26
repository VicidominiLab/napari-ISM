# napari-ISM

[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-ISM)](https://napari-hub.org/plugins/napari-ISM)
[![License](https://img.shields.io/pypi/l/napari-ISM.svg?color=green)](https://github.com/VicidominiLab/napari-ISM/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-ISM.svg?color=green)](https://pypi.org/project/napari-ISM)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-ISM.svg?color=green)](https://python.org)
<!--
[![tests](https://github.com/VicidominiLab/napari-ISM/workflows/tests/badge.svg)](https://github.com/VicidominiLab/napari-ISM/actions)
[![codecov](https://codecov.io/gh/VicidominiLab/napari-ISM/branch/main/graph/badge.svg)](https://codecov.io/gh/VicidominiLab/napari-ISM)
-->


It performs Adaptive Pixel Reassignment via a phase-correlation algorithm. Once installed, you can upload any ISM-dataset in .h5 or .npy format. The plugin expects a numpy array of the format _rzxytc_ (r: repetition, z: axial dimension, xy: lateral dimensions, t: time dimension, c: detector element). If the _rzt_ dimensions are not present, add manually fake dimensions (e.g. using the _numpy.expand_dims_ function).
You can also generate a synthetic ISM-dataset from the File menu. Once a dataset is uploaded on an image layer, you can use the Napari plugin menu to perform either a sum on the _c_ dimension or perform Adaptive Pixel Reassignment on the _c_ dimension.

----------------------------------

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/plugins/index.html
-->

## Installation

You can install `napari-ISM` via [pip]:

    pip install napari-ISM

It requires the following Python packages

    numpy
	scipy
	scikit-image
    h5py
	napari

<!--

To install latest development version :

    pip install git+https://github.com/VicidominiLab/napari-ISM.git
-->

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

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
