# Compiling the Project #

## Compiling the Client ##

First the client needs to be compiled. For this enter to the `client/`
directory and execute `npm install` to locally install all the required
dependencies. After that executing `npm run build` should build the client:

```sh
cd client/
npm install
npm run build
```

While working on the client this edit-compile-run cycle can get a bit slow
(webpack isn't the fastest while compiling typescript). To address this issue
a "dev server" is provided that automatically detect any change in the
source, compile it and then place the compiled client into
`diogenet_py/static/client/`. To run this dev server the following command
must be used instead of `npm build`:

```sh
npm run start
```

Compiling the client will put all the compiled resources (with their respective
sourcemap) in the `diogenet_py/static/client` directory. All resources,
including SASS/SCSS and dependencies of the program (like images or icons)
will also go to that directory. Now that they are compiled the Flash
application can make use of them.

**Note**: It is required to build the client before using the `diogenet_py`
package. Once the server is built, it does not need to be rebuilt when changes
are made only over `diogenet_py`.

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

#### Installing for development ####

If continuous work is being done on the source of the package, the easiest
way to install it is with:

```sh
pip install -e .
```

Which will install the package in the current virtual environment in *editable*
mode (so changes to the source code are inmmediatly available, no need to
reinstall).

#### Installing for production ####

The application can be packaged as described in the next section.  That will
automatically install the package and its dependencies as a `whl` file, under
`dist/`, and in the current virtual environment.

### Packaging ###

To package the whole app into a distributable "source distribution" (*sdist*)
or wheel file (`.whl`) which can later be installed in another computer it
first needs to be built as follows:

```sh
python3 setup.py build
```

**Note**: Remember to build the client before this!

[//]: # (How should I build the client?)

This will produce several files and an additional `dist/` directory. That
directory contains the wheel file which can be distributed and installed.

To directly install the application sidestepping the wheel file, just execute:

```sh
python3 setup.py install
```

If this is done then the wheel file does not need to be installed as
described in the "Installing for production" section.

## Building the Documentation ##

To build the documentation first enter the `docs/` directory and execute
`make html` (in \*NIX systems) or `make.bat` (in Microsoft Windows systems).
That will build the HTML documentation. You can additionally just execute
`make` without any argument to see the available commands.

## Running the server ##

The [`RUNNING.md`](RUNNING.md) file contains instructions on how to execute the
server once built.
