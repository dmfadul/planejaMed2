# user_requests/api/serializers.py
from rest_framework import serializers
from user_requests.models.userRequest import UserRequest
from user_requests.models.notifications import Notification
from rest_framework.validators import UniqueTogetherValidator


class UserRequestSerializer(serializers.ModelSerializer):    
    class Meta:
        model = UserRequest
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=UserRequest.objects.filter(is_open=True),
                fields=('requester', 'request_type', 'shift', 'start_hour', 'end_hour'),
                message="Você tem um pedido aberto para este horário."  # your custom text
            )
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
