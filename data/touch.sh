#!/bin/bash
#
# Sets the modified time for data files to their timestamp (instead of when
# they were downloaded)
#
# Useful since alphabetical order isn't the same as chronological

for f in *.CSV; do
  year=${f:12:4}
  month=${f:9:2}
  touch -t ${year}${month}010000 ${f}
done
