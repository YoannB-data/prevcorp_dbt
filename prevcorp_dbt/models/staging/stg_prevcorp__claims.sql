select
    claim_id,
    num_dos                                  as claim_number,
    policyholder_id,
    contract_id,
    company_id,
    cod_risque                               as risk_type,
    nullif(nat_arret, '')                    as leave_type,
    cast(dt_creation as date)               as created_date,
    cast(dt_fait_gen as date)               as event_date,
    cast(salaire_ref as decimal)             as salary_amount,
    cast(dt_etat_dos as date)               as status_date,
    nullif(motif_etat_dos, '')               as status_reason,
    cast(nullif(dt_attest_na, '') as date)  as non_activity_certificate_date,
    cast(nullif(dt_justif_ss, '') as date)  as ss_certificate_date,
    case
        when motif_etat_dos is null or motif_etat_dos = '' then true
        else false
    end                                      as is_open
from {{ ref('raw_claims') }}
