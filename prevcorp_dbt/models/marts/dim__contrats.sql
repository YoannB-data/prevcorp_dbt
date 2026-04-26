select
    contrat_id,
    contrat_numero,
    contrat_type,
    segment_nom,
    debut_date,
    fin_date,
    est_en_cours,
    entreprise_nombre
    
from {{ ref('int__contrats_enrichis') }}
