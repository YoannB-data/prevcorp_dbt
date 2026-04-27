"""
generate.py — Générateur de dataset synthétique PrevCorp
Aucune donnée réelle. Toutes les entités sont fictives.
"""

import csv
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

fake = Faker("fr_FR")
random.seed(42)
Faker.seed(42)

OUTPUT_DIR = Path("seeds")
OUTPUT_DIR.mkdir(exist_ok=True)

START_DATE = date(2022, 1, 1)
END_DATE = date(2025, 12, 31)


# ─────────────────────────────────────────────
# Utilitaires
# ─────────────────────────────────────────────


def uid() -> str:
    """Génère un identifiant unique universel."""
    return str(uuid.uuid4())


def rand_date(start: date, end: date) -> date:
    """Retourne une date aléatoire uniforme entre start et end."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def write_csv(filename: str, rows: list[dict]) -> None:
    """Écrit une liste de dictionnaires dans un fichier CSV dans OUTPUT_DIR."""
    if not rows:
        return
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  {filename:45s} {len(rows):>6} lignes")


def first_day_of_quarter(d: date) -> date:
    """Retourne le premier jour du trimestre calendaire contenant la date d."""
    quarter_start_month = ((d.month - 1) // 3) * 3 + 1
    return date(d.year, quarter_start_month, 1)


def add_months(d: date, months: int) -> date:
    """Ajoute un nombre entier de mois à une date en conservant le jour 1."""
    month = d.month + months
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    return date(year, month, 1)


# ─────────────────────────────────────────────
# 1. raw_segments
# ─────────────────────────────────────────────

SEGMENTS = [
    "Boucherie artisanale",
    "Enseignement privé",
    "Métallurgie",
    "Bâtiment et travaux publics",
    "Commerce de détail",
    "Transport routier",
    "Hôtellerie-restauration",
    "Santé et action sociale",
    "Agriculture",
    "Services aux entreprises",
]


def gen_segments() -> list[dict]:
    """Retourne les 10 segments professionnels fixes."""
    return [
        {"SEGMENT_ID": f"SEG{i+1:03d}", "NOM_SEGMENT": name}
        for i, name in enumerate(SEGMENTS)
    ]


# ─────────────────────────────────────────────
# 2. raw_contracts
# ─────────────────────────────────────────────

TYP_CONTRAT_VALUES = ["CADRE", "NON CADRE", "ENSEMBLE DU PERSONNEL"]
TYP_CONTRAT_WEIGHTS = [0.35, 0.35, 0.30]


def gen_contracts(segments: list[dict], n: int = 500) -> list[dict]:
    """Génère n contrats collectifs rattachés aléatoirement à un segment."""
    rows = []
    for i in range(n):
        seg = random.choice(segments)
        dt_adhesion = rand_date(date(2010, 1, 1), date(2023, 12, 31))
        # ~15% de contrats résiliés
        if random.random() < 0.15:
            dt_resiliation = rand_date(dt_adhesion + timedelta(days=365), END_DATE)
            dt_resiliation_str = dt_resiliation.isoformat()
        else:
            dt_resiliation_str = ""

        rows.append(
            {
                "CONTRACT_ID": f"CTR{i+1:05d}",
                "NUM_CONTRAT": f"C{random.randint(10000, 99999)}",
                "SEGMENT_ID": seg["SEGMENT_ID"],
                "TYP_CONTRAT": random.choices(TYP_CONTRAT_VALUES, TYP_CONTRAT_WEIGHTS)[
                    0
                ],
                "DT_ADHESION": dt_adhesion.isoformat(),
                "DT_RESILIATION": dt_resiliation_str,
            }
        )
    return rows


# ─────────────────────────────────────────────
# 3. raw_companies
# ─────────────────────────────────────────────


def gen_companies(n: int = 500) -> list[dict]:
    """Génère n entreprises adhérentes avec SIRET fictif."""
    rows = []
    for i in range(n):
        dt_debut = rand_date(date(2008, 1, 1), date(2023, 6, 30))
        # ~10% d'entreprises résiliées (DT_FIN renseigné)
        if random.random() < 0.10:
            dt_fin = rand_date(dt_debut + timedelta(days=180), END_DATE)
            dt_fin_str = dt_fin.isoformat()
        else:
            dt_fin_str = ""

        rows.append(
            {
                "COMPANY_ID": f"CMP{i+1:05d}",
                "SIRET": "".join([str(random.randint(0, 9)) for _ in range(14)]),
                "NOM_ENTREPRISE": fake.company(),
                "DT_DEBUT": dt_debut.isoformat(),
                "DT_FIN": dt_fin_str,
            }
        )
    return rows


# ─────────────────────────────────────────────
# 4. raw_contract_companies
# Règle : par entreprise, combinaisons valides :
#   CADRE seul / NON CADRE seul / ENSEMBLE DU PERSONNEL seul / CADRE + NON CADRE
# ─────────────────────────────────────────────


def gen_contract_companies(
    contracts: list[dict],
    companies: list[dict],
) -> list[dict]:
    """Crée les liens contrat-entreprise en respectant les règles de combinaison de types."""
    rows = []

    # Pour chaque contrat : 80% → 1 entreprise, 15% → 2, 5% → 3
    n_companies_weights = [0.80, 0.15, 0.05]
    company_ids = [c["COMPANY_ID"] for c in companies]

    pairs: set[tuple[str, str]] = set()

    for contract in contracts:
        n = random.choices([1, 2, 3], n_companies_weights)[0]
        chosen = random.sample(company_ids, min(n, len(company_ids)))

        # Garantie : au moins une entreprise par contrat
        added = False
        for company_id in chosen:
            existing_types = [
                c["TYP_CONTRAT"]
                for c in contracts
                if (c["CONTRACT_ID"], company_id) in pairs
                or any(
                    r["CONTRACT_ID"] == c["CONTRACT_ID"]
                    and r["COMPANY_ID"] == company_id
                    for r in rows
                )
            ]

            typ = contract["TYP_CONTRAT"]

            # Règle : ENSEMBLE DU PERSONNEL ne se combine avec rien
            if "ENSEMBLE DU PERSONNEL" in existing_types:
                continue
            if typ == "ENSEMBLE DU PERSONNEL" and existing_types:
                continue
            # Règle : pas deux fois le même type pour une même entreprise
            if typ in existing_types:
                continue

            key = (contract["CONTRACT_ID"], company_id)
            if key not in pairs:
                pairs.add(key)
                rows.append(
                    {
                        "CONTRACT_ID": contract["CONTRACT_ID"],
                        "COMPANY_ID": company_id,
                    }
                )
                added = True

        # Si aucune entreprise n'a pu être ajoutée, forcer un lien avec une entreprise aléatoire
        if not added:
            company_id = random.choice(company_ids)
            key = (contract["CONTRACT_ID"], company_id)
            if key not in pairs:
                pairs.add(key)
                rows.append(
                    {
                        "CONTRACT_ID": contract["CONTRACT_ID"],
                        "COMPANY_ID": company_id,
                    }
                )

    return rows


# ─────────────────────────────────────────────
# 5. raw_policyholders
# ~5% orphelins (sans dossier), ~95% auront un claim
# Pas de FK — lien via raw_claims
# ─────────────────────────────────────────────

PAYS_RESIDENCE = ["FR"] * 88 + [
    "BE",
    "DE",
    "ES",
    "IT",
    "PT",
    "CH",
    "MA",
    "TN",
    "DZ",
    "SN",
    "CM",
]


def gen_policyholders(n: int = 2000) -> list[dict]:
    """Génère n assurés avec données civiles et pays de résidence."""
    rows = []
    for i in range(n):
        pays = random.choice(PAYS_RESIDENCE)
        # Attestation fiscale étrangère uniquement si hors FR
        attest = (pays != "FR") and (random.random() < 0.6)

        rows.append(
            {
                "POLICYHOLDER_ID": f"POL{i+1:06d}",
                "NOM": fake.last_name().upper(),
                "PRENOM": fake.first_name(),
                "DT_NAISSANCE": rand_date(
                    date(1950, 1, 1), date(1995, 12, 31)
                ).isoformat(),
                "ADRESSE": fake.address().replace("\n", ", "),
                "COD_PAYS": pays,
                "ATTEST_FISC_ETR": str(attest).upper(),
            }
        )
    return rows


# ─────────────────────────────────────────────
# 6. raw_claims
# ─────────────────────────────────────────────

COD_RISQUE_VALUES = [
    "Incapacité",
    "Invalidité",
    "Décès",
    "Rente viagère",
    "Rente éducation",
]
COD_RISQUE_WEIGHTS = [0.45, 0.25, 0.10, 0.10, 0.10]

# NAT_ARRET pertinent pour Incapacité et Invalidité uniquement
NAT_ARRET_VALUES = [
    "Maladie",
    "Accident travail",
    "Accident de trajet",
    "Maladie Professionnelle",
    "Maternité",
]
NAT_ARRET_WEIGHTS = [0.65, 0.15, 0.08, 0.07, 0.05]

MOTIF_CLOTURE = ["SANS SUITE", "RETRAITE", "REPRISE TRAVAIL", "DECEDE"]


def gen_claims(  # pylint: disable=too-many-locals
    policyholders: list[dict],
    contracts: list[dict],
    contract_companies: list[dict],
) -> list[dict]:
    """Génère les dossiers sinistres pour ~95% des assurés, parfois 2 par assuré."""
    rows = []

    # Index : contract_id → liste de company_ids
    contract_to_companies: dict[str, list[str]] = {}
    for link in contract_companies:
        contract_to_companies.setdefault(link["CONTRACT_ID"], []).append(
            link["COMPANY_ID"]
        )

    # ~95% des assurés ont au moins un dossier
    active_pols = random.sample(policyholders, k=int(len(policyholders) * 0.95))

    claim_counter = 1
    for pol in active_pols:
        # 1 dossier par assuré, parfois 2 (10% des cas)
        n_claims = 2 if random.random() < 0.10 else 1

        for _ in range(n_claims):
            contract = random.choice(contracts)
            companies = contract_to_companies.get(contract["CONTRACT_ID"], [])
            company_id = random.choice(companies) if companies else ""

            cod_risque = random.choices(COD_RISQUE_VALUES, COD_RISQUE_WEIGHTS)[0]

            # NAT_ARRET : pertinent seulement pour Incapacité et Invalidité
            if cod_risque in ("Incapacité", "Invalidité"):
                nat_arret = random.choices(NAT_ARRET_VALUES, NAT_ARRET_WEIGHTS)[0]
            else:
                nat_arret = ""

            dt_creation = rand_date(START_DATE, END_DATE - timedelta(days=30))
            dt_fait_gen = dt_creation - timedelta(days=random.randint(0, 90))
            dt_etat_dos = rand_date(dt_creation, END_DATE)

            # ~40% des dossiers sont clos
            if random.random() < 0.40:
                motif = random.choice(MOTIF_CLOTURE)
            else:
                motif = ""

            # Attestation non-activité et justificatif SS : Invalidité uniquement
            if cod_risque == "Invalidité":
                dt_attest_na = (
                    rand_date(dt_creation, dt_etat_dos).isoformat()
                    if random.random() < 0.70
                    else ""
                )
                dt_justif_ss = (
                    rand_date(dt_creation, dt_etat_dos).isoformat()
                    if random.random() < 0.65
                    else ""
                )
            else:
                dt_attest_na = ""
                dt_justif_ss = ""

            # Salaire de référence : cadre vs non cadre
            typ = contract.get("TYP_CONTRAT", "ENSEMBLE DU PERSONNEL")
            if typ == "CADRE":
                salaire = round(random.uniform(3500, 12000), 2)
            elif typ == "NON CADRE":
                salaire = round(random.uniform(1600, 4000), 2)
            else:
                salaire = round(random.uniform(1600, 8000), 2)

            rows.append(
                {
                    "CLAIM_ID": f"CLM{claim_counter:06d}",
                    "NUM_DOS": f"DOS{random.randint(100000, 999999)}",
                    "POLICYHOLDER_ID": pol["POLICYHOLDER_ID"],
                    "CONTRACT_ID": contract["CONTRACT_ID"],
                    "COMPANY_ID": company_id,
                    "COD_RISQUE": cod_risque,
                    "NAT_ARRET": nat_arret,
                    "DT_CREATION": dt_creation.isoformat(),
                    "DT_FAIT_GEN": dt_fait_gen.isoformat(),
                    "SALAIRE_REF": salaire,
                    "DT_ETAT_DOS": dt_etat_dos.isoformat(),
                    "MOTIF_ETAT_DOS": motif,
                    "DT_ATTEST_NA": dt_attest_na,
                    "DT_JUSTIF_SS": dt_justif_ss,
                }
            )
            claim_counter += 1

    return rows


# ─────────────────────────────────────────────
# 7. raw_payments
# Règles métier :
#   - Incapacité    : paiement tous les 15 jours, 60-100% du SALAIRE_REF
#   - Invalidité    : paiement fin de mois, SALAIRE_REF - ressources simulées
#   - Rente (DC)    : paiement fin de mois, montant fixe par dossier
#   - Décès         : paiement unique, montant entre 30 000 et 800 000
# ─────────────────────────────────────────────


def _last_day_of_month(d: date) -> date:
    """Retourne le dernier jour du mois pour une date donnée."""
    next_month = add_months(d, 1)
    return next_month - timedelta(days=1)


def _generate_payments_incapacite(claim: dict) -> list[dict]:
    """Génère des paiements bi-mensuels (tous les 15 jours) pour un dossier incapacité."""
    rows = []
    salaire = float(claim["SALAIRE_REF"])
    taux = random.uniform(0.60, 1.00)
    montant_mensuel = salaire * taux
    montant_15j = round(montant_mensuel / 2, 2)

    dt_start = date.fromisoformat(claim["DT_CREATION"])
    dt_end = (
        END_DATE
        if not claim["MOTIF_ETAT_DOS"]
        else date.fromisoformat(claim["DT_ETAT_DOS"])
    )
    dt_end = min(dt_end, END_DATE)

    current = dt_start
    counter = 0
    while current <= dt_end:
        # Légère variation possible si changement de situation (+/- 5%)
        if counter > 0 and random.random() < 0.05:
            taux = random.uniform(0.60, 1.00)
            montant_mensuel = salaire * taux
            montant_15j = round(montant_mensuel / 2, 2)

        mnt_brut = montant_15j
        mnt_pas = round(mnt_brut * random.uniform(0.00, 0.11), 2)
        mnt_net = round(mnt_brut - mnt_pas, 2)

        rows.append(
            {
                "CLAIM_ID": claim["CLAIM_ID"],
                "MNT_BRUT": mnt_brut,
                "MNT_NET": mnt_net,
                "MNT_PAS": mnt_pas,
                "DT_PAIEMENT": current.isoformat(),
            }
        )
        current += timedelta(days=15)
        counter += 1

    return rows


def _generate_payments_invalidite(claim: dict) -> list[dict]:
    """Génère des paiements mensuels (fin de mois) pour un dossier invalidité.

    Le montant est calculé comme SALAIRE_REF moins une ressource simulée,
    dans la limite du salaire (contrainte légale).
    """
    rows = []
    salaire = float(claim["SALAIRE_REF"])

    # Ressource simulée : entre 20% et 60% du salaire (SS + PE)
    ressource_base = salaire * random.uniform(0.20, 0.60)
    montant_base = round(max(0, salaire - ressource_base), 2)

    dt_start = date.fromisoformat(claim["DT_CREATION"])
    dt_end = (
        END_DATE
        if not claim["MOTIF_ETAT_DOS"]
        else date.fromisoformat(claim["DT_ETAT_DOS"])
    )
    dt_end = min(dt_end, END_DATE)

    current = date(dt_start.year, dt_start.month, 1)
    montant_courant = montant_base

    while current <= dt_end:
        # Changement de montant rare (~5%) : nouvelle situation du salarié
        if random.random() < 0.05:
            ressource_base = salaire * random.uniform(0.20, 0.60)
            montant_courant = round(max(0, salaire - ressource_base), 2)

        dt_paiement = _last_day_of_month(current)
        if dt_paiement > END_DATE:
            break

        mnt_pas = round(montant_courant * random.uniform(0.00, 0.11), 2)
        mnt_net = round(montant_courant - mnt_pas, 2)

        rows.append(
            {
                "CLAIM_ID": claim["CLAIM_ID"],
                "MNT_BRUT": montant_courant,
                "MNT_NET": mnt_net,
                "MNT_PAS": mnt_pas,
                "DT_PAIEMENT": dt_paiement.isoformat(),
            }
        )
        current = add_months(current, 1)

    return rows


def _generate_payments_rente(claim: dict) -> list[dict]:
    """Génère des paiements mensuels fixes (fin de mois) pour les rentes DC."""
    rows = []
    salaire = float(claim["SALAIRE_REF"])
    # Rente fixe entre 20% et 60% du salaire de référence
    montant_fixe = round(salaire * random.uniform(0.20, 0.60), 2)

    dt_start = date.fromisoformat(claim["DT_CREATION"])
    dt_end = (
        END_DATE
        if not claim["MOTIF_ETAT_DOS"]
        else date.fromisoformat(claim["DT_ETAT_DOS"])
    )
    dt_end = min(dt_end, END_DATE)

    current = date(dt_start.year, dt_start.month, 1)

    while current <= dt_end:
        dt_paiement = _last_day_of_month(current)
        if dt_paiement > END_DATE:
            break

        mnt_pas = round(montant_fixe * random.uniform(0.00, 0.11), 2)
        mnt_net = round(montant_fixe - mnt_pas, 2)

        rows.append(
            {
                "CLAIM_ID": claim["CLAIM_ID"],
                "MNT_BRUT": montant_fixe,
                "MNT_NET": mnt_net,
                "MNT_PAS": mnt_pas,
                "DT_PAIEMENT": dt_paiement.isoformat(),
            }
        )
        current = add_months(current, 1)

    return rows


def _generate_payments_deces(claim: dict) -> list[dict]:
    """Génère un paiement unique pour un dossier décès (capital décès)."""
    dt_paiement = rand_date(
        date.fromisoformat(claim["DT_CREATION"]),
        min(date.fromisoformat(claim["DT_CREATION"]) + timedelta(days=90), END_DATE),
    )
    # Distribution log-normale pour avoir une moyenne autour de 75 000
    mnt_brut = round(min(800_000, max(30_000, random.lognormvariate(11.2, 0.6))), 2)
    mnt_pas = round(mnt_brut * random.uniform(0.00, 0.11), 2)
    mnt_net = round(mnt_brut - mnt_pas, 2)

    return [
        {
            "CLAIM_ID": claim["CLAIM_ID"],
            "MNT_BRUT": mnt_brut,
            "MNT_NET": mnt_net,
            "MNT_PAS": mnt_pas,
            "DT_PAIEMENT": dt_paiement.isoformat(),
        }
    ]


def gen_payments(claims: list[dict]) -> list[dict]:
    """Génère les paiements pour tous les dossiers selon leur type de risque."""
    rows = []
    counter = 1

    dispatch = {
        "Incapacité": _generate_payments_incapacite,
        "Invalidité": _generate_payments_invalidite,
        "Rente viagère": _generate_payments_rente,
        "Rente éducation": _generate_payments_rente,
        "Décès": _generate_payments_deces,
    }

    for claim in claims:
        fn = dispatch.get(claim["COD_RISQUE"])
        if fn is None:
            continue
        for row in fn(claim):
            row["PAYMENT_ID"] = f"PAY{counter:07d}"
            rows.append(row)
            counter += 1

    return rows


# ─────────────────────────────────────────────
# 8. raw_premiums — cotisations trimestrielles
# Règles métier :
#   - Montant de base stable par contrat
#   - Revalorisation annuelle au 1er janvier : 0-15%
#   - Si revalorisation > 12% : résiliation probable l'année suivante
#   - Parfois double paiement : un trimestre est sauté, le suivant est doublé
#   - ~5% de trimestres manquants (impayés)
# ─────────────────────────────────────────────


def gen_premiums(  # pylint: disable=too-many-locals,too-many-branches
    contracts: list[dict],
) -> list[dict]:
    """Génère les cotisations trimestrielles avec revalorisation annuelle cohérente."""
    rows = []
    counter = 1

    quarters = []
    d = first_day_of_quarter(START_DATE)
    while d <= END_DATE:
        quarters.append(d)
        d = add_months(d, 3)

    for contract in contracts:
        dt_adhesion = date.fromisoformat(contract["DT_ADHESION"])
        dt_resiliation = contract["DT_RESILIATION"]
        dt_end = date.fromisoformat(dt_resiliation) if dt_resiliation else END_DATE

        montant_courant = round(random.uniform(1_000, 15_000), 2)
        annee_courante = None
        trimestres_sautes: set[date] = set()

        for i, q in enumerate(quarters):
            if q < first_day_of_quarter(dt_adhesion):
                continue
            if q > dt_end:
                break

            # Revalorisation au 1er janvier
            if annee_courante != q.year and q.month == 1:
                annee_courante = q.year
                taux_revalo = random.uniform(0.00, 0.15)
                montant_courant = round(montant_courant * (1 + taux_revalo), 2)
                # Résiliation probable si revalorisation > 12%
                if taux_revalo > 0.12 and not dt_resiliation:
                    dt_resil = date(q.year, random.randint(3, 12), 1)
                    if dt_resil > q:
                        dt_end = dt_resil

            # Trimestre sauté (double paiement anticipé)
            if q in trimestres_sautes:
                continue

            # ~5% d'impayés
            if random.random() < 0.05:
                continue

            # ~8% de double paiement : on saute le trimestre suivant
            if random.random() < 0.08 and i + 1 < len(quarters):
                trimestres_sautes.add(quarters[i + 1])
                mnt = round(montant_courant * 2, 2)
            else:
                mnt = montant_courant

            dt_encaissement = add_months(q, 3) + timedelta(days=random.randint(0, 20))
            if dt_encaissement > END_DATE:
                continue

            rows.append(
                {
                    "PREMIUM_ID": f"PRM{counter:07d}",
                    "CONTRACT_ID": contract["CONTRACT_ID"],
                    "MNT_COTISATION": mnt,
                    "DT_ENCAISSEMENT": dt_encaissement.isoformat(),
                    "ECHEANCE_DATE": q.isoformat(),
                }
            )
            counter += 1

    return rows


# ─────────────────────────────────────────────
# 9. raw_resources — Invalidité uniquement
# ─────────────────────────────────────────────

TYP_RESSOURCE_VALUES = ["PE", "Salaire", "Rente SS", "Autre"]
TYP_RESSOURCE_WEIGHTS = [0.35, 0.25, 0.30, 0.10]


def gen_resources(claims: list[dict]) -> list[dict]:
    """Génère 1 à 3 ressources par dossier invalidité (PE, salaire, rente SS, autre)."""
    rows = []
    counter = 1

    inval_claims = [c for c in claims if c["COD_RISQUE"] == "Invalidité"]

    for claim in inval_claims:
        dt_creation = date.fromisoformat(claim["DT_CREATION"])
        # 1 à 3 ressources par dossier
        n = random.randint(1, 3)
        used_types: set[str] = set()

        for _ in range(n):
            typ = random.choices(TYP_RESSOURCE_VALUES, TYP_RESSOURCE_WEIGHTS)[0]
            if typ in used_types:
                continue
            used_types.add(typ)

            dt_debut = rand_date(dt_creation, END_DATE - timedelta(days=30))
            # ~60% des ressources sont en cours
            if random.random() < 0.40:
                dt_fin = rand_date(dt_debut + timedelta(days=30), END_DATE).isoformat()
            else:
                dt_fin = ""

            rows.append(
                {
                    "RESOURCE_ID": f"RES{counter:06d}",
                    "CLAIM_ID": claim["CLAIM_ID"],
                    "TYP_RESSOURCE": typ,
                    "MONTANT": round(random.uniform(300, 2500), 2),
                    "DT_DEBUT": dt_debut.isoformat(),
                    "DT_FIN": dt_fin,
                }
            )
            counter += 1

    return rows


# ─────────────────────────────────────────────
# 10. raw_beneficiaries — Rentes DC uniquement
# ─────────────────────────────────────────────


def gen_beneficiaries(claims: list[dict]) -> list[dict]:
    """Génère les bénéficiaires des rentes DC (conjoint ou enfants selon le type)."""
    rows = []
    counter = 1

    rente_claims = [
        c for c in claims if c["COD_RISQUE"] in ("Rente viagère", "Rente éducation")
    ]

    for claim in rente_claims:
        # Rente éducation : 1 à 3 enfants
        # Rente viagère : 1 conjoint
        if claim["COD_RISQUE"] == "Rente éducation":
            n = random.randint(1, 3)
        else:
            n = 1

        for _ in range(n):
            if claim["COD_RISQUE"] == "Rente éducation":
                # Enfants : nés entre 1990 et 2015
                dt_naissance = rand_date(date(1990, 1, 1), date(2015, 12, 31))
            else:
                # Conjoint : né entre 1950 et 1980
                dt_naissance = rand_date(date(1950, 1, 1), date(1980, 12, 31))

            rows.append(
                {
                    "BENEFICIARY_ID": f"BEN{counter:05d}",
                    "CLAIM_ID": claim["CLAIM_ID"],
                    "NOM": fake.last_name().upper(),
                    "PRENOM": fake.first_name(),
                    "DT_NAISSANCE": dt_naissance.isoformat(),
                }
            )
            counter += 1

    return rows


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────


def main() -> None:
    """Point d'entrée : génère et écrit tous les CSV du dataset PrevCorp."""
    print("\nGeneration du dataset PrevCorp\n")

    segments = gen_segments()
    contracts = gen_contracts(segments, n=500)
    companies = gen_companies(n=500)
    contract_companies = gen_contract_companies(contracts, companies)
    policyholders = gen_policyholders(n=5000)
    claims = gen_claims(policyholders, contracts, contract_companies)
    payments = gen_payments(claims)
    premiums = gen_premiums(contracts)
    resources = gen_resources(claims)
    beneficiaries = gen_beneficiaries(claims)

    write_csv("raw_segments.csv", segments)
    write_csv("raw_contracts.csv", contracts)
    write_csv("raw_companies.csv", companies)
    write_csv("raw_contract_companies.csv", contract_companies)
    write_csv("raw_policyholders.csv", policyholders)
    write_csv("raw_claims.csv", claims)
    write_csv("raw_payments.csv", payments)
    write_csv("raw_premiums.csv", premiums)
    write_csv("raw_resources.csv", resources)
    write_csv("raw_beneficiaries.csv", beneficiaries)

    print(f"\nDataset genere dans {OUTPUT_DIR}/\n")


if __name__ == "__main__":
    main()
