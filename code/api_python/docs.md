# Benchmark Rewriter

Change directory: `cd code\api_python`

## Install dependencies

`pip install -r requirements.txt`

Necessary dependencies:

(
setuptools
wheel
twine
pytest
pytest-runner
)

## Build library

`python setup.py bdist_wheel`

## Run test

`pytest tests/tests.py`

## Install library

`pip install "C:\Users\Bianca\OneDrive - FH Vorarlberg\JRZ\JRZ\Scheduling\scheduling_model\code\api_python\dist\benchmarkrewriter-0.1-py3-none-any.whl"`

## Use library

The library can be imported like `import benchmarkrewriter`

For later:

## Publish to PyPI

`twine upload dist/\*`
`pip install benchmarkrewriter`