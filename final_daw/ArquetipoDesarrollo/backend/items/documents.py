from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import Item


@registry.register_document
class ItemDocument(Document):

    # Búsqueda principal
    nombre = fields.TextField(analyzer='spanish')
    nombre_raw = fields.KeywordField()

    # Filtros
    tipo = fields.KeywordField()
    mime_type = fields.KeywordField()
    usuario_id = fields.IntegerField()
    padre_id = fields.IntegerField()
    eliminado = fields.BooleanField()
    favorito = fields.BooleanField()

    # Contenido texto extraído (TXT, MD, CSV)
    contenido = fields.TextField(analyzer='spanish')

    # Metadatos de audio 
    meta_artista = fields.TextField()
    meta_album = fields.TextField()
    meta_anno = fields.IntegerField()
    meta_genero = fields.KeywordField()

    # Metadatos de imagen
    meta_camara = fields.KeywordField()

    # Fechas y tamaño para filtros avanzados
    fecha_creacion = fields.DateField()
    tamano_bytes = fields.LongField()

    class Index:
        name = 'items'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        model = Item
        fields = []

    # Estos métodos son llamados tanto al indexar manualmente (ItemService)
    # como al reconstruir el índice con: manage.py search_index --rebuild

    def prepare_nombre_raw(self, instance):
        return instance.nombre

    def prepare_usuario_id(self, instance):
        return instance.usuario_id

    def prepare_padre_id(self, instance):
        return instance.padre_id

    def prepare_contenido(self, instance):
        return instance.metadatos.get('contenido') or ''

    def prepare_meta_artista(self, instance):
        return instance.metadatos.get('artista') or ''

    def prepare_meta_album(self, instance):
        return instance.metadatos.get('album') or ''

    def prepare_meta_anno(self, instance):
        return instance.metadatos.get('año')

    def prepare_meta_genero(self, instance):
        return instance.metadatos.get('genero') or ''

    def prepare_meta_camara(self, instance):
        return instance.metadatos.get('camara_modelo') or ''
