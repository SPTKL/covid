DROP TABLE IF EXISTS public.:"DATE";
CREATE TABLE public.:"DATE" (
    origin_census_block_group text,
    date_range_start timestamp without time zone,
    date_range_end timestamp without time zone,
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
    bucketed_percentage_time_home text
);