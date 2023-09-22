# geotaste
Code, notebooks and resources for a "Geography of Taste" in the Shakespeare &amp; Co. Project Dataset


[![Documentation Status](https://readthedocs.org/projects/geotaste/badge/?version=latest)](https://geotaste.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://codecov.io/gh/Princeton-CDH/geotaste/branch/main/graph/badge.svg)](https://codecov.io/gh/Princeton-CDH/ppa-django)
[![Unit test status](https://github.com/Princeton-CDH/geotaste/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/Princeton-CDH/geotaste/actions/workflows/unit-tests.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/princeton-cdh/geotaste/badge)](https://www.codefactor.io/repository/github/geotaste/ppa-django)

Python 3.10 / Dash 2.13 / Plotly 5.17 / Flask 2.2

## Installation

```bash
# 0. Clone repo
git clone https://github.com/Princeton-CDH/geotaste
cd geotaste

# 1. Install pyenv if necessary
curl https://pyenv.run | bash

# 2. Make python env
vnum=$(cat .python-version)
pyenv install $vnum
pyenv shell $vnum
python -m venv venv

# 3. Activate python env
. venv/bin/activate
pip install -qU pip wheel

# 4. Install
pip install -e .

# 5. Run locally
geotaste-app

# 6. Navigate to localhost:1919
```


## Testing

```bash
# install requirements to develop/test
pip install -r dev-requirements.txt

# install chromedriver
brew install --cask chromedriver    # on mac
# for linux see: https://gist.github.com/mikesmullin/2636776?permalink_comment_id=2986509#gistcomment-2986509
# for windows see: https://medium.com/@patrick.yoho11/installing-selenium-and-chromedriver-on-windows-e02202ac2b08

# run pytest
pytest --headless --cov
```

## Documentation

See [full code documentation here](https://geotaste.readthedocs.io/en/latest). To generate documentation locally using [sphinx](http://www.sphinx-doc.org/):

```bash
# install requirements to develop/test
pip install -r dev-requirements.txt

# generate html
cd sphinx-docs
make html

# check coverage
make html -b coverage
```

