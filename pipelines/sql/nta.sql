CREATE TEMP TABLE tmp as (
    WITH 
    ct as (
        SELECT 
            (CASE 
                WHEN left(origin_census_block_group, 5) = '36061' THEN '1' --mn
                WHEN left(origin_census_block_group, 5) = '36005' THEN '2' --bx
                WHEN left(origin_census_block_group, 5) = '36047' THEN '3' --bk
                WHEN left(origin_census_block_group, 5) = '36081' THEN '4' --qn
                WHEN left(origin_census_block_group, 5) = '36085' THEN '5' --si
            END) || left(right(origin_census_block_group, 7),6) as origin_boroct,
            (CASE 
                WHEN left(desti.key, 5) = '36061' THEN '1' --mn
                WHEN left(desti.key, 5) = '36005' THEN '2' --bx
                WHEN left(desti.key, 5) = '36047' THEN '3' --bk
                WHEN left(desti.key, 5) = '36081' THEN '4' --qn
                WHEN left(desti.key, 5) = '36085' THEN '5' --si
            END) || left(right(desti.key, 7),6) as desti_boroct,
            round(desti.value::numeric/candidate_device_count, 4) as normalized_counts
        FROM public.:"DATE", json_each_text(destination_cbgs) as desti
        WHERE LEFT(desti.key, 5) in ('36005', '36061', '36081', '36047', '36085')
        and  LEFT(origin_census_block_group, 5) in ('36005', '36061', '36081', '36047', '36085')
    ),
    NTA_ori as (
        SELECT
            a.origin_boroct,
            a.desti_boroct,
            b.nta as origin_nta,
            a.normalized_counts
        FROM ct a
        LEFT JOIN ct_nta b
        ON a.origin_boroct = b.boroct
    ),
    NTA_desti as (
        SELECT
            a.origin_boroct,
            a.desti_boroct,
            a.origin_nta,
            b.nta as desti_nta,
            a.normalized_counts
        FROM NTA_ori a
        LEFT JOIN ct_nta b
        ON a.desti_boroct = b.boroct
    ),
    grouped as (
        SELECT 
            origin_nta, 
            desti_nta, 
            sum(normalized_counts) as normalized_counts
        FROM NTA_desti
        WHERE origin_nta != desti_nta
        GROUP BY origin_nta, desti_nta
    )
    select
        :'DATE'::timestamp as date,
        origin_nta, 
        desti_nta, 
        normalized_counts,
        (select lat from nta_latlon where nta = a.origin_nta) as origin_lat,
        (select lon from nta_latlon where nta = a.origin_nta) as origin_lon,
        (select lat from nta_latlon where nta = a.desti_nta) as desti_lat,
        (select lon from nta_latlon where nta = a.desti_nta) as desti_lon
    FROM grouped a
    ORDER BY normalized_counts desc LIMIT 1500
);

\COPY tmp TO PSTDOUT DELIMITER ',' CSV;