
from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST

from django.contrib import messages
from .forms import UploadedDocumentForm
from .models import UploadedDocument
from shifts.models import Month
from core.models import User
from django.db.models.functions import Lower

from .services import build_finance_grid, get_user_finance_summary, SHEET_COLUMNS
from django.contrib.auth.decorators import login_required


@login_required
def finance_spreadsheet(request):
    month = Month.get_current()
    grid = build_finance_grid(month)

    return render(request, "finance/spreadsheet.html", {"month": month, "grid": grid})


@login_required
def edit_cell(request):
    return redirect("finance:spreadsheet")

@login_required
@require_POST
def update_cell(request):
    return redirect("finance:spreadsheet")

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