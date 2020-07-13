#!/bin/bash

# Compute diff
mc ls -r sg/sg-c19-response/social-distancing/v2/ > _objects.txt
python3 python/nta.py > update.txt

# Import NTA Location table
psql $ENGINE -c "
    CREATE TABLE nta_latlon (
        nta text,
        lat double precision,
        lon double precision
    );
"
cat ../data/nta_latlon.csv | psql $ENGINE -c "COPY nta_latlon FROM STDIN DELIMITER ',' CSV HEADER;"

psql $ENGINE -c "
    CREATE TABLE ct_nta (
        boroct text,
        nta text,
        lat double precision,
        lon double precision
    );
"
cat ../data/ct_nta.csv | psql $ENGINE -c "COPY ct_nta FROM STDIN DELIMITER ',' CSV HEADER;"

# ETL
if [ -s update.txt ]
then 

for f in $(cat update.txt)
do
    echo "Pulling $f"
    NAME=$(basename $f)
    DATE=$(echo $NAME | cut -c1-10)
    mkdir -p tmp && (
        cd tmp
        mc cp sg/sg-c19-response/social-distancing/v2/$f $NAME
        psql $ENGINE -v DATE=$DATE -f ../sql/create.sql
        psql $ENGINE -c "\copy public.\"$DATE\" FROM PROGRAM 'gzip -dc $NAME' DELIMITER ',' CSV HEADER NULL '' QUOTE '\"'"
        psql $ENGINE -v DATE=$DATE -f ../sql/nta.sql >> ../../data/nta_outflow.csv
        psql $ENGINE -c "DROP TABLE IF EXISTS public.\"$DATE\";"
    )
    rm -rf tmp
done
    
echo "
[$(date)] safegraph NTA auto update
$(cat update.txt)
$(wc -l ../data/nta_outflow.csv)
" >> CHANGE.txt
    rm update.txt
    rm _objects.txt

else

echo "
[$(date)] safegraph NTA no change, skipping ...
" >> CHANGE.txt
rm update.txt
rm _objects.txt

fi
