# Generated migration for LearnedKnowledge models

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('HumeAiTwilio', '0001_initial'),  # Adjust based on your last migration
    ]

    operations = [
        migrations.CreateModel(
            name='LearnedKnowledge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(db_index=True, unique=True)),
                ('answer', models.TextField()),
                ('source', models.CharField(db_index=True, default='live_call', max_length=50)),
                ('metadata', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Learned Knowledge',
                'verbose_name_plural': 'Learned Knowledge',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CallConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_sid', models.CharField(db_index=True, max_length=50, unique=True)),
                ('customer_phone', models.CharField(max_length=20)),
                ('agent_id', models.CharField(blank=True, max_length=50, null=True)),
                ('conversation_data', models.JSONField(help_text='Full conversation transcript')),
                ('qa_pairs_count', models.IntegerField(default=0)),
                ('duration_seconds', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(default='completed', max_length=20)),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Call Conversation',
                'verbose_name_plural': 'Call Conversations',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TrainingDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('file_path', models.CharField(max_length=500)),
                ('file_type', models.CharField(max_length=10)),
                ('content', models.TextField(help_text='Extracted text content')),
                ('chunks_count', models.IntegerField(default=0)),
                ('uploaded_by', models.CharField(blank=True, max_length=100, null=True)),
                ('uploaded_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Training Document',
                'verbose_name_plural': 'Training Documents',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='learnedknowledge',
            index=models.Index(fields=['question'], name='HumeAiTwil_questio_idx'),
        ),
        migrations.AddIndex(
            model_name='learnedknowledge',
            index=models.Index(fields=['source', '-created_at'], name='HumeAiTwil_source_idx'),
        ),
    ]
