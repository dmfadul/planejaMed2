from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from user_requests.models import DonationRequest


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


def userRequestSerializer(request_type, requester, params):
    if request_type in ['donation_required', 'donation_offered']:
        requestee = User.objects.filter(crm=params.get('requesteeCRM')).first()
        center = Center.objects.filter(abbreviation=params.get('center')).first()
        month = Month.objects.filter(year=params.get('year'), number=params.get('monthNumber')).first()
        day = params.get('day')
        start_hour = params.get('startHour')
        end_hour = params.get('endHour')
        
        if request_type == 'donation_required':
            donor = requestee
            donee = requester
        else:
            donor = requester
            donee = requestee
        
        shift = Shift.objects.filter(
            user=donor,
            center=center,
            month=month,
            day=day,
            start_time=start_hour,
            end_time=end_hour
        ).first()

        if not shift:
            return None
        
        payload = {
            'action': 'donation',
            'requester': requester.pk,
            'requestee': requestee.pk,
            'donor': donor.pk,
            'donee': donee.pk,
            'shift': shift.pk,
        }
        
        serializer = DonationRequestSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return serializer.instance

    return None

class DonationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonationRequest
        fields = '__all__'
