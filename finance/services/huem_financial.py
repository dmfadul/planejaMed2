# finance/services/hospital_financial.py

from collections import defaultdict
from decimal import Decimal


TRANSFER_CATEGORIES = {
    "aih": ["AIH"],
    "ambulatorial": ["Ambulatorial"],
    "convenios": ["Convênios"],
    "particulares": ["Particulares"],
}