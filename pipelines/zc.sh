#!/bin/bash

python3 python/zc.py
DATE=$(date)
echo "
[$DATE] zipcode level auto update
$(wc -l ../data/modzcta.csv)
" >> CHANGE.txt