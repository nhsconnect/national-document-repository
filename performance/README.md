# National Document Repository: Performance

This part of the repository contains the performance tests and setup required these include...

- bulk_upload
- tests

## Prerequisite

This project will be using Python 3.11. Install this on your machine from <https://www.python.org/downloads/>

Alternatively, you can set up `pyenv` to handle multiple Python versions:

### Mac/Linux

<https://github.com/pyenv/pyenv>

### Windows

<https://github.com/pyenv-win/pyenv-win>

## Virtual Environment

To setup the Python environment for backend development, run: `make env`

This will create a virtual environment with all production and test requirements. The virtual environment can be found
at `./performance/tests/performance-venv`.

To activate the environment in Mac/Linux or UNIX based Windows terminal, run:
`source ./performance/tests/performance-env/bin/activate`

`./performance/tests/performance-env/Scripts/activate`

To activate in Windows terminals, run:

`./performance/tests/performance-env/Scripts/activate`

## Locust Setup

You will need to install the requirements for performance tests for Linux user this can be done using the command for `make performance-env`

Upon completion to run the locust tests navigate to the ./performance/tests directory and run the command `locust`
