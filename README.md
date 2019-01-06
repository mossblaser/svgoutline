svgoutline
==========

A library which converts SVG graphics a set of simple line and curve segments.
This tools is intended to be used as a back-end for driving pen plotters or
desk-top cutting machines.

Tests
-----

The tests are written using [py.test](https://docs.pytest.org/en/latest/) and
test dependencies can be installed an the tests executed with:

    $ pip install -r requirements-test.txt
    $ py.test tests

The code adheres to the Python [PEP8 style
guide](https://www.python.org/dev/peps/pep-0008/) and is checked using
[flake8](http://flake8.pycqa.org/en/latest/) (installed with py.test in the
commands above). Run it using:

    $ flake8 tests svgoutline
