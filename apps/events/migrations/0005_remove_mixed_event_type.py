from django.db import migrations, models


def delete_mixed_events(apps, schema_editor):
    Event = apps.get_model("events", "Event")
    Event.objects.filter(event_type="mixed").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_change_receipt_to_filefield"),
    ]

    operations = [
        migrations.RunPython(delete_mixed_events, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="event",
            name="event_type",
            field=models.CharField(
                choices=[
                    ("payment", "Arrecadação"),
                    ("potluck", "Lanche Partilhado"),
                    ("presence", "Confirmação de Presença"),
                ],
                default="payment",
                max_length=20,
                verbose_name="Tipo do Evento",
            ),
        ),
    ]
