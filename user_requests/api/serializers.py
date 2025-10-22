# user_requests/api/serializers.py
from vacations.models import Vacation
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from user_requests.models import UserRequest, VacationRequest, Notification


class VacationRequestSerializer(serializers.ModelSerializer):
    requester = serializers.HiddenField(default=serializers.CurrentUserDefault())
    requestee = serializers.HiddenField(default=None)
    responder = serializers.HiddenField(default=None)
    
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    leave_type = serializers.ChoiceField(choices=Vacation.VacationType.choices)

    class Meta:
        model = VacationRequest
        fields = [
            "start_date", "end_date", "leave_type",
            # included but not writable (returned in the response)
            "id", "created_at", "is_open", "is_approved", "closing_date",
            "requester", "user", "requestee", "responder",
        ]
        read_only_fields = [
            "id", "created_at", "is_open", "is_approved", "closing_date",
            "requestee", "responder",
        ]

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date must be after start date.")

        return attrs

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