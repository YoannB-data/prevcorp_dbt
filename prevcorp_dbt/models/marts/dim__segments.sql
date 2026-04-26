select
    segment_id,
    segment_nom
from {{ ref('stg_prevcorp__segments') }}
