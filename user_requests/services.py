from django.db import transaction
from user_requests.models import UserRequest, IncludeRequestData
from api.serializers import IncludeRequestDataSerializer

@transaction.atomic
def create_user_request(
    *,
    requester,
    request_type,
    requestee,
    donor,
    donee,
    shift,
    start_hour,
    end_hour,
    include_payload,
    action,
):
    req = UserRequest.objects.create(
        requester=requester,
        request_type=request_type,
        requestee=requestee,
        donor=donor,
        donee=donee,
        shift=shift,
        start_hour=start_hour,
        end_hour=end_hour,
    )

    if action == "include" and include_payload:
        inc_ser = IncludeRequestDataSerializer(data=include_payload)
        inc_ser.is_valid(raise_exception=True)
        inc_ser.save(user_request=req)

    req.notify_request()
    return req
