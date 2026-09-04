# Data Dictionary

## sample_observations.csv

`observation_id` unique record key; `observed_at` observation date; `species_common_name` observed species; `species_category` category such as Birds/Insects/Plants; `habitat_type` observation habitat; `observer_id` local pseudonymous contributor key; `latitude` and `longitude` coordinates; `image_count` linked image count; `abundance_count` observed count; `season` seasonal label; `habitat_quality_score` 0–100 observed habitat quality; `human_disturbance_score` 0–100 disturbance signal; `species_confidence_pct` 0–100 observation confidence.

## sample_habitats.csv

`habitat_id` unique habitat key; `habitat_name` display name; `habitat_type` habitat class; `zone` local area label; `area_hectares` area; `native_plant_pct` native plant share; `canopy_cover_pct` canopy coverage; `water_availability_score` 0–100 water availability; `fragmentation_score` 0–100 fragmentation pressure; `disturbance_score` 0–100 disturbance pressure; `seasonal_stability_score` 0–100 seasonal stability.
