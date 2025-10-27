from core.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def users_list(request):
    exclude_curr = request.GET.get('exclude_curr_user', 'false').lower() == 'true'

    users_qs = User.objects.filter(is_active=True, is_invisible=False)

    if exclude_curr and request.user.is_authenticated:
        users_qs = users_qs.exclude(id=request.user.id)

    users = [
        {
            "id": user.id,
            "crm": user.crm,
            "name": user.name
        }
        for user in users_qs.order_by('name')
    ]
    return JsonResponse(users, safe=False)