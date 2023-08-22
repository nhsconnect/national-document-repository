# national-document-repository

## Setup
This project will be using Python 3.11. Install this on your machine from https://www.python.org/downloads/

Alternatively, you can set up `pyenv` to handle multiple Python versions:

### Mac/Linux
https://github.com/pyenv/pyenv

### Windows
https://github.com/pyenv-win/pyenv-win


### Virtual Environment

To setup the Python environment for backend development, run: `make env`

This will create a virtual environment with all production and test requirements. The virtual environment can be found at `.lambdas/venv`.

To activate the environment run `source ./lambdas/venv/bin/activate`

## Package
To create a deployable zip package for the AWS lambdas, run: `make package` 

This will install production dependancies and copy our files into to `lambdas/package`.  This folder will then be zipped as `lambdas/package/lambdas.zip` and ready to deploy to AWS either manually or through github actions.