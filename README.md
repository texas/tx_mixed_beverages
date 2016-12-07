Mixed Beverages
===============

[![Build Status](https://travis-ci.org/texas/tx_mixed_beverages.svg?branch=master)](https://travis-ci.org/texas/tx_mixed_beverages)

Data
----

* https://www.comptroller.texas.gov/transparency/open-data/search-datasets/


Setting up the project
----------------------

In a Python 3 virtualenv:

    # install requirements
    make install
    # add base dir to your Python path
    add2virtualenv .

Setup your environment:

    DJANGO_SETTINGS_MODULE=mixed_beverages.settings
    DEBUG=1

#### Pull data

First, you have to get the [csvs](https://www.comptroller.texas.gov/transparency/open-data/search-datasets/).

Then:

    make import
