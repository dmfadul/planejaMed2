from django.db import models
from core.models import User
from django.utils import timezone
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

# ------------------- Template Registry ---------------------------------
# Placeholders correspond to context keys

    TEMPLATE_REGISTRY = {
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
                "no centro {shift_center} no dia {shift_date}. "
                "Aperte Cancelar para cancelar a solicitação.",
        },

        # “Your request is created and waiting for a response.”
        'request_pending_donation_asked_for': {
            'kind': Kind.ACTION,
            'title': "Requisição de doação pendente",
            'body':
                "{sender_name} solicitou para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {shift_center} no dia {shift_date}.",
        },

        'request_pending_donation_offered': {
            'kind': Kind.ACTION,
            'title': "Requisição de doação pendente",
            'body':
                "{sender_name} ofereceu para {{{receiver_id}}} a doação dos horários: "
                "{start_hour} - {end_hour} no centro {shift_center} no dia {shift_date}.",
        },

        'request_pending_exclusion': {
            'kind': Kind.ACTION,
            'title': "Requisição de exclusão pendente",
            'body':
                "{sender_name} solicita a exclusão dos horários de {excludee_name}: "
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
