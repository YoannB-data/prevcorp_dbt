select
    claim_id as dossier_id,
    num_dos as dossier_numero,
    policyholder_id as assure_id,
    contract_id as contrat_id,
    company_id as entreprise_id,
    cod_risque as risque,
    nullif(nat_arret, '') as nature_arret,
    cast(dt_creation as date) as creation_date,
    cast(dt_fait_gen as date) as fait_generateur_date,
    cast(salaire_ref as decimal) as salaire_montant,
    cast(dt_etat_dos as date) as etat_date,
    nullif(motif_etat_dos, '') as etat_motif,
    dt_attest_na as attest_non_activite_date,
    dt_justif_ss as justif_ss_date,
    case
        when motif_etat_dos is null or motif_etat_dos = '' then true
        else false
    end as est_en_cours
    
from {{ ref('raw_claims') }}
