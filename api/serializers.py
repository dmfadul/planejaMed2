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

        start_hour = params.get('startHour')
        end_hour = params.get('endHour')
        shift_id = params.get('shift')

        shift = Shift.objects.get(pk=int(shift_id))
        if not shift:
            return None
 
        if not start_hour in shift.hour_list or not (end_hour - 1) in shift.hour_list:
            print("Start or end hour not in shift range")
            return None

        if request_type == 'donation_required':
            donor, donee = requestee, requester
        else:
            donor, donee = requester, requestee
                
        payload = {
            'action': 'donation',
            'requester': requester.pk,
            'requestee': requestee.pk,
            'donor': donor.pk,
            'donee': donee.pk,
            'shift': shift.pk,
            'start_hour': start_hour,
            'end_hour': end_hour
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
