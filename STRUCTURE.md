# Project Structure #

The toplevel directories are:

- `diogenet_py`: The Python package with the server.
- `docs`: Sphinx docs for the Python package.
- `tests`: Tests for the Python package.
- `client`: Source for the JavaScript client.

## The Python Package ##

`diogenet_py/` contains the python package for the server. To start the server
the function `main` in the module `diogenet_py.main` must be called or the
module `diogenet_py.main` must be executed (preferably with
`python3 -m diogenet_py.main` either in the toplevel directory or after
installing). This package has two special directories in it: `static/` and
`templates/`. `static/` contains static files for the Flask application and
`templates/` contains the Jinja templates.

There is an special file in `diogenet_py/static/`: When the client is compiled
(see [`COMPILING.md`](COMPILING.md)) a directory `client/` inside
`diogenet_py/static/` will contain all the compiled resources.

## The Documentation ##

The `docs/` directory contains the documentation for the `diogenet_py` package.
This project uses Sphinx to generate the documentation.

Just like the `diogenet_py/` directory, inside `docs/` there are two
important subdirectories: `_static/` which contains static files for the
documentation and `_templates/` which contains the sphinx templates.

## The Tests ##

The `tests/` directory has all the tests for the `diogenet_py` package. It uses
Pytest as it's testing framework. Keeping with the Pytest practice, every file
under `tests/` which filename starts with `test_` is a test.

## The Client ##

The `client/` directory contains the source for the Javascript client. It has
a very simple structure:

- `src/` contains the typescript/javascript sources. Generally one main file
  per page (so `map.ts` for the map page and `horus.ts` for the horus).
- `styles/` contains any SASS/SCSS to be compiled.

Typescript is compiled to Javascript which is later passed to Babel. The
SASS/SCSS files are compiled too via a dummy `styles.ts` file that imports
them. All of the compiled files are then bundled with Webpack and the
compiled output (plus any additional sourcemap) is put into
`diogenet_py/static/client/` where the server can load it.
