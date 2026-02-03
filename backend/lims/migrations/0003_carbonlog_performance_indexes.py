# Generated manually for performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lims', '0002_carbonlog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carbonlog',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterModelOptions(
            name='carbonlog',
            options={'ordering': ['-timestamp']},
        ),
        migrations.AddIndex(
            model_name='carbonlog',
            index=models.Index(fields=['-timestamp', 'zone'], name='lims_carbon_timesta_idx'),
        ),
    ]
