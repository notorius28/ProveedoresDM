# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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