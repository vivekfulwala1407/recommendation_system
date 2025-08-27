from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterField(
            model_name='post',
            name='likes',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='comments', 
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='shares',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='post',
            name='interactions',
            field=models.JSONField(default=dict),
        ),
    ]