Mixed Beverages
===============

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
Then:

    make import

