# Mixed Beverages

This map helps explore the mixed beverage gross receipts taxes collected by the
[Texas Comptroller](https://comptroller.texas.gov/taxes/mixed-beverage/sales.php)

## Data

A great overview and introduction to the data: https://data.texas.gov/stories/s/tj7s-7tc8

You can export the raw data at:
https://data.texas.gov/Government-and-Taxes/Mixed-Beverage-Gross-Receipts/naix-2893

### Importing Data

To import the latest data from Texas:

```bash
make import  # Downloads, sorts, imports, and processes data (~1.5 hours)
```

Or run steps individually:
```bash
make data     # Download and sort CSV (~15 minutes)
make slurp    # Import into database (~5-10 minutes with bulk insert)
make process  # Generate statistics (~1.5 hours)
```

#### Data Deduplication

The source data contains duplicate entries where the same TABC permit and date appear multiple times with different location names. This typically occurs with temporary permits (TB) where:
- One entry represents the permanent venue (e.g., "Randy's Cafe")
- Another entry represents the temporary event (e.g., "Courtney Wedding Reception")

**Import Strategy:**
- We keep the entry with the **lowest location_number**, which represents the permanent venue
- This ensures consistent location data for mapping and analysis
- Example: For TB015938 on 2007-10-31:
  - Location #1: "Randy's Cafe" (venue) → **KEPT**
  - Location #3: "Courtney Wedding Reception" (event) → DROPPED

This deduplication happens during the `slurp` command and respects the `unique_together = ("tabc_permit", "date")` constraint in the Receipt model.

## Setting up the project

### OSX

    brew install gdal

### Installing

    # install requirements
    make install

Setup your environment:

    DJANGO_SETTINGS_MODULE=mixed_beverages.settings
    DEBUG=1
