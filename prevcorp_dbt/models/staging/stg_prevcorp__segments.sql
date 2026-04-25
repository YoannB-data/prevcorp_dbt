select
    segment_id,
    nom_segment as segment_name
from {{ ref('raw_segments') }}
