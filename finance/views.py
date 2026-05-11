# views.py
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import UploadedDocumentForm
from .models import UploadedDocument
from shifts.models import Month

from django.contrib.auth.decorators import login_required


@login_required
def finance_dashboard(request):
    if not (request.user.is_superuser or request.user.is_staff):
        messages.error(request, "You do not have permission to upload documents.")
        return redirect("finance:dashboard")
    docs = UploadedDocument.objects.select_related("month").order_by("-uploaded_at")
    return render(request, "finance/dashboard.html", {"docs": docs})


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