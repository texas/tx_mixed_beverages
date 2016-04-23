Mixed Beverages
===============

[![Build Status](https://travis-ci.org/texas/tx_mixed_beverages.svg?branch=master)](https://travis-ci.org/texas/tx_mixed_beverages)

Data
----

* http://www.window.state.tx.us/taxinfo/taxfiles.html
* http://www.window.state.tx.us/taxinfo/mixbev/
* http://www.texastransparency.org/Data_Center/Search_Datasets.php


Setting up the project
----------------------

Install requirements:

    pip install -r requirements.txt
    npm install

Setup your Python path:

    add2virtualenv .

Setup your environment:

    DJANGO_SETTINGS_MODULE=mixed_beverages.settings
    DEBUG=1

#### Pull data

First, you have to get the [csvs](http://www.texastransparency.org/Data_Center/Search_Datasets.php).

Sometimes, the csvs there are out of date. You can find some of them at
http://www.window.state.tx.us/taxinfo/taxfiles.html too, albeit with different
file names.

Then:

    make import
