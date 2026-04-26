select
    contract_id as contrat_id,
    num_contrat as contrat_numero,
    segment_id,
    typ_contrat as contrat_type,
    dt_adhesion as debut_date,
    dt_resiliation as fin_date,
    (dt_resiliation is null) as est_en_cours
    
from {{ ref('raw_contracts') }}
