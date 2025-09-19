from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from user_requests.models import DonationRequest


def userRequestSerializer(request_type, requester, parameters):
    center_abbr = parameters.get('center')
    center = get_object_or_404(Center, abbreviation=center_abbr)

    month_number = parameters.get('monthNumber')
    year = parameters.get('year')
    month = get_object_or_404(Month, number=month_number, year=year)

    attrs = {
        'requester': requester,
        'center': center,
        'month': month,
    }
    print(request_type)
    print(requester)
    print(parameters)

    return None

class DonationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = '__all__'

    def validate(self, attrs):
        # Custom validation logic
        return attrs
