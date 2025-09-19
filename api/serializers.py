from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from user_requests.models import DonationRequest


def userRequestSerializer(requester_crm, request_type, **kwargs):
    requester = get_object_or_404(User, crm=requester_crm)

    if request_type == 'donation':
        requestee_crm = kwargs.get('requestee_crm')
        requestee = get_object_or_404(User, crm=requestee_crm) if requestee_crm else None

        if not requestee:
            raise ValueError("requestee is required for donation requests")
        return "donation request created"
        # return DonationRequest(requester=requester, requestee=requestee)
    else:
        raise ValueError("Unsupported request type")


# class DonationRequestSerializer(serializers.ModelSerializer)
