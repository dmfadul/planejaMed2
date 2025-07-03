from django.http import JsonResponse
from shifts.models import Center, Month
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET


@require_GET
def centers_list(request):
    centers = [{"abbr": c.abbreviation} for c in Center.objects.all()]
    return JsonResponse(centers, safe=False)


@require_GET
def month_list(request):
    months = [
        {"number": i, "name": name, "current": i == Month.objects.current().number}
        for i, name in enumerate([
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ], 1)
    ]
    return JsonResponse(months, safe=False)


@require_GET
def year_list(request):
    years = [{"year": year, "current": year == Month.objects.current().year} for year in range(2025, 2031)]
    return JsonResponse(years, safe=False)

@require_GET
def day_schedule(request, center_abbr, month_number, year):
    center = get_object_or_404(Center, abbreviation=center_abbr)
    month = get_object_or_404(Month, number=month_number, year=year)

    schedule_data = {
    }

    return JsonResponse(schedule_data)

