from decimal import Decimal, InvalidOperation

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models.functions import Lower
from django.contrib import messages


from core.models import User
from shifts.models import Month
from finance.grids import FINANCE_GRIDS, CONSTANTS_GRIDS
from finance.models import FinanceEntry, FinanceCategory, FinanceSource

from .services import build_finance_grid, build_constant_grid
from .forms import UploadedDocumentForm
from .models import UploadedDocument


@login_required
def finance_constants(request):
    month = Month.get_current()

    selected_grid_key = "constants"
    selected_grid = CONSTANTS_GRIDS.get(selected_grid_key)

    grid = build_constant_grid(
        month=month,
        rows=selected_grid["rows"],
        user=request.user,
    )

    return render(request, "finance/spreadsheet.html", {
        "month": month,
        "months": [],
        "grid": grid,
        "grids": [],
        "selected_grid_key": selected_grid_key,
    })

@login_required
def finance_spreadsheet(request):  
    current_month = Month.get_current()

    month_year = request.GET.get("month_year")
    if month_year:
        selected_month_number, selected_year = month_year.split("-")
    else:
        selected_month_number = current_month.number
        selected_year = current_month.year

    month = get_object_or_404(
        Month,
        number=selected_month_number,
        year=selected_year,
    )

    selected_grid_key = request.GET.get("grid", "input")
    selected_grid = FINANCE_GRIDS.get(selected_grid_key)

    if selected_grid is None:
        selected_grid_key = "input"
        selected_grid = FINANCE_GRIDS["input"]

    grid = build_finance_grid(
        month=month,
        columns=selected_grid["columns"],
    )

    months = Month.objects.all().order_by("-year", "-number")

    return render(request, "finance/spreadsheet.html", {
        "month": month,
        "months": months,
        "grid": grid,
        "grids": FINANCE_GRIDS,
        "selected_grid_key": selected_grid_key,
    })


@login_required
def edit_cell(request, grid_key, month_id, user_id, column_key):
    month = get_object_or_404(Month, id=month_id)
    user = get_object_or_404(User, id=user_id)
    column = get_column_or_404(grid_key, column_key)

    if not column.get("editable", False):
        return HttpResponseForbidden("Protected cell")
    
    category = FinanceCategory.objects.filter(code=column["category_code"]).first()

    entry = FinanceEntry.objects.filter(
        month=month,
        user=user,
        category=category,
    ).first()

    value = entry.amount if entry else Decimal("0.00")

    return render(request, "finance/partials/cell_input.html", {
        "month": month,
        "user": user,
        "column": column,
        "value": value,
        "selected_grid_key": grid_key,
    })


@login_required
@require_POST
def update_cell(request, grid_key, month_id, user_id, column_key):
    month = get_object_or_404(Month, id=month_id)
    user = get_object_or_404(User, id=user_id)
    column = get_column_or_404(grid_key, column_key)

    if not column.get("editable"):
        return HttpResponseForbidden("Protected cell")

    raw_value = request.POST.get("value", "0").replace(",", ".")

    try:
        amount = Decimal(raw_value)
    except InvalidOperation:
        return HttpResponseBadRequest("Invalid number")

    category, _ = FinanceCategory.objects.get_or_create(
        name=column["category"],
        code=column["category_code"],
    )

    source = FinanceSource.objects.filter(name=column["source"]).first()   
    if source is None:
        return HttpResponseBadRequest("Invalid source")

    FinanceEntry.objects.update_or_create(
        month=month,
        user=user,
        category=category,
        description=f"{column['subcategory']}_{column['label']}",
        entry_type=column["entry_type"],
        source=source,
        defaults={
            "amount": amount,
        },
    )

    return render(request, "finance/partials/cell_display.html", {
        "month": month,
        "user": user,
        "column": column,
        "value": f"{amount:<,.2f}",
        "editable": True,
        "selected_grid_key": grid_key,
    })

@login_required
def edit_constant_cell(request, month_id, user_id, column_key):
    from django.http import HttpResponse
    month = get_object_or_404(Month, id=month_id)
    user = get_object_or_404(User, id=user_id)
    rows = CONSTANTS_GRIDS["constants"]["rows"]

    print("col key", column_key)


    return HttpResponse(repr(column_key))

@login_required
@require_POST
def update_constant_cell(request, grid_key, month_id, user_id, column_key):
    pass

def get_column_or_404(grid_key, column_key):
    grid_config = FINANCE_GRIDS.get(grid_key)
    
    if grid_config is None:
        raise Http404("Grid not found")

    for column in grid_config["columns"]:
        if column["key"] == column_key:
            return column

    raise Http404("Column not found")


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