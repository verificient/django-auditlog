from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auditlog", "0006_object_pk_index"),
    ]

    operations = [
        migrations.AlterField(
            model_name="logentry",
            name="object_pk",
            field=models.CharField(
                verbose_name="object pk", max_length=255
            ),
        ),
        migrations.AddField(
            model_name="logentry",
            name="remote_addr",
            field=models.GenericIPAddressField(
                null=True, verbose_name="remote address", blank=True
            ),
        ),
       migrations.AddField(
            model_name="logentry",
            name="additional_data",
            field=models.JSONField(null=True, blank=True),
        ),
    ]
