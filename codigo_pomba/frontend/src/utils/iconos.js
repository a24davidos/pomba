const ICONO_DEFECTO = 'pi-file text-surface-400'

export function obtenerIcono(item) {
  if (!item) return ICONO_DEFECTO
  if (item.tipo === 'carpeta') return 'pi-folder text-yellow-500'

  const mime = (item.mime_type || '').toLowerCase()

  //Audio, video e imagen
  if (mime.startsWith('image/')) return 'pi-image text-purple-400'
  if (mime.startsWith('video/')) return 'pi-video text-sky-400'
  if (mime.startsWith('audio/')) return 'pi-headphones text-pink-400'


  //PDFs, Word etc
  if (mime === 'application/pdf')
    return 'pi-file-pdf text-red-400'
  if (mime === 'application/msword' || mime.includes('wordprocessingml'))
    return 'pi-file-word text-blue-500'
  if (['vnd.ms-excel', 'spreadsheetml', 'text/csv', 'application/csv'].some(f => mime.includes(f)))
    return 'pi-file-excel text-green-500'

  //Comprimidos
  if (['zip', 'tar', 'rar', '7z', 'gzip', 'compress'].some(f => mime.includes(f)))
    return 'pi-box text-amber-500'

  //Archivos estilo programador jejeje
  if (['application/json', 'text/html', 'text/css', 'javascript', 'xml'].some(f => mime.includes(f)))
    return 'pi-code text-emerald-500'

  if (mime.startsWith('text/'))
    return 'pi-file-edit text-surface-500'

  return ICONO_DEFECTO
}
