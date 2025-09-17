from core.models import User
from django.shortcuts import get_object_or_404
from user_requests.models import DonationRequest


def userRequestSerializer(requester_crm, request_type, **kwargs):
    requester = get_object_or_404(User, crm=requester_crm)

    if request_type == 'donation':
        requestee_crm = kwargs.get('requestee_crm')
        requestee = get_object_or_404(User, crm=requestee_crm) if requestee_crm else None
        
        if not requestee:
            raise ValueError("requestee is required for donation requests")
        return DonationRequest(requester=requester, requestee=requestee)
    else:
        raise ValueError("Unsupported request type")


