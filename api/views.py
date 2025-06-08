from django.http import JsonResponse
from django.views.decorators.http import require_GET
from shifts.models import Center


@require_GET
def centers_list(request):
    centers = [{"abbr": c.abbreviation} for c in Center.objects.all()]
    return JsonResponse(centers, safe=False)


@require_GET
def month_list(request):
    months = [
        {"number": i, "name": name}
        for i, name in enumerate([
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ], 1)
    ]
    return JsonResponse(months, safe=False)


@require_GET
def year_list(request):
    years = [{"year": year} for year in range(2025, 2031)]
    return JsonResponse(years, safe=False)
