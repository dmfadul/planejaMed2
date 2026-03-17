# views.py
from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import UploadedDocumentForm
from .models import UploadedDocument
from shifts.models import Month 


def finance_dashboard_view(request):
    docs = UploadedDocument.objects.select_related("month").order_by("-uploaded_at")
    return render(request, "finance/dashboard.html", {"docs": docs})

def upload_document_view(request):
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