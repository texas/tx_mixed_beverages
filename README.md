# Mixed Beverages

This map helps explore the mixed beverage gross receipts taxes collected by the
[Texas Comptroller](https://comptroller.texas.gov/taxes/mixed-beverage/sales.php)

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
