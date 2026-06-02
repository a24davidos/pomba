from django.db import migrations, models
from django.db.models import Max


def crear_versiones_actuales(apps, schema_editor):
    """Para cada ítem de audio que ya tenga un archivo, crea un ItemVersion marcado como activo
    apuntando al archivo actual de Item. Así todos los ítems de audio participan del nuevo modelo."""
    Item = apps.get_model('items', 'Item')
    ItemVersion = apps.get_model('items', 'ItemVersion')

    audio_items = Item.objects.filter(
        tipo='archivo',
        eliminado=False,
    ).exclude(file__isnull=True).exclude(file='')

    for item in audio_items:
        if not (item.mime_type or '').startswith('audio/'):
            continue
        max_num = item.versiones.aggregate(Max('numero'))['numero__max'] or 0
        ItemVersion.objects.create(
            item=item,
            numero=max_num + 1,
            file=str(item.file),
            tamano_bytes=item.tamano_bytes or 0,
            mime_type=item.mime_type or '',
            metadatos=item.metadatos or {},
            es_actual=True,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0010_add_item_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemversion',
            name='es_actual',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(crear_versiones_actuales, migrations.RunPython.noop),
    ]
