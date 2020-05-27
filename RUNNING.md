# Running the server #

**Note**: This document assumes that you have already built the server.
See the [`COMPILING.md`](COMPILING.md) file for instructions on how to
build it.

## Running from the source ##

This method doesn't require you to package the application but the commands
described here **need*** to be run from the project's top-level directory.

For POSIX systems, execute the following commands on a shell:

```sh
export FLASK_APP="diogenet_py.app"
export FLASK_ENV="development"
flask run
```

In Windows the following commands can be used instead (they must be
executed in PowerShell, not in Windows' CMD):

```powershell
[System.Environment]::SetEnvironmentVariable("FLASK_APP", "diogenet_py.app")
[System.Environment]::SetEnvironmentVariable("FLASK_ENV", "development")
flask run
```

Changing the `FLASK_ENV` variable from `development` to `production` will
instead run the server in production mode (but see the "Running in
production" section for details).

If the server is started on development mode, Flask will re-render any
required templates on each HTTP call and will not cache files. This combined
with the fact that the client's compiled files go into `diogenet_py/static/`
means that executing the server from the source in development mode allows
you to make almost any change to both the client and the server and see the
effects instantly.

## Running from a package ##

If you have packaged the application into a Wheel (`.whl`) or an sdist and
installed it, then any of the following two options can be used to run the
server:

1. The previous commands can still be used, but now they can be used anywhere,
not only in the top-level directory of the project.
2. The command `diogenet-py` should have been installed along the package:
to run the server using this command just execute `diogenet-py`.

Changes made to the source will only be visible if the package was installed
on development mode (see [`COMPILING.md`](COMPILING.md) for more information
about installing a package in development mode**.

**Warning**: The command `diogenet-py` is currently unimplemented.

## Running in production ##

Flask applications are not meant to be run directly in production, instead
a WSGI wrapper should be used. The Flask documentation [contains more
information](https://flask.palletsprojects.com/en/1.1.x/deploying/)
on how to do it with the most common web servers (Apache, Ngix, etc).
