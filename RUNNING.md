# Running the server #

**Note**: At this point you must have already built the server.
Check [`COMPILING.md`](COMPILING.md) for detailed instructions about how to
build it.

## Running from the source ##

This method does not require you to package the application. However, the commands
described in this document **need*** to be run from the top-level directory of the project.

For POSIX systems execute the following commands on a shell:

```sh
export FLASK_APP="diogenet_py.app"
export FLASK_ENV="development"
flask run
```

In Windows the following commands can be used instead. This must be
executed in PowerShell, not in Windows' CMD. 

```powershell
[System.Environment]::SetEnvironmentVariable("FLASK_APP", "diogenet_py.app")
[System.Environment]::SetEnvironmentVariable("FLASK_ENV", "development")
flask run
```
At this point the service should be available at the defined `http` site.  

Changing the `FLASK_ENV` variable from `development` to `production` will run the 
server in production mode (See the "Running in production" section for details).

If the server is started in development mode, Flask will re-render any
required templates on each HTTP call and will not cache files. Since the compiled 
files of the client go into `diogenet_py/static/`, executing the server from the source 
in development mode allows you to make changes in the source and inmediatly have the changes 
available in the deployment. Changes can be made to both the client and the server.   

## Running from a package ##

If you have packaged the application into a Wheel (`.whl`) or an sdist, and
installed it, then any of the following two options can be used to run the
server:

1. The previous commands can still be used, but now they can be used anywhere,
not only in the top-level directory of the project.
2. The command `diogenet-py` should have been installed along the package:
to run the server using this command just execute `diogenet-py`.

Changes made to the source will only be visible if the package was installed
on development mode (see [`COMPILING.md`](COMPILING.md) for more information
about installing a package in development mode**).

**Warning**: The command `diogenet-py` is currently unimplemented.

## Running in production ##

Flask applications are not meant to be run directly in production, instead
a WSGI wrapper should be used. The Flask documentation [contains more
information](https://flask.palletsprojects.com/en/1.1.x/deploying/)
on how to do it with the most common web servers (Apache, Ngix, etc).
