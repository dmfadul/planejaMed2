# user_requests/api/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from user_requests.models import UserRequest, VacationRequest, Notification


class VacationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VacationRequest
        fields = '__all__'
        

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

    def to_representation(self, instance):
        data = super().to_representation(instance)

        viewer_id = self.context.get('viewer_id')
        if viewer_id:
            fresh = instance.render(viewer_id)
            data["body"] = fresh["body"]

        return data