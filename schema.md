# Schéma de données PrevCorp

Dataset synthétique d'une compagnie d'assurance prévoyance collective fictive.  
Généré avec Faker + logique métier custom. Aucune donnée réelle.

---

## Hiérarchie des entités principales

```
raw_segments       1 ──── n  raw_contracts
raw_contracts      n ──── n  raw_companies        (via raw_contract_companies)
raw_companies      1 ──── n  raw_policyholders
raw_policyholders  1 ──── n  raw_claims
raw_claims         1 ──── n  raw_payments
raw_claims         1 ──── n  raw_resources
raw_claims         1 ──── n  raw_beneficiaries
raw_contracts      1 ──── n  raw_premiums
```

---

## Tables seeds (raw_*)

### raw_segments

| Colonne | Type | Description |
|---|---|---|
| SEGMENT_ID | VARCHAR | PK |
| NOM_SEGMENT | VARCHAR | Ex: `Boucherie artisanale`, `Enseignement privé` |

---

### raw_contracts

| Colonne | Type | Description |
|---|---|---|
| CONTRACT_ID | VARCHAR | PK |
| NUM_CONTRAT | VARCHAR | Numéro de contrat fictif |
| SEGMENT_ID | VARCHAR | FK → raw_segments |
| TYP_CONTRAT | VARCHAR | `CADRE` / `NON CADRE` / `ENSEMBLE DU PERSONNEL` |
| DT_ADHESION | DATE | Date d'effet du contrat |
| DT_RESILIATION | DATE | NULL si en cours |

---

### raw_companies

| Colonne | Type | Description |
|---|---|---|
| COMPANY_ID | VARCHAR | PK |
| SIRET | VARCHAR | SIRET fictif (14 chiffres) |
| NOM_ENTREPRISE | VARCHAR | Nom fictif |
| DT_DEBUT | DATE | Date d'entrée en portefeuille |
| DT_FIN | DATE | NULL si active |

---

### raw_contract_companies
Table de liaison contrats ↔ entreprises (relation n-n).  
Distribution : 80% des contrats couvrent 1 entreprise, 15% en couvrent 2, 5% en couvrent 3.

Combinaisons valides par entreprise : `CADRE seul` / `NON CADRE seul` / `ENSEMBLE DU PERSONNEL seul` / `CADRE + NON CADRE`. La combinaison `ENSEMBLE DU PERSONNEL + autre` est interdite.

| Colonne | Type | Description |
|---|---|---|
| CONTRACT_ID | VARCHAR | FK → raw_contracts |
| COMPANY_ID | VARCHAR | FK → raw_companies |

---

### raw_policyholders
Le lien avec les contrats et entreprises se fait via raw_claims.

| Colonne | Type | Description |
|---|---|---|
| POLICYHOLDER_ID | VARCHAR | PK |
| NOM | VARCHAR | Nom fictif |
| PRENOM | VARCHAR | Prénom fictif |
| DT_NAISSANCE | DATE | |
| ADRESSE | VARCHAR | Adresse fictive |
| COD_PAYS | VARCHAR | Code ISO pays résidence (ex: `FR`, `DE`, `MA`) |
| ATTEST_FISC_ETR | BOOLEAN | Attestation fiscale pays étranger reçue |

---

### raw_claims

| Colonne | Type | Description |
|---|---|---|
| CLAIM_ID | VARCHAR | PK |
| NUM_DOS | VARCHAR | Numéro de dossier fictif |
| POLICYHOLDER_ID | VARCHAR | FK → raw_policyholders |
| CONTRACT_ID | VARCHAR | FK → raw_contracts |
| COMPANY_ID | VARCHAR | FK → raw_companies |
| COD_RISQUE | VARCHAR | `Incapacité` / `Invalidité` / `Décès` / `Rente viagère` / `Rente éducation` |
| NAT_ARRET | VARCHAR | `Maladie` / `Accident travail` / `Accident de trajet` / `Maladie Professionnelle` / `Maternité` |
| DT_CREATION | DATE | Date d'ouverture du dossier |
| DT_FAIT_GEN | DATE | Date du sinistre initial (fait générateur) |
| SALAIRE_REF | DECIMAL | Salaire de référence pour calcul des prestations |
| DT_ETAT_DOS | DATE | Date de dernière mise à jour du statut |
| MOTIF_ETAT_DOS | VARCHAR | NULL si dossier en cours — `SANS SUITE` / `RETRAITE` / `REPRISE TRAVAIL` / `DECEDE` si clos |
| DT_ATTEST_NA | DATE | Date réception attestation de non-activité — NULL si non reçue |
| DT_JUSTIF_SS | DATE | Date réception justificatif SS — NULL si non reçu |

---

### raw_payments
Règles métier par type de risque :
- **Incapacité** : paiement tous les 15 jours, entre 60% et 100% du SALAIRE_REF. Montant stable, changement rare (~5%) si situation du salarié évolue.
- **Invalidité** : paiement fin de mois. Montant = SALAIRE_REF - ressources du salarié. Ne peut pas dépasser le salaire (contrainte légale).
- **Rente viagère / Rente éducation** : paiement fin de mois, montant fixe entre 20% et 60% du SALAIRE_REF.
- **Décès** : paiement unique, montant entre 30 000 et 800 000 (moyenne ~75 000).


| Colonne | Type | Description |
|---|---|---|
| PAYMENT_ID | VARCHAR | PK |
| CLAIM_ID | VARCHAR | FK → raw_claims |
| MNT_BRUT | DECIMAL | Montant brut versé |
| MNT_NET | DECIMAL | Montant net versé |
| MNT_PAS | DECIMAL | Montant Prélèvement à la Source |
| DT_PAIEMENT | DATE | Date de paiement |

---

### raw_premiums
Règles métier :
- Cotisations trimestrielles. `ECHEANCE_DATE` = premier jour du trimestre concerné (01/01, 01/04, 01/07, 01/10).
- `DT_ENCAISSEMENT` = environ 3 mois après `ECHEANCE_DATE`.
- Montant de base stable par contrat, avec revalorisation annuelle au 1er janvier (0% à 15%).
- Si revalorisation > 12% : résiliation du contrat probable dans l'année.
- Double paiement (~8% des cas) : un trimestre est sauté, le suivant contient le double du montant habituel.
- ~5% de trimestres manquants (impayés).


| Colonne | Type | Description |
|---|---|---|
| PREMIUM_ID | VARCHAR | PK |
| CONTRACT_ID | VARCHAR | FK → raw_contracts |
| MNT_COTISATION | DECIMAL | Montant de la cotisation |
| DT_ENCAISSEMENT | DATE | Date d'encaissement (environ 3 mois après ECHEANCE_DATE) |
| ECHEANCE_DATE | DATE | Premier jour du trimestre concerné (ex: 01/01, 01/04, 01/07, 01/10) |

---

### raw_resources
Uniquement pour les dossiers `COD_RISQUE = 'Invalidité'` — l'assurance vient en complément des ressources existantes.


| Colonne | Type | Description |
|---|---|---|
| RESOURCE_ID | VARCHAR | PK |
| CLAIM_ID | VARCHAR | FK → raw_claims |
| TYP_RESSOURCE | VARCHAR | `PE` / `Salaire` / `Rente SS` / `Autre` |
| MONTANT | DECIMAL | Montant mensuel |
| DT_DEBUT | DATE | Début de perception |
| DT_FIN | DATE | NULL si en cours |

---

### raw_beneficiaries
Uniquement pour les dossiers `COD_RISQUE = 'Rente viagère'` ou `COD_RISQUE = 'Rente éducation'` (rentes DC). Dans raw_claims, le champ NOM du défunt est l'assuré lui-même.


| Colonne | Type | Description |
|---|---|---|
| BENEFICIARY_ID | VARCHAR | PK |
| CLAIM_ID | VARCHAR | FK → raw_claims |
| NOM | VARCHAR | Nom fictif |
| PRENOM | VARCHAR | Prénom fictif |
| DT_NAISSANCE | DATE | Calcul majorité rentes éducation (18 ans) |

---

## Modèles dbt

```
seeds/
├── raw_segments.csv
├── raw_contracts.csv
├── raw_companies.csv
├── raw_contract_companies.csv
├── raw_policyholders.csv
├── raw_claims.csv
├── raw_payments.csv
├── raw_premiums.csv
├── raw_resources.csv
└── raw_beneficiaries.csv

models/
├── staging/
│   ├── stg_prevcorp__segments.sql
│   ├── stg_prevcorp__contrats.sql
│   ├── stg_prevcorp__entreprises.sql
│   ├── stg_prevcorp__contrats_entreprises.sql
│   ├── stg_prevcorp__assures.sql
│   ├── stg_prevcorp__dossiers.sql
│   ├── stg_prevcorp__paiements.sql
│   ├── stg_prevcorp__cotisations.sql
│   ├── stg_prevcorp__ressources.sql
│   └── stg_prevcorp__beneficiaires.sql
├── intermediate/
│   ├── int__dossiers_enrichis.sql
│   ├── int__contrats_enrichis.sql
│   ├── int__paiements_enrichis.sql
│   └── int__cotisations_enrichies.sql
└── marts/
    ├── dim__segments.sql
    ├── dim__entreprises.sql
    ├── dim__contrats.sql
    ├── dim__assures.sql
    ├── dim__beneficiaires.sql
    ├── fct__dossiers.sql
    ├── fct__paiements.sql
    ├── fct__cotisations.sql
    └── fct__ressources.sql
```

---

## Volumes cibles

| Table | Volume cible | Note |
|---|---|---|
| raw_segments | ~10 | |
| raw_contracts | ~500 | Multi-contrats par segment |
| raw_companies | ~500 | |
| raw_contract_companies | ~600 | Distribution 80/15/5 |
| raw_policyholders | ~2 000 | ~4 assurés par entreprise || raw_claims | ~1 500 | |
| raw_payments | ~50 000 | Historique 36 mois |
| raw_premiums | ~24 000 | 4 trimestres × 36 mois / 3 × 500 contrats — ~5% de trimestres manquants (impayés) |
| raw_resources | ~1 000 | |
| raw_beneficiaries | ~100 | |

---

## Décisions d'architecture (ADR)

| Décision | Choix | Raison |
|---|---|---|
| Nommage seeds en MAJUSCULES | Convention volontaire | Simule un export brut de progiciel de gestion |
| Normalisation des noms de champs | Couche staging | La valeur ajoutée du staging est précisément cette transformation |
| Langue des colonnes | Français | Cohérence avec les valeurs métier, la documentation et les utilisateurs. Choix délibéré, pas une méconnaissance des conventions dbt. |
| Convention de nommage | `entite_attribut` (ex: `contrat_type`) | Lisibilité — on sait immédiatement à quelle entité appartient une colonne |
| Double underscore `int__`, `dim__`, `fct__` | Alignement sur `stg_prevcorp__` | Cohérence visuelle entre toutes les couches |
| `COMPANY_ID` dans raw_claims | Dénormalisation intentionnelle | Simule la réalité d'un SI de gestion |
| `raw_contract_companies` junction table | Table de liaison dédiée | Relation n-n contrats ↔ entreprises |
| `raw_policyholders` sans FK entreprise | Lien via raw_claims | Un assuré peut exister sans dossier actif (~5% du dataset) |
| Langue des colonnes | Français | Cohérence avec les valeurs métier, la documentation et les utilisateurs. Choix délibéré, pas une méconnaissance des conventions dbt.

---

*Dernière mise à jour : Phase 0 — schéma v3*
