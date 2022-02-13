# Usage Monitor
Provides Python CPU, GPU, and runtime monitors in the form of context managers.

## Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Uninstallation](#uninstallation)

## Installation

See the `requirements.txt` file for the required packages. One can install all of them with pip by using:

```bash
$ pip install -r requirements.txt
```
Users who have no need for GPU monitoring may wish to skip installing `GPUtil`.

Once the required packages are installed, download this repository, then navigate to the base folder and run:

```
$ pip install [-e] .
```

where `-e` will install the package in-place if desired.

## Usage

Example use case:
```python
>>> import numpy as np
>>> from monitor import *
>>> 
>>> A = np.random.randint(1, 50, size=(1000, 1000))
>>> B = np.random.randint(1, 50, size=(1000, 1000))
>>> 
>>> with Runtime("matmul") as t:
>>>     C = A @ B
matmul: 1.2834016999999989
>>> print(t.elapsed)
1.2834016999999989
```

## Uninstallation

To uninstall the package, use:

`pip uninstall monitor`