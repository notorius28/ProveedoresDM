# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.30] 2025/03/28

## Correcciones

- Para el "Proveedor 48 Novedades", se soluciona un error para cuando el formato es "LP VINILO" más una variante

## [1.0.29] 2025/01/22

## Correcciones

- Para el "Proveedor 48 Novedades", se elimina el valor de la columna "Estilo" procedente del fichero del proveedor

## [1.0.28] 2025/01/11

## Correcciones

- Corregido un error en el parámetro "patronFormato" que daba problemas con el formato 2LP para el "Proveedor 48 Novedades". Pendiente de revisar ese patrón para el resto de procesadores.

## [1.0.27] 2025/01/07

## Correcciones

- Para el "Proveedor 23 Novedades", se corrige un fallo que no permitía procesar el fichero si no incluía los encabezados de los campos

## [1.0.26] 2024/11/05

## Correcciones

- Para el "Proveedor 17", se reemplazan los caracteres tipo ″ por "

## [1.0.25] 2024/10/08

## Novedades

- Añadido el "Proveedor 48 prelanzamientos", que permite además cargar varios ficheros a la vez y que los consolide en un único fichero excel con tantas pestañas como ficheros subidos, para su posterior procesamiento. Este proveedor permite dos diseños de registro: uno con la fecha de lanzamiento en la cabecera y otro con la fecha de lanzamiento en una columna.
- El listado de proveedores se ordena alfabéticamente

## Notas de Desarrollo

- Añadida una propiedad DateOnTab para marcar qué proveedores envían la fecha de lanzamiento en el título de la pestaña y no dentro de la hoja
- Añadida libreria xlsxwriter a los requisitos

## [1.0.24] 2024/09/15

## Correcciones

- Para el "Proveedor 11 fondo", se soluciona el problema por el que seguían incluyendose en la exportación filas con caracteres extraños
- Para el "Proveedore 17 novedades", se soluciona un error para pestañas que no contenían ninguna referencia
- Reemplazado "MINILP" como "MiniLP" en el diccionario de formatos

## [1.0.23] 2024/09/10

## Correcciones

- Para el "Proveedor 11 fondo", se descartan de la exportación las filas que contienen caracteres extraños (que no son ASCII, como cirílicos o japoneses)

## [1.0.22] 2024/09/09

## Correcciones

- Para el "Proveedor 11 fondo", se controlan posibles errores derivados de valores inesperados en el campo "Formato"
- Se mejoran algunas funciones para mostrar el error exacto que se produce en una celda en concreto
- VVAA se traduce a Varios Artistas
- Nuevos mapeos del campo formato en el fichero de Formatos

## [1.0.21] 2024/09/02

## Correcciones

- Añadida una función para todos los ficheros que controla que, en el precio, se normalice el símbolo del decimal cuando aparezcan tanto puntos como comas (como ocurre en prov 17)
- Añadidos formateados no mapeados del proveedor 11

## [1.0.20] 2024/08/31

## Correcciones

- Se controlan posibles errores en ficheros multipestaña, cuando la fecha de una pestaña no cumpla con uno de los formatos predeterminados (por ejemplo, "6 septiembre24")
- Se controla un error de filas vacías (NA) en el comienzo del prov 23 novedades

## [1.0.19] 2024/08/29

## Novedades

- Añadida configuración al proveedor 42 novedades para poder trabajar dos estructuras: una de 11 columnas y otra de 13 columnas
- Añadida propiedad a cada procesador de proveedor para indicar si pueden ser multipestaña o no. En caso de que un proveedor esté configurado como que no es multipestaña y el excel contiene varias, se procesaría solo la primera (por ejemplo, prov 42 novedades)

## [1.0.18] 2024/08/25

## Novedades
- Añadida validación para comprobar que la estructura del fichero excel coincide con la definición de campos para cada proveedor. Si el número de columnas no coincide, muestra un mensaje de error

## [1.0.17] 2024/08/23

## Novedades
- Para todos los proveedores, se asigna la referencia como código de barras si este último dato viene vacío

## Correcciones
- Modificado el método de lectura de los excel para que no convierta los códigos de barras a decimales cuando hay un valor o más vacío para ese dato

## [1.0.16] 2024/08/01

## Correcciones

- En el "Proveedor 84 Novedades", se fuerza que el decimal en el precio se transforme a coma, ya que no lo interpreta correctamente del fichero excel original y lo lee como punto.

## [1.0.15] 2024/07/31

## Novedades

- Añadida extracción de la fecha de lanzamiento para cadenas de texto con sólo un artículo "de". Por ejemplo, "24 de Junio 2022". Este formato aplica al "Proveedor 48 Novedades"

## [1.0.14] 2024/07/28

## Novedades

- Añadida extracción de la fecha de lanzamiento para cadenas de texto con artículo "de". Por ejemplo, "15 de Junio de 1984". Este formato aplica al "Proveedor 84 Novedades"

## Correcciones

- Corregido "Proveedor 84 Novedades" para evitar que devuelva error cuando hay una fila vacía (N/A)
- Añadido un control para que no devuelva error en aquellos proveedores que procesan solo los lanzamientos recientes si el fichero excel no contiene ningún lanzamiento que cumpla esa condición.

## [1.0.13] 2024/07/24

## Novedades

- Añadido "Proveedor 84 Novedades"
- Añadidos los Comentarios del proveedor para el "Proveedor 11 Novedades"

## [1.0.12] 2024/07/20

## Novedades

- Añadido "Proveedor 11 Fondo"
- Añadido "Proveedor 48 Fondo"

## [1.0.11] 2024/07/18

## Novedades

- Añadido "Proveedor 11 Novedades"
- Añadido "Proveedor 48 Novedades"

## [1.0.10] 2024/06/27

## Correcciones

- Refactorización de codigo orientada a un tratamiento más eficiente de los ficheros multipestaña
- Se muestra una advertencia para los ficheros multipestaña, independientemente del procesador

## Otros

- Añadido dockerfile

## [1.0.9] 2024/06/09

## Novedades

- En los códigos de barras, se rellena con ceros a la izquierda hasta los 13 caracteres. Esta transformación solo aplica a los procesados en los que los ficheros contienen un código de barras y no se copia el valor de la Referencia.

### Correcciones

- En el procesador del prov 23, no se mostraban datos si el fichero contenía varías filas con los encabezados

## [1.0.8] 2024/06/06

## Novedades

- Añadido el procesador para ficheros completos del proveedor 23

### Correcciones

- Algunos proveedores no mostraban en pantalla los registros que no tienen coincidencia por formato en el diccionario

## [1.0.7] 2024/06/04

### Correcciones

- En los ficheros 17 multipestaña, se mantiene el Sello del excel original
- Solucionado error de procesamiento en fichero 17 monopestaña

## [1.0.6] 2024/06/04

### Correcciones

- Mejorada la velocidad de procesamiento en el proveedor 17 multipestaña, donde solo se procesan las pestañas con fecha de los últimos 30 días en adelante (incluidas fechas futuras)
- Solucionado errores al convertir la fecha del texto de la pestaña del proveedor 17

## [1.0.5] 2024/05/29

### Novedades 

- Añadida versión inicial del tratamiento de ficheros multipestaña o multitabs, incorporado al procesador 17

### Correcciones

- En el proveedor 17 multipestaña, la fecha se toma del nombre de la pestaña en lugar de la primera celda
- Solucionado un error al obtener la fecha de un texto, donde no se interpretaba como año textos como "23" o "24"

## [1.0.4] 2024/05/25

### Novedades 

- Añadido el __Proveedor 23 Novedades__
- Añadido menú lateral con opciones para consultar diccionarios de formatos y artistas
- Añadido esta sección de "Notas de Versión"
- Los registros que no tienen un formato en el diccionario se muestran en una vista previa
- Contadores de filas para fichero sin procesar y procesado

### Correcciones

- Pequeños arreglos

## [1.0.3]

### Novedades

- Modificado el proveedor 42 para mostrar solo los lanzamientos de los últimos 30 días
- Ahora se extrae, del formato, la edición o variación del artículo para añadirla al título entre paréntesis precedido de EDICIÓN