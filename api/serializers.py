from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from user_requests.models import userRequest


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = userRequest
        fields = '__all__'

