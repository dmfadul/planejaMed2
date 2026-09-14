from shifts.models import Month
from django.shortcuts import get_object_or_404
from .alt_month_table_builder import build_alt_month_table_data
from .alt_table_builder import build_alt_template_table_data


def build_alt_table_data(month_num=None, year=None):
    if month_num is not None and year is not None:
        month = get_object_or_404(Month, number=month_num, year=year)
        return build_alt_month_table_data(month)
    else:
        return build_alt_template_table_data()