from decimal import Decimal, InvalidOperation

from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models.functions import Lower
from django.contrib import messages

from core.models import User
from shifts.models import Month
from finance.grid import FINANCE_GRID_COLUMNS
from finance.models import FinanceEntry, FinanceCategory, FinanceSource

from .services import build_finance_grid, get_user_finance_summary, SHEET_COLUMNS
from .forms import UploadedDocumentForm
from .models import UploadedDocument




@login_required
def finance_spreadsheet(request):
    month = Month.get_current()
    grid = build_finance_grid(month)

    return render(request, "finance/spreadsheet.html", {"month": month, "grid": grid})


@login_required
def edit_cell(request, month_id, user_id, column_key):
    month = get_object_or_404(Month, id=month_id)
    user = get_object_or_404(User, id=user_id)
    column = get_column_or_404(column_key)

    if not column.get("editable", False):
        return HttpResponseForbidden("Protected cell")
    
    category = FinanceCategory.objects.get(code=column["category_code"])

    entry = FinanceEntry.objects.filter(
        month=month,
        user=user,
        category=category,
    ).first()

    value = entry.ammount if entry else Decimal("0.00")

    return render(request, "finance/partials/edit_cell.html", {
        "month": month,
        "user": user,
        "column": column,
        "value": value,
    })

@login_required
@require_POST
def update_cell(request):
    return redirect("finance:spreadsheet")


def get_column_or_404(column_key):
    for column in FINANCE_GRID_COLUMNS:
        if column["key"] == column_key:
            return column

    from django.http import Http404
    raise Http404("Column not found")


@login_required
def finance_dashboard(request):
    selected_month_id = request.GET.get("month")
    months = Month.objects.all().order_by("-year", "-number")

    if selected_month_id:
        month = get_object_or_404(Month, id=selected_month_id)
    else:
        month = Month.get_current()

    users = User.objects.filter(is_active=True, is_invisible=False).order_by(Lower("name"))

    rows = []

    for user in users:
        summary = get_user_finance_summary(month, user)

        rows.append({
            "user": user,
            **summary,
        })

    context = {
        "month": month,
        "months": months,
        "rows": rows,
        "sheet_columns": SHEET_COLUMNS,
    }

    return render(request, "finance/dashboard.html", context)

# @login_required
# def finance_dashboard(request):
#     if not (request.user.is_superuser or request.user.is_staff):
#         messages.error(request, "You do not have permission to upload documents.")
#         return redirect("finance:dashboard")
#     docs = UploadedDocument.objects.select_related("month").order_by("-uploaded_at")
#     return render(request, "finance/dashboard.html", {"docs": docs})


@login_required
def upload_document_view(request):
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "You do not have permission to upload documents.")
        return redirect("finance:dashboard")
    if request.method != "POST":
        return redirect("finance:dashboard")

    form = UploadedDocumentForm(request.POST, request.FILES)

    if form.is_valid():
        document = form.save(commit=False)
        document.month = Month.get_current()
        document.save()
        messages.success(request, "Document uploaded successfully.")
    else:
        error_text = " | ".join(
            [f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()]
        )
        messages.error(request, error_text)

    return redirect("finance:dashboard")