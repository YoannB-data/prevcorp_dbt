select
    segment_id,
    segment_name
from {{ ref('stg_prevcorp__segments') }}
