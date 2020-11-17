"""Command line interface for the web server.

Run the :py:func:`main` function to start the web server. Executing this
module will also execute :py:func:`main` automatically.
"""
import sys


def main():
    print("Hello World")
    return 0


if __name__ == "__main__":
    sys.exit(main())
