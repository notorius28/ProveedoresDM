# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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