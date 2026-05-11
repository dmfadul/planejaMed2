# views.py
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .forms import UploadedDocumentForm
from .models import UploadedDocument
from shifts.models import Month
from core.models import User

from .services import get_user_finance_summary
from django.contrib.auth.decorators import login_required


@login_required
def finance_dashboard(request, month_id):
    month = get_object_or_404(Month, id=month_id)

    users = User.objects.filter(is_active=True).order_by("name")

    rows = []

    for user in users:
        summary = get_user_finance_summary(month, user)

        rows.append({
            "user": user,
            **summary,
        })

    context = {
        "month": month,
        "rows": rows,
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