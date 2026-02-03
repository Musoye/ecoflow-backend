# Generated manually - Link alerts to cameras

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0003_carbonlog_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='camera',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='alerts',
                to='lims.camera'
            ),
        ),
        # Set existing alerts to camera_id=1
        migrations.RunSQL(
            "UPDATE lims_alert SET camera_id = 1 WHERE camera_id IS NULL;",
            reverse_sql="UPDATE lims_alert SET camera_id = NULL;"
        ),
    ]
