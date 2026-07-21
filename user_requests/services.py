import datetime
from django.utils import timezone
from django.db import transaction
from user_requests.models import UserRequest
from user_requests.api.serializers import IncludeRequestDataSerializer


@transaction.atomic
def create_user_request(
    *,
    requester,
    request_type,
    requestee,
    donor,
    donee,
    audience,
    shift,
    start_hour,
    end_hour,
    include_payload,
    action,
):
    expires_at = None

    if action == "open_offer":
        if shift is None:
            raise ValueError("Shift must be provided for open_offer action.")
        
        expires_at = shift.date_time - datetime.timedelta(hours=24)

    req = UserRequest.objects.create(
        requester=requester,
        request_type=request_type,
        requestee=requestee,
        donor=donor,
        donee=donee,
        audience=audience,
        shift=shift,
        start_hour=start_hour,
        end_hour=end_hour,
        expires_at=expires_at
    )

    if action == "include" and include_payload:
        inc_ser = IncludeRequestDataSerializer(data=include_payload)
        inc_ser.is_valid(raise_exception=True)
        inc_ser.save(user_request=req)

    req.notify_request()

    return req


@transaction.atomic
def close_expired_requests():
    from user_requests.models.notifications import Notification
    expired_requests = UserRequest.objects.filter(
        is_open=True,
        expires_at__lte=timezone.now(),
    )

    count = 0
    notified_users = set()
    for req in expired_requests:
        req.expire()
        notified_users.add(req.requester)
        if req.requester not in notified_users:
            Notification.notify_expiration(req)
        count += 1

    return count