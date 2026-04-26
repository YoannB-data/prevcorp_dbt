select
    segment_id,
    nom_segment as segment_nom
    
from {{ ref('raw_segments') }}
