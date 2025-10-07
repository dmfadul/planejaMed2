from django.db import models
from core.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Notification(models.Model):
    class Kind(models.TextChoices):
        ACTION = 'action', 'Action'
        INFO = 'info', 'Info'
        CANCEL = 'cancel', 'Cancel'
        ERROR = 'error', 'Error'

    # High-level category (visual style/badge color)
    kind = models.CharField(max_length=20, choices=Kind.choices)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')

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
        return f"Notification to {self.receiver.name}: {self.title}"

    def archive(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

# ------------------- Template Registry ---------------------------------
# Placeholders correspond to context keys

# Marcela Vogel Paracatu de Oliveira solicitou DOAÇÃO dos horários:
# 19:00 - 07:00 no centro CCG no dia 26/08/25 (PARA Alberto David Fadul Filho)

# Sua SOLICITAÇÃO DE DOAÇÃO dos horários:
# 07:00 - 19:00 no centro CCG no dia 17/08/25 (DE Roberto Talamini Espínola Filho) foi autorizada.

    TEMPLATE_REGISTRY = {
        # “Another user sent you a request for X.”
        'request_received': {
            'kind': Kind.CANCEL,
            'title': "Pending request with {requestee_name}",
            'body': 
                "Você tem uma SOLICITAÇÃO PENDENTE de {request_type} para {requestee_name} "
                "dos horários: {start_hour} - {end_hour} "
                "no centro {shift_center} no dia {shift_date}. "
                "Aperte Cancelar para cancelar a solicitação.",
        },

        # “Your request is created and waiting for a response.”
        'request_pending_donation_required': {
            'kind': Kind.ACTION,
            'title': "Requisição pendente",
            'body':
                "{sender_name} solicitou para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {shift_center} no dia {shift_date}.",
        },

        'request_pending_donation_offered': {
            'kind': Kind.ACTION,
            'title': "Requisição pendente",
            'body':
                "{sender_name} ofereceu para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {shift_center} no dia {shift_date}.",
        },

        'request_responded': {
            'kind': Kind.INFO,
            'title': "Requisição respondida",
            'body':
                "{sender_name} {response} {{{receiver_id}}} {verb} DE {req_type}."
                "{start_hour} - {end_hour} no centro {shift_center} no dia {shift_date}.",
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

        # # Fill defaults for optional phrases to avoid KeyError in format()
        # defaults = {
        #     "cta_sentence": "",
        #     "reason_sentence": "",
        #     "requester_name": "",
        #     "responder_name": "",
        #     "receiver_name": "",
        #     "request_type": "",
        #     "shift_label": "",
        #     "start_hour": "",
        #     "end_hour": "",
        #     "link": "",
        # }
        # data = {**defaults, **context}

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

    def rerender(self):
        """
        Re-render title/body from stored template + context.
        Useful if you changed TEMPLATE_REGISTRY copy or translations.
        """
        # TODO: apply and add the you/name logic here
        if not self.template_key:
            return
        tmpl = self.TEMPLATE_REGISTRY.get(self.template_key)
        if not tmpl:
            return
        data = self.context or {}
        self.title = tmpl['title'].format(**data)
        self.body  = tmpl['body'].format(**data)
        self.kind  = tmpl['kind']
        self.save(update_fields=['title', 'body', 'kind'])