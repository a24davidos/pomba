from django.utils import timezone

from django.core.exceptions import ValidationError
from .models import Item


class ItemService:

    # Validamos que no se den bucles en el arbol (Por ejemplo mover una carpeta dentro de si misma)
    @staticmethod
    def check_cycle(item, nueva_carpeta_padre):
        actual = nueva_carpeta_padre

        while actual:
            if actual.id == item.id:
                return True
            actual = actual.padre

        return False

    # Aplicamos reglas de almacenamietno
    @staticmethod
    def aplicar_reglas_almacenamiento(item, usuario=None, fichero=None):

        # Si es carpeta, no tiene datos de archivo
        if item.tipo == Item.Tipo.CARPETA:
            item.ruta = None
            item.tamano_bytes = None
            item.mime_type = None
            return item

        # Si es archivo, debe existir archivo
        if not fichero:
            raise ValidationError("Archivo requerido")

        item.ruta = f"uploads/{usuario.id}/{fichero.name}"
        item.tamano_bytes = fichero.size
        item.mime_type = fichero.content_type

        return item

    @staticmethod
    def obtener_breadcrumb(usuario, carpeta_id):
        ruta_base = [{"id": None, "label": "Inicio"}]
        
        # Si no hay ID o es la raíz, devolvemos solo inicio
        if not carpeta_id:
            return ruta_base

        try:
            # IMPORTANTE: Asegurarnos de que el ID sea un entero para que coincida con el diccionario
            id_actual = int(carpeta_id)
        except (ValueError, TypeError):
            return ruta_base

        # 1. Traemos TODAS las carpetas (incluidas las eliminadas)
        # Si no traemos las eliminadas, el breadcrumb fallará dentro de la papelera
        carpetas = Item.objects.filter(
            usuario=usuario, 
            tipo='carpeta'
        ).values('id', 'nombre', 'padre_id')

        # 2. Mapa en memoria
        mapa_carpetas = {c['id']: c for c in carpetas}

        # 3. Construcción del camino
        nodos_padre = []

        while id_actual is not None:
            carpeta = mapa_carpetas.get(id_actual)
            
            if not carpeta:
                # Si no encontramos la carpeta en el mapa, 
                # puede ser que el ID no exista o no sea del usuario
                break
            
            nodos_padre.append({
                "id": carpeta['id'],
                "label": carpeta['nombre']
            })
            
            # Saltamos al padre
            id_actual = carpeta['padre_id']

        # 4. Invertimos para ir de Raíz -> Hijo
        ruta_base.extend(reversed(nodos_padre))
        return ruta_base

    # GUARDADO CENTRALIZADO
    @staticmethod
    def guardar_item(item):
        item.full_clean()
        item.save()
        return item

    # CREAR ITEM
    @staticmethod
    def crear_item(usuario, datos, fichero=None): 
        
        # Creamos la instancia del modelo con los datos del formulario
        nuevo_item = Item(usuario=usuario, **datos)

        # Pasamos el archivo  a las reglas de almacenamiento
        nuevo_item = ItemService.aplicar_reglas_almacenamiento(
            item=nuevo_item,
            usuario=usuario,
            fichero=fichero # Aquí le pasas el objeto que recibiste arriba
        )
        
        return ItemService.guardar_item(nuevo_item)

    # MOVER ITEM
    @staticmethod
    def mover_item(item, nueva_carpeta_padre):

        if ItemService.check_cycle(item, nueva_carpeta_padre):
            raise ValidationError("No puedes crear ciclos")

        item.padre = nueva_carpeta_padre

        return ItemService.guardar_item(item)
    
    # Método Soft Delete - Mandar a la papelera
    @staticmethod
    def mover_a_papelera(ids, usuario):
        ahora = timezone.now()
        
        # 1. Traemos los items que no estan en la papelera
        todos_los_items = Item.objects.filter(usuario=usuario, eliminado=False).values('id', 'padre_id')
        
        # 2. Creamos un mapa de adyacencia: {padre_id: [lista_de_hijos]}
        # Esto facilita buscar los hijos de cualquier carpeta en memoria
        hijos_por_padre = {}
        for item in todos_los_items:
            p_id = item['padre_id']
            if p_id not in hijos_por_padre:
                hijos_por_padre[p_id] = []
            hijos_por_padre[p_id].append(item['id'])

        # 3. Función recursiva pero SOLO sobre el diccionario de Python (instantánea)
        ids_totales = set()

        def buscar_descendientes_en_memoria(id_actual):
            # Buscamos en el diccionario, no en la BD
            hijos = hijos_por_padre.get(id_actual, [])
            for h_id in hijos:
                if h_id not in ids_totales:
                    ids_totales.add(h_id)
                    buscar_descendientes_en_memoria(h_id)

        # 4. Procesamos los IDs iniciales
        for root_id in ids:
            ids_totales.add(root_id)
            buscar_descendientes_en_memoria(root_id)

        # 5. Aplicamos el update
        return Item.objects.filter(id__in=ids_totales, usuario=usuario).update(
            eliminado=True, 
            fecha_eliminado=ahora
        )