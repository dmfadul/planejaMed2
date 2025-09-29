from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from user_requests.models import UserRequest, Notification
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueTogetherValidator


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class UserRequestSerializer(serializers.ModelSerializer):    
    class Meta:
        model = UserRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=UserRequest.objects.filter(is_open=True),
                fields=('requester', 'request_type', 'shift', 'start_hour', 'end_hour'),
                message=_("Você tem um pedido aberto para este horário.")  # your custom text
            )
        ]
    
    # def validate(self, attrs):
    #     requester = attrs.get('requester') or getattr(self.instance, 'requester', None)
    #     request_type = attrs.get('request_type') or getattr(self.instance, 'request_type', None)
    #     shift = attrs.get('shift') or getattr(self.instance, 'shift', None)

    #     if requester and request_type and shift:
    #         exists = UserRequest.objects.filter(
    #             requester=requester,
    #             request_type=request_type,
    #             shift=shift,
    #             start_hour=attrs.get('start_hour') or getattr(self.instance, 'start_hour', None),
    #             end_hour=attrs.get('end_hour') or getattr(self.instance, 'end_hour', None),
    #             is_open=True
    #         )
    #         if self.instance:
    #             exists = exists.exclude(pk=self.instance.pk)
    #         if exists.exists():
    #             self.fail("duplicate_open")
    #     return attrs

