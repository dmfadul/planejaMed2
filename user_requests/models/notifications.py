from django.db import models
from core.models import User
from django.utils import timezone
from vacations.models import Vacation as V
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


# TODO: make some kinds of notifications (e.g. 'INFO') be hard-deletable by users

class Notification(models.Model):
    class Kind(models.TextChoices):
        ACTION = 'action', 'Action'
        INFO = 'info', 'Info'
        CANCEL = 'cancel', 'Cancel'
        ERROR = 'error', 'Error'

    # High-level category (visual style/badge color)
    kind = models.CharField(max_length=20, choices=Kind.choices)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications', null=True, blank=True)

    # Template machinery
    template_key = models.CharField(max_length=50, null=True, blank=True)
    context = models.JSONField(default=dict, blank=True)

    # Optional linkage to any domain object (UserRequest, Shift, etc.)
    related_ct = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    related_id = models.CharField(max_length=64, null=True, blank=True)
    related_obj = GenericForeignKey('related_ct', 'related_id')
    
    # Rendered fields (what you actually show in the UI)
    title = models.CharField(max_length=120)
    body = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    seen_at = models.DateTimeField(null=True, blank=True)   # optional but handy
    is_deleted = models.BooleanField(default=False)         # optional “archive”

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['receiver', 'is_read', 'is_deleted', 'created_at']),
            models.Index(fields=['template_key']),
            models.Index(fields=['related_ct', 'related_id']),
        ]

    def __str__(self):
        receiver_name = self.receiver.name if self.receiver else "Admin"
        return f"Notification to {receiver_name}: {self.title}"

    def archive(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
    
        
    @classmethod
    def notify_request(cls, req):
        """Notify relevant users about a UserRequest event."""
        from user_requests.models import UserRequest as UR

        if req.request_type == V.VacationType.REGULAR:
            temp_key = f'request_pending_regular_vacation'
        elif req.request_type == V.VacationType.SICK:
            temp_key = f'request_pending_sick_leave'
        elif req.request_type == UR.RequestType.DONATION and (req.donor and req.donor == req.requester):
            temp_key = f'request_pending_donation_offered'
        elif req.request_type == UR.RequestType.DONATION and (req.donee and req.donee == req.requester):
            temp_key = f'request_pending_donation_asked_for'
        elif req.request_type == UR.RequestType.EXCLUDE:
            temp_key = f'request_pending_exclusion'
        elif req.request_type == UR.RequestType.INCLUDE:
            temp_key = f'request_pending_inclusion'
        else:
            temp_key = f'request_pending_{UR.request_type}'


        # if req.request_type == req.RequestType.DONATION and req.donor == req.requester:
        #     temp_key = f'request_pending_donation_offered'
        # elif req.request_type == req.RequestType.DONATION and req.donee == req.requester:
        #     temp_key = f'request_pending_donation_asked_for'
        # elif req.request_type == req.RequestType.EXCLUDE:
        #     temp_key = f'request_pending_exclusion'
        # elif req.request_type == req.RequestType.INCLUDE:
        #     temp_key = f'request_pending_inclusion'
        # else:
        #     temp_key = f'request_pending_{req.request_type}'

        if req.request_type in V.VacationType.values:
            ctx = {
                'sender_name':  req.requester.name,
                'start_date':  req.start_date.strftime("%d/%m/%y"),
                'end_date':    req.end_date.strftime("%d/%m/%y"),
                'vacation_type': req.get_request_type_display(),
            }

            cls.from_template(
                template_key=temp_key,  # your vacation pending template
                sender=req.requester,
                receiver=req.requestee,
                context=ctx,
                related_obj=req,
            )

            cls.from_template(
                template_key="vacation_request_received",  # NEW TEMPLATE
                sender=req.requester,
                receiver=req.requester,
                context=ctx,
                related_obj=req,
            )
            return
        else:
            ctx = {
                'sender_name':      req.requester.name,
                'receiver_id':      req.requestee.id if req.requestee else None,
                'requestee_name':   req.requestee.name if req.requestee else "Admin",
                'center':           req.center.abbreviation if req.center else "N/A",
                'date':             req.date.strftime("%d/%m/%y"),
                'start_hour':       f"{req.start_hour:02d}:00",
                'end_hour':         f"{req.end_hour:02d}:00",
                'target_name':      req.target.name,
                'request_type':     req.get_request_type_display().upper(),
            }

        # Notify the requestee
        cls.from_template(
            template_key=temp_key,
            sender=req.requester,
            receiver=req.requestee,
            context=ctx,
            related_obj=req,
        )

        # Send cancelable notification to requester 
        cls.from_template(
            template_key='request_received',
            sender=req.requester,
            receiver=req.requester,
            context=ctx,
            related_obj=req,
        )
        return
    
    @classmethod
    def notify_vacation_response(cls, req, response):
        """Notify relevant users about a VacationRequest response event."""
        # Do I need to add Cancelable notification to requester?
        from user_requests.models import UserRequest as UR

        was_solicited = ((req.request_type == UR.RequestType.DONATION) and
                         (req.donee == req.requestee))

        cls.from_template(
            template_key="request_responded",
            sender=req.responder,
            receiver=req.requester,

            context={
                'sender_name':   req.responder.name,
                'receiver_id':   req.requester.id,
                'response':      "ACEITOU" if response == "accept" else "NEGOU",
                'req_type':      "Férias" if req.get_request_type_display().upper() == "REGULAR" else "Licença Médica",
                'start_date':    req.start_date.strftime("%d/%m/%y"),
                'end_date':      req.end_date.strftime("%d/%m/%y"),
            },
            related_obj=req,
        )

    @classmethod
    def notify_response(cls, req, response):
        """Notify relevant users about a UserRequest response event."""
        # Do I need to add Cancelable notification to requester?
        from user_requests.models import UserRequest as UR

        was_solicited = ((req.request_type == UR.RequestType.DONATION) and
                         (req.donee == req.requestee))

        cls.from_template(
            template_key="request_responded",
            sender=req.responder,
            receiver=req.requester,
            context={
                'sender_name':    req.responder.name,
                'receiver_id':    req.requester.id,
                'response':       "ACEITOU" if response == "accept" else "NEGOU",
                'verb':           "SOLICITAÇÃO" if was_solicited else "OFERTA",
                'req_type':       req.get_request_type_display().upper(),
                'center':         req.center.abbreviation,
                'date':           req.date.strftime("%d/%m/%y"),
                'start_hour':     f"{req.start_hour:02d}:00",
                'end_hour':       f"{req.end_hour:02d}:00",
            },
            related_obj=req,
        )

    
    @classmethod
    def notify_conflict(cls, req, conflict_shift):
        """Notify the requester about a conflict found on their request."""

        cls.from_template(
            template_key="conflict_found",
            sender=req.responder,
            receiver=req.requester,
            context={
                'requester_name': req.requester.name,
                'requestee_name': req.requestee.name if req.requestee else "Admin",
                'donee_name':     req.donee.name,
                'conflict_abbr':  conflict_shift.center.abbreviation,
                'conflict_day':   conflict_shift.get_date().strftime("%d/%m/%y"),
            },
            related_obj=req,
        )


# ------------------- Template Registry ---------------------------------
# Placeholders correspond to context keys
    
    TEMPLATE_REGISTRY = {
        'vacation_request_received': {
            'kind': Kind.CANCEL,
            'title': "Pedido de férias enviado",
            'body': (
                "Seu pedido de {vacation_type} de {start_date} até {end_date} foi enviado "
                "e está aguardando aprovação. Aperte Cancelar para cancelar o pedido."
            ),
        },

        'vacation_request_pending': {
            'kind': Kind.ACTION,
            'title': "Pedido de férias pendente",
            'body': (
                "{sender_name} solicitou {vacation_type} de {start_date} até {end_date}."
            ),
        },

        'request_pending_regular_vacation': {
            'kind': Kind.ACTION,
            'title': "Requisição de férias pendente",
            'body':
                "{sender_name} solicitou férias "
                "de {start_date} até {end_date}.",
        },

        'request_pending_sick_leave': {
            'kind': Kind.ACTION,
            'title': "Requisição de licença médica pendente",
            'body':
                "{sender_name} solicitou licença médica "
                "de {start_date} até {end_date}.",
        },
    
        # “A conflict was found on the your request.”
        'conflict_found': {
            'kind': Kind.INFO,
            'title': "Conflito encontrado. Requisição cancelada",
            'body':
                "A solicitação de {requester_name} para {requestee_name} foi cancelada"
                "porque {donee_name} já está inscrito no centro {conflict_abbr}"
                "no dia {conflict_day} no horário solicitado.",
        },

        # “Another user sent you a request for X.”
        'request_received': {
            'kind': Kind.CANCEL,
            'title': "Pending request with {requestee_name}",
            'body': 
                "Você tem uma SOLICITAÇÃO PENDENTE de {request_type} para {requestee_name} "
                "dos horários: {start_hour} - {end_hour} "
                "no centro {center} no dia {date}. "
                "Aperte Cancelar para cancelar a solicitação.",
        },

        # “Your request is created and waiting for a response.”
        'request_pending_donation_asked_for': {
            'kind': Kind.ACTION,
            'title': "Requisição de doação pendente",
            'body':
                "{sender_name} solicitou para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {center} no dia {date}.",
        },

        'request_pending_donation_offered': {
            'kind': Kind.ACTION,
            'title': "Requisição de doação pendente",
            'body':
                "{sender_name} ofereceu para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {center} no dia {date}.",
        },

        'request_pending_exclusion': {
            'kind': Kind.ACTION,
            'title': "Requisição de exclusão pendente",
            'body':
                "{sender_name} solicita a exclusão dos horários de {target_name}: "
                "{start_hour} - {end_hour} no centro {center} no dia {date}.",
        },

        'request_pending_inclusion': {
            'kind': Kind.ACTION,
            'title': "Requisição de inclusão pendente",
            'body':
                "{sender_name} solicita a inclusão dos horários de {target_name}: "
                "{start_hour} - {end_hour} no centro {center} no dia {date}.",
        },

        'request_responded': {
            'kind': Kind.INFO,
            'title': "Requisição respondida",
            'body':
                "{sender_name} {response} {{{receiver_id}}} {verb} DE {req_type}."
                "{start_hour} - {end_hour} no centro {center} no dia {date}.",
        },
         
        'vacation_request_responded': {
            'kind': Kind.INFO,
            'title': "Requisição respondida",
            'body':
                "{sender_name} {response} {{{receiver_id}}} Pedido DE {req_type}."
                "de {start_date} até {end_date}.",
        },
    }


 # ---- helpers -----------------------------------------------------------
    @classmethod
    def from_template(
        cls,
        *,
        template_key: str,
        sender: User,
        receiver: User,
        context: dict | None = None,
        related_obj=None,
    ) -> "Notification":
        """
        Factory method that:
        - pulls the template,
        - applies defaults,
        - renders title/body with safe placeholders,
        - persists the notification (returns saved instance).
        """

        context = context or {}
        tmpl = cls.TEMPLATE_REGISTRY.get(template_key)
        if not tmpl:
            raise ValidationError(f"Unknown template_key: {template_key}")

        data = context
        title = tmpl['title'].format(**data)
        body  = tmpl['body'].format(**data)
        kind  = tmpl['kind']

        instance = cls(
            kind=kind,
            sender=sender,
            receiver=receiver,
            template_key=template_key,
            context=data,
            title=title,
            body=body,
        )

        if related_obj is not None:
            instance.related_ct = ContentType.objects.get_for_model(related_obj)
            instance.related_id = str(getattr(related_obj, "pk", related_obj))

        instance.full_clean(exclude=['related_ct', 'related_id'])  # sanity
        instance.save()
        return instance

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.seen_at = timezone.now()
            self.save(update_fields=['is_read', 'seen_at'])

    def _personalize_text(self, text: str, viewer_id: int) -> str:
        if not text:
            return text
        viewer_id = int(viewer_id)
        receiver_id = int(self.receiver.id) if self.receiver else None
        receiver_name = self.receiver.name if self.receiver else "Admin"
        # Replace {receiver_id} with "você" if viewer is the receiver
        token = f"{{{receiver_id}}}"
        replacement = (
            "você"
            if viewer_id == receiver_id
            else receiver_name
        )
        return text.replace(token, replacement)
    
    def render(self, viewer_id) -> dict:
        """Return a freshly rendered version (no DB writes)."""
        return {
            "body": self._personalize_text(self.body,  viewer_id),
        }
