from collections import defaultdict
from decimal import Decimal

from finance.models import HospitalFinancialEntry

TRANSFER_CATEGORIES = {
    "aih": ["AIH"],
    "ambulatorial": ["Ambulatorial"],
    "convênios": ["Convênios", "Convenios"],
    "particular": ["Particulares"],
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
            "transfer_description",
            "amount",
        )
    )

    result = defaultdict(lambda: Decimal("0.00"))

    for entry in entries:
        category = classify_transfer_description(
            entry["transfer_description"]
        )

        if category is None:
            raise ValueError(
                f"Entry {entry['id']} could not be categorized: "
                f"{entry['transfer_description']!r}"
            )

        result[
            (entry["doctor_id"], category)
        ] += entry["amount"]

    return result


def classify_transfer_description(description):
    description = description.casefold()

    for category, words in TRANSFER_CATEGORIES.items():
        if any(word.casefold() in description for word in words):
            return category

    return None