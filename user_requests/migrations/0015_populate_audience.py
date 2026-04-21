from django.db import migrations

def populate_audience(apps, schema_editor):
    UserRequest = apps.get_model('user_requests', 'UserRequest')

    UserRequest.objects.filter(
        requestee__isnull=False,
        audience__isnull=True
    ).update(audience='individual')

    UserRequest.objects.filter(
        requestee__isnull=True,
        audience__isnull=True
    ).update(audience='admins')


def reverse_populate_audience(apps, schema_editor):
    UserRequest = apps.get_model('user_requests', 'UserRequest')
    UserRequest.objects.update(audience=None)


class Migration(migrations.Migration):

    dependencies = [
        ('user_requests', '0014_userrequest_audience'),
    ]

    operations = [
        migrations.RunPython(populate_audience, reverse_populate_audience),
    ]