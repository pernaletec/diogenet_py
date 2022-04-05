# Running the server #

**Note**: At this point you must have already built the server.
Check [`COMPILING.md`](COMPILING.md) for detailed instructions about how to
build it.

## Running from the source ##

This method does not require you to package the application. However, the commands
described in this document **need*** to be run from the top-level directory of the project.

For run the horus app execute the following commands on a shell:

```sh
gunicorn horus.index:server
```

At this point the service should be available at the defined `http` site.
## Running in production ##

Flask applications are not meant to be run directly in production, instead
a WSGI wrapper should be used. The Flask documentation [contains more
information](https://flask.palletsprojects.com/en/1.1.x/deploying/)
on how to do it with the most common web servers (Apache, Ngix, etc).
