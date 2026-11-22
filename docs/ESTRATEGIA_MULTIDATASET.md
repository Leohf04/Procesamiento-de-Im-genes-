# Estrategia multidataset del Equipo 2

**Estado:** estrategia aprobada para implementación; acceso y anotaciones aún en validación.  
**Rama:** `urban-models-and-benchmark`  
**Regla:** no iniciar entrenamiento hasta aprobar los preflights de cada fuente y el mapeo de etiquetas.

## 1. Combinación seleccionada

| Dataset | Rol | Tareas que se le asignan | Limitaciones que deben respetarse |
|---|---|---|---|
| **A2D2 (Audi)** | Dominio real principal | Semántica urbana y, tras decodificar el formato, instancias/detección de participantes. Fuente para contrastar el dominio sintético. | Acceso anónimo S3 ya confirmado; estructura de muestra localizada, pero el emparejamiento/decodificación de anotaciones aún no está aprobado. Licencia CC BY-ND 4.0. No se han confirmado atributos por imagen para estratificar día/noche/lluvia/niebla. |
| **UrbanSyn** | Fuente sintética principal para entrenar y comparar tareas 2D | Segmentación semántica de 19 clases, panoptic instances de clases dinámicas y cajas 2D. | No tiene clase específica de carril. Panoptic/bbox se limitan a objetos dinámicos. No proporciona una partición de condiciones meteorológicas reales. La licencia publicada por HF y los términos del sitio oficial no coinciden literalmente; resolver antes de redistribuir o publicar derivados. |
| **SHIFT (SysCV)** | Evaluación de cambios de dominio y complemento de etiquetas | RGB, semántica, detección 2D e instance segmentation 2D, según grupos disponibles. Separar condiciones/variantes del dominio para pruebas de robustez. | Dataset sintético; no equivale a evaluación de campo real. Acceso al servidor oficial pendiente. La cabecera del descargador oficial declara CC BY-NC-SA 4.0. |

Fuentes primarias: [A2D2](https://a2d2-dataset.github.io/), [A2D2 paper](https://arxiv.org/abs/2004.06320), [UrbanSyn](https://urbansyn.org/), [UrbanSyn en Hugging Face](https://huggingface.co/datasets/UrbanSyn/UrbanSyn), [SHIFT DevKit](https://github.com/SysCV/shift-dev).

## 2. Separación de experimentos

1. **Semántica:** entrenar/ajustar DeepLabV3+ con etiquetas semánticas verificadas de UrbanSyn y A2D2. Informar métricas por dataset; no concatenar máscaras con IDs distintos sin un adaptador y una taxonomía documentados.
2. **Instancias:** entrenar/evaluar Mask R-CNN usando panoptic de UrbanSyn convertido a máscaras por instancia y las anotaciones SHIFT/A2D2 solo después de validar su formato. Mantener el identificador de instancia local a cada imagen.
3. **Detección:** usar cajas 2D de UrbanSyn y SHIFT. Las cajas 3D de A2D2 solo se convertirán a 2D si se dispone de calibración y proyección verificadas; no tratarlas como cajas 2D nativas.
4. **Robustez:** SHIFT será el conjunto de estrés sintético para clima/iluminación cuando se comprueben sus metadatos y archivos. A2D2 permitirá una evaluación real general, pero no se afirmará una comparación real día/noche/lluvia/niebla sin atributos verificables.
5. **Carriles y señales:** UrbanSyn sí etiqueta traffic sign semántico, pero no ofrece instancia/caja de señales según su ficha. No se ha certificado todavía una clase lane-marking común a los tres. Las métricas de carriles solo se publicarán si una fuente contiene esa etiqueta explícita y su decoder se valida.

## 3. Ontología común provisional

La taxonomía canónica no se fijará hasta inspeccionar los mapas de clases oficiales de A2D2 y SHIFT. Se propone esta correspondencia conceptual, no una equivalencia automática de IDs:

- Personas: `person/pedestrian`.
- Ciclistas: conservar `cyclist` frente a `bicycle` y `rider`; solo agrupar cuando la definición de etiqueta sea equivalente.
- Vehículos: conservar al menos `car`, `truck`, `bus`, `motorcycle`, `bicycle`, `train` cuando existan.
- Infraestructura: `road`, `sidewalk`, `traffic sign`, `traffic light`, `road marking/lane marking` solo si están anotadas.
- Fondo/no etiquetado/ignore: mapear explícitamente a `ignore_index`; nunca confundir ID 0 con fondo sin consultar la fuente.

Se guardará por muestra el dataset de origen, split, secuencia, frame, condición/metadata disponible, versión del mapa de clases y checksum.

## 4. Protocolo de particiones y comparabilidad

- Respetar los splits oficiales. Cuando existan secuencias, separar por secuencia/escena para evitar fuga de frames correlacionados.
- No usar el split de validación para ajustar umbrales y reportarlo después como test.
- Reportar por separado: (a) entrenamiento y validación dentro de UrbanSyn, (b) evaluación real en A2D2, (c) evaluación de domain shift en SHIFT.
- Añadir un experimento de transferencia sintético→real solo cuando los mapeos de clases sean compatibles; no comparar directamente mIoU de taxonomías diferentes.
- No aplicar augmentations sintéticas al conjunto de test salvo en un protocolo de corrupción separado, con severidad y semilla registradas.
- Las condiciones artificiales (gamma, exposición, blur, lluvia/niebla simuladas) se reportan como corruptions sintéticas y no como observaciones reales.

## 5. Métricas

- Semántica: IoU por clase, mIoU y matriz de confusión.
- Instancias: Mask AP/AP50/AP75 y AP por clase; Box AP se reporta aparte.
- Detección: mAP y AP por clase/IoU.
- Robustez: cambio absoluto/relativo de mIoU, Mask AP y mAP respecto al split limpio, desglosado por condición y severidad.
- Rendimiento: FPS, latencia media/mediana/p95/p99, resolución, batch size, hardware y precisión numérica.
- Registrar falsos positivos/negativos y errores cualitativos por categoría y condición.

## 6. Puertas obligatorias antes de entrenar

1. **A2D2:** corregir el preflight de estructura, descargar una muestra pequeña desde S3 remoto, inspeccionar JSON/PNG y class_list, decodificar semántica/instancias y comprobar correspondencia de tamaños/clases. No considerar PASS de anotaciones por el mero listado del bucket.
2. **UrbanSyn:** corregir el emparejamiento por identificador numérico (los archivos se llaman `rgb_0001`, `ss_0001`, `panoptic_0001`, `bbox2d_0001`); descargar como máximo cuatro muestras y validar RGB, máscaras, IDs, JSON y licencia.
3. **SHIFT:** comprobar endpoints oficiales sin descargar archivos grandes; después descargar un subconjunto pequeño (vista front, split y frecuencia acotados) de RGB + semseg + instance labels, verificar estructura y metadatos de condición.
4. **Adaptadores:** implementar pruebas unitarias de cada conversión al esquema común, incluyendo ignore labels, categorías ausentes y máscaras de instancias.
5. **Preflight global:** producir un manifiesto con conteos por clase/split/condición, imágenes sin etiqueta, tamaños, checksums y estado de licencia.
6. Solo entonces habilitar configuración de entrenamiento. Hasta ese momento `RUN_TRAINING=False`.

## 7. Licencias y atribución

- **A2D2:** CC BY-ND 4.0; atribuir a Audi AG y revisar restricciones antes de redistribuir transformaciones o derivados.
- **UrbanSyn:** HF etiqueta CC BY-SA 4.0, mientras el sitio oficial describe CC BY-NC-SA 4.0. Tratar como revisión pendiente y solicitar aclaración al proveedor antes de redistribución/uso externo.
- **SHIFT:** el descargador oficial declara CC BY-NC-SA 4.0; uso no comercial y atribución/compartir bajo términos aplicables.
- No subir imágenes, máscaras, archivos de etiquetas, ni checkpoints derivados al repositorio Git privado. Conservar solo código, manifiestos agregados y métricas permitidas.

## 8. Estado actual comprobado (2026-11-22)

- A2D2 run [44965195376](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44965195376): **falló la búsqueda del par** porque el script anterior asumía un directorio `/label/`. Sí confirmó listado anónimo del bucket y descubrió las raíces `camera_lidar_semantic/` y `camera_lidar_semantic_instance/`. No descargó ni validó anotaciones.
- UrbanSyn run [44963969661](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44963969661): **falló el índice de emparejamiento**, no el acceso remoto. Encontró 7.539 archivos en cada modalidad, pero buscaba stems idénticos pese a los prefijos distintos. Se corrigió para emparejar por ID numérico.
- SHIFT: preflight de endpoints añadido; aún no ejecutado.
- Ningún dataset completo descargado. No hay entrenamiento, checkpoints ni resultados experimentales nuevos.
