# Mixed Beverages

[![Build Status](https://travis-ci.org/texas/tx_mixed_beverages.svg?branch=master)](https://travis-ci.org/texas/tx_mixed_beverages)

## Data

A great overview and introduction to the data: https://data.texas.gov/stories/s/tj7s-7tc8

You can export the raw data at:
https://data.texas.gov/Government-and-Taxes/Mixed-Beverage-Gross-Receipts/naix-2893

## Setting up the project

### OSX

    brew install gdal

### Installing

    # install requirements
    make install

Setup your environment:

    DJANGO_SETTINGS_MODULE=mixed_beverages.settings
    DEBUG=1

#### Pull data

**NOTE:** The data format and process has changed so this is out of date

First, you have to get the [csvs](https://www.comptroller.texas.gov/transparency/open-data/search-datasets/).

Then:

    make import
