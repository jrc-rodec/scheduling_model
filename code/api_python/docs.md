# Benchmark Rewriter

## Local usage

Change directory: `cd code\api_python`

### Install dependencies

Create a text file named requirements.txt with following content:

{
setuptools
wheel
twine
pytest
pytest-runner
}

`pip install -r requirements.txt`

### Build library

`python setup.py bdist_wheel`

### Run tests (optional)

`pytest tests/tests.py`

### Install library

Adjust path to whl-File (in dist-folder)

`pip install "dist\benchmarkrewriter-0.1-py3-none-any.whl"`

### Use library

The library can be imported like `import benchmarkrewriter`

For later:

## Publish to PyPI

`twine upload dist/\*`
`pip install benchmarkrewriter`
