#!/bin/bash

mc ls -r sg/sg-c19-response/social-distancing/v2/ > _objects.txt
tail -n 1 _objects.txt

python3 python/migration.py > update.txt
tail -n 1 update.txt

for f in $(cat update.txt)
do
    echo "Pulling $f"
    NAME=$(basename $f)
    DATE=$(echo $NAME | cut -c1-10)
    mkdir -p tmp && (

        cd tmp

        mc cp sg/sg-c19-response/social-distancing/v2/$f $NAME

        # Load to postgres
        psql $ENGINE -c "
            DROP TABLE IF EXISTS public.\"$DATE\";
            CREATE TABLE public.\"$DATE\" (
            origin_census_block_group text,
            date_range_start timestamp,
            date_range_end timestamp,
            device_count integer,
            distance_traveled_from_home text,
            bucketed_distance_traveled text,
            median_dwell_at_bucketed_distance_traveled text,
            completely_home_device_count text,
            median_home_dwell_time text,
            bucketed_home_dwell_time text,
            at_home_by_each_hour text,
            part_time_work_behavior_devices text,
            full_time_work_behavior_devices text,
            destination_cbgs json,
            delivery_behavior_devices text,
            median_non_home_dwell_time text,
            candidate_device_count integer,
            bucketed_away_from_home_time text,
            median_percentage_time_home text,
            bucketed_percentage_time_home text,
            mean_home_dwell_time text,
            mean_non_home_dwell_time text,
            mean_distance_traveled_from_home text
        );"

        psql $ENGINE -c "\copy public.\"$DATE\" FROM PROGRAM 'gzip -dc $NAME' DELIMITER ',' CSV HEADER NULL '' QUOTE '\"'"

        # Inflow
        psql $ENGINE -c "\COPY (
                WITH 
                matrix as (
                    SELECT 
                        LEFT(origin_census_block_group, 2) as origin_state, 
                        (CASE WHEN
                                LEFT(origin_census_block_group, 5) in (
                                        '34023', '34025', '34029', '34035', '36059', 
                                        '34003', '34017', '34031', '36079', '36103',
                                        '36087', '36119', '34013', '34019', '34027', 
                                        '34037', '34039', '42103') 
                                THEN 'MSA'
                                ELSE NULL END) as msa,
                        desti.key as cbg,
                        LEFT(desti.key, 5) as desti_county,
                        desti.value::numeric/candidate_device_count as normalized_counts
                    FROM public.\"$DATE\", json_each_text(destination_cbgs) as desti
                    WHERE LEFT(desti.key, 5) in ('36005', '36061', '36081', '36047', '36085')
                ),
                STATE as (
                    SELECT
                        'STATE' as boundary_level, 
                        origin_state as boundary, 
                        desti_county, 
                        sum(normalized_counts) as normalized_counts
                    FROM matrix
                    group by origin_state, desti_county
                ),
                MSA as (
                    SELECT
                        'MSA' as boundary_level, 
                        msa as boundary, 
                        desti_county, 
                        sum(normalized_counts) as normalized_counts
                    FROM matrix
                    WHERE msa = 'MSA'
                    group by msa, desti_county
                )
                SELECT '$DATE' as date, * FROM state
                UNION SELECT '$DATE' as date, * FROM msa
                ) TO STDOUT DELIMITER ',' CSV HEADER;" > $DATE-in.csv
        tail -n +2  $DATE-in.csv >> ../data/inflow.csv

        # Outflow
        psql $ENGINE -c "\COPY (
                WITH Matrix as (
                    select 
                        LEFT(origin_census_block_group, 5) as county,  
                        desti.key as cbg,
                        LEFT(desti.key, 2) as state,
                        (CASE WHEN
                            LEFT(desti.key, 5) in (
                                    '34023', '34025', '34029', '34035', '36059', 
                                    '34003', '34017', '34031', '36079', '36103',
                                    '36087', '36119', '34013', '34019', '34027', 
                                    '34037', '34039', '42103') 
                            THEN 'MSA'
                            ELSE NULL END) as msa,
                        desti.value::numeric/candidate_device_count as normalized_counts
                    from public.\"$DATE\", json_each_text(destination_cbgs) as desti
                    where left(origin_census_block_group, 5) in (
                            '36005', '36061', '36081', '36047', '36085'
                        )
                ),
                state as (
                    SELECT 
                        county as origin_county,
                        'STATE' as boundary_level,
                        state as boundary,
                        sum(normalized_counts) as normalized_counts
                    FROM Matrix
                    GROUP BY county, state
                ),
                msa as (
                    SELECT 
                        county as origin_county,
                        'MSA' as boundary_level,
                        msa as boundary,
                        sum(normalized_counts) as normalized_counts
                    FROM (SELECT * FROM Matrix WHERE msa = 'MSA') a
                    GROUP BY county, msa
                )
                SELECT '$DATE' as date, * FROM state
                UNION SELECT '$DATE' as date, * FROM msa
                ) TO STDOUT DELIMITER ',' CSV HEADER;" > $DATE-out.csv
        tail -n +2  $DATE-out.csv >> ../data/outflow.csv
    )
    rm -rf tmp
done

rm update.txt
rm _objects.txt

echo "
[$(date)] safegraph auto update
$(cat update.txt)
$(wc -l ../data/inflow.csv) 
$(wc -l ../data/outflow.csv)
" >> CHANGE.txt

