# Setup the Project #

## Installing the Python Package ##

The python package itself does not needs to be compiled, but to run it outside
of the toplevel directory it needs to be installed.

### Creating a Virtual Environment ###

For safety reasons a virtual environment is recommended to be used. If
virtualenvwrapper is being used then the following command should create a
virtual environment with the name `diogenet_py`. That specific name is not
required but if you use a different one remember to change it throught the rest
of the installation instructions:

```sh
mkvirtualenv diogenet_py
# For ms windows setup u must install virtualenvwrapper-win (pip install virtualenvwrapper-win)
```

### Installing the dependencies ###

Now the dependencies of the package need to be installed. The recommended way
of installing them is using the `requirements.txt` file which specifies the **exact**
version of every dependency. Nonetheless, if more flexibility is required then the
dependencies can be installed from `setup.cfg`.

**Note**: While working on `diogenet_py` it is strongly recommended to use
`requirements.txt` as it provides a consistent working environment. While
*deploying* `diogenet_py` any of the two different options can be used but
they come with different tradeoffs:

- `requirements.txt` has the most probability of just working as it is the same
  environment in which `diogenet_py` is tested.
- The list in `setup.cfg` will always use the most recent versions available
  which easyl provides security fixes.

To install the dependencies from `requirements.txt` execute in the toplevel
directory:

```sh
pip install -r requirements.txt
```

Dependencies from `setup.cfg` will be automatically installed in the next step.

### Installing the package ###

If continuous work is being done on the source of the package, the easiest
way to install it is with:

```sh
pip install -e .
```

Which will install the package in the current virtual environment in *editable*
mode (so changes to the source code are inmmediatly available, no need to
reinstall).

## Building the Documentation ##

To build the documentation first enter the `docs/` directory and execute
`make html` (in \*NIX systems) or `make.bat` (in Microsoft Windows systems).
That will build the HTML documentation. You can additionally just execute
`make` without any argument to see the available commands.

## Running the server ##

The [`RUNNING.md`](RUNNING.md) file contains instructions on how to execute the
server once built.
