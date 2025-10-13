from core.models import User
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from shifts.models import Center, Month, Shift
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueTogetherValidator
from user_requests.models import UserRequest,IncludeRequestData,Notification


class IncomingUserRequestSerializer(serializers.Serializer):
    ACTIONS = ("ask_for_donation", "offer_donation", "include", "exclude")

    action = serializers.ChoiceField(choices=ACTIONS)
    cardCRM = serializers.CharField(max_length=10, required=False, allow_blank=True)
    center = serializers.SlugField(max_length=10, required=False, allow_blank=True)
    day = serializers.IntegerField(min_value=1, max_value=31, required=False)
    shift = serializers.CharField(max_length=10, required=False, allow_blank=True)
    startHour = serializers.IntegerField(min_value=0, max_value=23, required=False)
    endHour = serializers.IntegerField(min_value=0, max_value=23, required=False)    
    
    def validate(self, attrs):
        request = self.context['request']
        action = attrs['action']
        center_abbr = attrs.get('center')
        shift_raw = attrs.get('shift')
        print("Validating with attrs:", attrs)
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
        if not crm:
            raise serializers.ValidationError({"cardCRM": _("CRM é obrigatório para doações.")})
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
            
class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class IncludeRequestDataSerializer(serializers.ModelSerializer):    
    class Meta:
        model = IncludeRequestData
        fields = ('center', 'month', 'day')


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

