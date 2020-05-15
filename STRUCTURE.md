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
(see [`COMPILING.md`](COMPILING.md)) two files named `bundle.js` and
`bundle.js.map` are put into `diogenet_py/static/`. Those files are the compiled
source for the client and the sourcemap of it.

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

The `client/` directory contains the source for the javascript client, it has
a very simple structure consisting only of a `src/` subdirectory with the
TypeScript source of the client, and a few configuration files for the different
linters and compilers. In particular, ESLint with the TypeScript plugin is used
as a linter and Babel+Webpack are used to compile and bundle the source code to
a single file.
