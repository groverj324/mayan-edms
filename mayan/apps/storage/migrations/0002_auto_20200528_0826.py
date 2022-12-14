from django.db import migrations


def code_copy_entries(apps, schema_editor):
    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )
    StorageSharedUploadedFile = apps.get_model(
        app_label='storage', model_name='StorageSharedUploadedFile'
    )

    for entry in SharedUploadedFile.objects.using(alias=schema_editor.connection.alias).all():
        StorageSharedUploadedFile.objects.create(
            file=entry.file, filename=entry.filename,
            datetime=entry.datetime
        )
        entry.delete()


def code_copy_entries_reverse(apps, schema_editor):
    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )
    StorageSharedUploadedFile = apps.get_model(
        app_label='storage', model_name='StorageSharedUploadedFile'
    )

    for entry in StorageSharedUploadedFile.objects.using(alias=schema_editor.connection.alias).all():
        SharedUploadedFile.objects.create(
            file=entry.file, filename=entry.filename,
            datetime=entry.datetime
        )
        entry.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('storage', '0001_initial'), ('common', '0015_auto_20200501_0631')
    ]

    operations = [
        migrations.RunPython(
            code=code_copy_entries,
            reverse_code=code_copy_entries_reverse
        )
    ]
