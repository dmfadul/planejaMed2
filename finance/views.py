from django.shortcuts import render, redirect
from .forms import UploadForm


def upload_view(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload')
    else:
        form = UploadForm()
    return render(request, 'finance/upload.html', {'form': form})
