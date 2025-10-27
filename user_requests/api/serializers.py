from core.models import User
from vacations.models import Vacation
from rest_framework import serializers
from shifts.models import Center, Month, Shift
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
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

# class UserRequestSerializer(serializers.ModelSerializer):    
#     class Meta:
#         model = UserRequest
#         fields = '__all__'
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=UserRequest.objects.filter(is_open=True),
#                 fields=('requester', 'request_type', 'shift', 'start_hour', 'end_hour'),
#                 message="Você tem um pedido aberto para este horário."  # your custom text
#             )
#         ]


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
    

class IncomingUserRequestSerializer(serializers.Serializer):
    ACTIONS = ("ask_for_donation", "offer_donation", "include", "exclude")

    action = serializers.ChoiceField(choices=ACTIONS)
    cardCRM = serializers.CharField(max_length=10, required=False, allow_blank=True, allow_null=True)
    center = serializers.SlugField(max_length=10, required=False, allow_blank=True)
    day = serializers.IntegerField(min_value=1, max_value=31, required=False)
    shift = serializers.CharField(max_length=10, required=False, allow_blank=True)
    startHour = serializers.IntegerField(min_value=0, max_value=23, required=False, allow_null=True)
    endHour = serializers.IntegerField(min_value=0, max_value=23, required=False, allow_null=True)    
    
    def validate(self, attrs):
        request = self.context['request']
        action = attrs['action']
        center_abbr = attrs.get('center')
        shift_raw = attrs.get('shift')
        
        # Resolve center if provided/required
        center = None
        if action in ("include"):
            if not center_abbr:
                raise serializers.ValidationError({"center": _("Centro é obrigatório para inclusão.")})
            center = get_object_or_404(Center, abbreviation=center_abbr)

        # resolve users (requester/requestee/donor/donee) by action
        requester = request.user
        requestee = None
        donor = None
        donee = None 
         
        crm = attrs.get('cardCRM')
        if not crm and action in ("ask_for_donation", "offer_donation"):
            raise serializers.ValidationError({"cardCRM": _("CRM é obrigatório para doações.")})
        elif not crm:
            crm = requester.crm
        other_user = get_object_or_404(User, crm=crm)

        if action in ("ask_for_donation", "offer_donation"):
            requestee = other_user
        elif action in ("include", "exclude"):
            requestee = None # requestee are Admin in these cases

        if action == "ask_for_donation":
            donor, donee = requestee, requester
            request_type = UserRequest.RequestType.DONATION
        elif action == "offer_donation":
            donor, donee = requester, requestee
            request_type = UserRequest.RequestType.DONATION
        elif action == "exclude":
            donor, donee = other_user, None
            request_type = UserRequest.RequestType.EXCLUDE
        elif action == "include":
            donor, donee = None, other_user
            request_type = UserRequest.RequestType.INCLUDE
        else:
            raise serializers.ValidationError({"action": _("Ação inválida.")})
        
        if requester == requestee:
            raise serializers.ValidationError({"non_field_errors": _("Você não pode fazer um pedido para si mesmo.")})

        # resolve shift/start_hour/end_hour normalization
        if not shift_raw:
            raise serializers.ValidationError({"shift": _("Turno é obrigatório para inclusão.")})
        
        shift = None
        start_hr, end_hr = attrs.get('startHour'), attrs.get('endHour')
        if not action == 'include':
            shift = get_object_or_404(Shift, id=int(shift_raw))
        elif not shift_raw == '-':
            start_hr, end_hr = Shift.convert_to_hours(shift_raw)        

        if shift and not shift.month == Month.get_current():
            raise serializers.ValidationError({"shift": _("Turno não pertence ao mês atual.")})
        
        # conflict check for actions that place someone on a schedule
        if action in ("include", "ask_for_donation", "offer_donation"):
            month_obj = Month.get_current()
            conflict = Shift.check_conflict(
                doctor=donee,
                month=month_obj,
                day=shift.day if shift else attrs.get('day'),
                start_time=start_hr,
                end_time=end_hr,
            )

            if conflict:
                raise serializers.ValidationError({
                    "conflito": (
                        f"O usuário {getattr(donee, 'name', donee)} já está no centro "
                        f"{conflict.center.abbreviation} no dia {conflict.day}."
                    )
                })
        # For include, validate the extra payload now so the service can trust it
        include_payload = None
        if action == "include":
            include_payload = {
                "center": center.id,
                "month": month_obj.id,
                "day": attrs.get('day'),
            }

        # For include, validate the extra payload now so the service can trust it
        return {
            "request_type": request_type,
            "requester": requester,
            "requestee": requestee,
            "donor": donor,
            "donee": donee,
            "shift": shift,
            "start_hour": start_hr,
            "end_hour": end_hr,
            "include_payload": include_payload,
            "action": action,
        }
    
class OutUserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequest
        fields = ("id", "request_type", "created_at")