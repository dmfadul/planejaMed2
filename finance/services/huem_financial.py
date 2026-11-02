from collections import defaultdict
from decimal import Decimal

from finance.models import HospitalFinancialEntry

TRANSFER_CATEGORIES = {
    "REPASSE PARTICULARES": {
        "dp": ["CONSULTA COM ANESTESIOLOGISTA", "AVALIACAO PRE-ANESTESICA"],
        "key": "individual_particular_consult",
        "key_neg": "rp_huem_particular_proc"
    },
    "REPASSE CONVENIOS": {
        "dp": ["EM CONSULTÓRIO"],
        "key": "individual_convenios_consult",
        "key_neg": "rp_huem_convenios_proc"
    },
    "REPASSE AMBULATORIAL": {
        "dp": ["CONSULTA MEDICA EM ATENÇÃO ESPECIALIZADA"],
        "key": "individual_sus_ambulatoryconsult",
        "key_neg": "rp_huem_ambulatory_proc"
    },
    "REPASSE AIH": {
        "dp": ["AVALIACAO PRE-ANESTESICA", "CONSULTA/AVALIAÇÃO EM PACIENTE INTERNADO"],
        "key": "individual_sus_aihconsult",
        "key_neg": "rp_huem_aih_proc"
    }
}

# Used to exclude entries from the financial map, base on procedure descriptions.
EXCLUDED_CATEGORIES = {
}


def build_hospital_financial_map(month, batch_type):
    entries = (
        HospitalFinancialEntry.objects
        .filter(
            batch__month=month,
            batch__batch_type=batch_type,
        )
        .values(
            "id",
            "doctor_id",
            "procedure_description",
            "transfer_description",
            "amount",
        )
    )

    result = defaultdict(lambda: Decimal("0.00"))

    for entry in entries:
        key = classify_transfer_description(
            dr=entry["transfer_description"],
            dp=entry["procedure_description"]
        )
        if key is None:
            raise ValueError(
                f"Entry {entry['id']} could not be categorized: "
                f"{entry['transfer_description']!r}"
            )

        result[
            (entry["doctor_id"], key)
        ] += entry["amount"]

    return result


def classify_transfer_description(dr, dp):
    for dr_category, category_dict in TRANSFER_CATEGORIES.items():
        if not dr.startswith(dr_category):
            continue
        dp_categories = category_dict["dp"]
        if any(dp.startswith(dp_category) for dp_category in dp_categories):
            return category_dict["key"]
        else:
            return category_dict["key_neg"]
        
    return None
