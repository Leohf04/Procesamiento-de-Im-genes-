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


## 9. Actualización de validación remota (2026-11-22)

### A2D2 — semántica confirmada a nivel de muestra

- Workflow [44971559558](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971559558) confirmó descarga anónima de una imagen RGB y su máscara semántica desde S3: 1920×1208, dimensiones coincidentes, máscara RGB con 21 colores observados.
- Workflow [44971681934](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971681934) localizó y leyó `camera_lidar_semantic/class_list.json`: 55 entradas de color/nombre. Los colores de la muestra se mapearon a clases como Car 1–4, Bicycle 1–4, Pedestrian 1–3, Truck 1–3, Solid line, Sidewalk y Sky.
- La muestra confirma **etiquetas semánticas A2D2** y contiene subclases de participantes que el paper describe como anotaciones de instancia derivadas de la semántica. No se encontró un PNG independiente bajo `camera_lidar_semantic_instance/.../label/cam_front_center/`; la extracción de instancias desde subclases/connected components debe validarse antes de entrenar Mask R-CNN.
- El mapa de clases se ha leído, pero el adaptador final a la ontología común aún no existe. No se ha validado cobertura completa de las 55 clases ni todos los splits.

### UrbanSyn — preflight de muestra aprobado

- Workflow [44971557432](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971557432) terminó success.
- Se encontraron 7.539 IDs con los cuatro archivos correspondientes (RGB, semántica, panoptic y bbox2D). Se descargaron solo dos muestras.
- Las muestras RGB, semántica, panoptic y JSON bbox se pudieron abrir; resolución 2048×1024. Las máscaras semánticas almacenadas como RGB triplicado se redujeron a un canal de IDs. Se detectaron IDs semánticos 0–19 en las dos muestras; canal azul panoptic con IDs dinámicos, por ejemplo 11, 12 y 13.
- Esto aprueba solo una muestra remota de estructura/decodificación, no todos los 7.539 pares ni la calidad de las anotaciones.
- Licencia aún bloqueada por discrepancia: Hugging Face etiqueta CC BY-SA 4.0 y la página oficial describe CC BY-NC-SA 4.0. No redistribuir ni publicar derivados hasta aclararlo.

### SHIFT — espejo parcial

- El endpoint oficial `dl.cv.ethz.ch` falló en GitHub Actions con error DNS/NXDOMAIN (run [44971481786](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971481786)); además existe un issue público del DevKit reportando la misma indisponibilidad.
- Se encontró un espejo público `KevinConnorLee/SHIFT`. El preflight [44971720763](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971720763) confirmó que contiene únicamente `discrete/videos`, no rutas `continuous/`. Para `val/front` declara 15.7 GB: `img.tar` 9.62 GB, `semseg.tar` 3.56 GB, `det_insseg_2d.json` 954 MB y `seq.csv` 19.7 kB.
- `seq.csv` fue descargado y leído; contiene `start_weather_fine` y `start_timeofday_fine`, con valores como small rain, small fog, heavy fog, night y noon. Esto aporta metadata para un benchmark sintético de robustez.
- El primer preflight solo leyó prefijos de 16 MiB de los tar, insuficientes para extraer un video completo. Se implementó un nuevo lector HTTP Range que descarga como máximo el primer miembro MP4 (límite 64 MiB) de RGB y semseg; ejecución pendiente.
- El mirror declara MIT, pero el DevKit oficial declara CC BY-NC-SA 4.0. Se conserva la licencia original más restrictiva como referencia y no se asume que el mirror pueda relicenciar los datos.
- SHIFT solo se usará como **evaluación sintética**, no entrenamiento, y solo después de confirmar que el video RGB y el video semseg se decodifican y se emparejan.

### Decisiones actualizadas

- A2D2 y UrbanSyn tienen validación positiva de muestras pequeñas para semántica; UrbanSyn también tiene muestra panoptic y bbox.
- SHIFT es candidato de test sintético con metadata de clima/hora, pero su muestra visual todavía está pendiente.
- A2D2 no se dará por aprobado para Mask R-CNN hasta probar extracción de instancias a partir de las subclases (y comprobar componentes/objetos).
- Los datasets completos no se han descargado; no se ha iniciado entrenamiento ni hay métricas de modelos.


### Seguimiento del preflight SHIFT por rango — 2026-11-22

- El primer intento del lector de MP4 falló por dependencia OpenCV ausente; se añadió `opencv-python-headless` al workflow.
- El segundo intento confirmó el espejo y la metadata, pero encontró un directorio TAR inicial `./` antes del primer MP4; el lector se corrigió para saltar miembros de directorio y localizar el primer video.
- Script actualizado: `scripts/validate_shift_hf_mirror.py`, commit `5f54e40e116a2b4a516ef829d281e151d625da78`.
- Workflow de la versión corregida: [44971898884](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971898884), pendiente en el momento de actualizar este documento. No afirmar muestra SHIFT aprobada hasta ver su resultado.


## 10. Evidencia final de muestra SHIFT y ajuste A2D2 (2026-11-22)

### SHIFT — RGB y semseg decodificados desde el espejo parcial

- Workflow [44972034973](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972034973) terminó success.
- Se extrajo por HTTP Range el mismo miembro `eba5-a5bd.mp4` desde `img.tar` (16,770,040 bytes) y `semseg.tar` (5,847,998 bytes). Ambos decodificaron a 501 frames y 1280×800.
- La fila correspondiente de `seq.csv` identifica `small fog` y `sunrise/sunset`.
- **Precaución temporal:** OpenCV reportó 10 FPS para RGB y 25 FPS para semseg. Aunque coinciden nombre, dimensiones y número de frames, no se ha demostrado todavía que cada índice de frame corresponda temporalmente. El preflight ahora informa esta diferencia explícitamente; SHIFT no se habilita para métricas hasta verificar la sincronización (o definir un emparejamiento por timestamps/frame IDs).
- El espejo sigue siendo solo `discrete/videos`, 500 secuencias en `val/front`, sin `continuous/`; no es una fuente de entrenamiento. La muestra pequeña sirve para investigar la alineación y el decoder, no para certificar el split completo.

### A2D2 — interpretación de instancias

- El paper oficial de A2D2 indica que 41.277 imágenes contienen etiquetas semánticas y de instancia para 38 categorías; las instancias de participantes se derivan de la semántica y los objetos adyacentes se diferencian mediante subclases como Car 1–4, Pedestrian 1–3 y Bicycle 1–4. Los objetos no adyacentes pueden reutilizar una subclase.
- La muestra real confirma colores correspondientes a estas subclases y a líneas sólidas, entre otras clases. Por tanto, la carpeta independiente `camera_lidar_semantic_instance` no es necesaria para la primera aproximación: el adaptador puede formar máscaras por subclase y componentes conectados. Se debe probar el caso de objetos fragmentados/oclusiones y no asumir que un ID de subclase es un ID de instancia global.
- El paper reporta 12.497 frames frontales con cajas 3D. No son cajas 2D nativas; proyectarlas exige calibración y un protocolo aparte.
- El paper caracteriza la captura como diurna; aunque menciona días soleados, nublados y lluviosos, no hay metadata por imagen verificada para separar esos casos. A2D2 no cubrirá noche en el benchmark por condición.

### Implicación para el proyecto

- A2D2 puede aportar semántica, lane markings y subclases de instancias en dominio real diurno.
- UrbanSyn aporta entrenamiento/validación sintética semántica y panoptic/cajas 2D de clases dinámicas.
- SHIFT espejo puede aportar evaluación sintética de lluvia/niebla/hora solo tras resolver el desfase FPS; hasta entonces se conserva como candidato.


## 11. Estado de implementación de adaptadores y smoke tests (2026-11-22)

Se añadió `src/data_adapters.py` con decodificadores puros y explícitos:

- A2D2: lectura de `class_list.json` (`#RRGGBB -> nombre`), conversión de máscara RGB a IDs canónicos, alias de clases y extracción de instancias mediante componentes conectados para subclases como `Car 1` y `Pedestrian 2`. Las subclases no se interpretan como IDs globales; componentes pequeños se filtran con un umbral configurable.
- UrbanSyn: lectura de máscara semántica de un canal o RGB triplicado, con mapeo fuente→canónico explícito; decodificación panoptic conforme a `instance_id = R*256 + G` y `class_id = B`; generación de máscaras, etiquetas, cajas XYXY, áreas y targets Torchvision.
- El mapeo UrbanSyn fuente→canónico se proporciona explícitamente en la llamada. No se inventa una correspondencia de IDs ni se asume que coincida con A2D2.
- Los decodificadores no descargan datos ni guardan imágenes derivadas en el repositorio.

Se añadió `tests/test_multidataset_adapters.py` con pruebas sintéticas para color map/ignore, componentes de instancia, semántica RGB triplicada, panoptic RG+B y contrato de targets.

También se incorporó un smoke test de entrenamiento en CPU que construye los modelos reales DeepLabV3+ ResNet-50 y Mask R-CNN ResNet-50-FPN, ejecuta forward, calcula pérdidas y backward con etiquetas/targets sintéticos pequeños. Esto comprueba compatibilidad estructural y gradientes, **no** calidad predictiva ni entrenamiento con datasets.

### Límites pendientes antes de declarar adaptadores de dataset listos para entrenamiento

- Ejecutar los decodificadores sobre varias muestras remotas reales A2D2 y UrbanSyn, no solo fixtures sintéticos.
- Revisar el mapa completo de 55 clases A2D2 y acordar la ontología definitiva; la tabla canónica actual es una base explícita, no una equivalencia validada para todas las clases.
- Confirmar los nombres/IDs de clases UrbanSyn con su metadata oficial y construir el mapeo de clases versionado.
- Implementar loaders de archivos, manifiestos, splits reproducibles y control de muestras corruptas/ausentes.
- Verificar fragmentación/oclusiones A2D2: componentes desconectados pueden dividir un objeto parcialmente oculto en varias máscaras.
- Resolver la discrepancia de licencia de UrbanSyn antes de uso/publicación externa.
- SHIFT continúa excluido de métricas mientras no se resuelva la alineación temporal RGB/semseg (10 frente a 25 FPS).

**Estado de entrenamiento:** no iniciar todavía entrenamiento de producción. El smoke test no sustituye el preflight de datos reales. `RUN_TRAINING=False` permanece vigente.


### Loaders de manifiesto añadidos

La implementación se amplió con cuatro clases `torch.utils.data.Dataset`: `A2D2SemanticDataset`, `A2D2InstanceDataset`, `UrbanSynSemanticDataset` y `UrbanSynInstanceDataset`. Reciben manifiestos explícitos con rutas de imágenes/etiquetas; permiten redimensionado coherente (bilineal para RGB, nearest para máscaras), normalización ImageNet para DeepLab y tensores [0,1] para Mask R-CNN. Se añadieron pruebas de lectura temporal con archivos sintéticos para las cuatro clases.

El manifiesto y el mapeo fuente→canónico deben generarse/verificarse a partir de los splits y metadatos oficiales; estos loaders no descargan datasets ni inventan el split. La validación sobre muestras reales remotas y la sincronización SHIFT siguen pendientes.


## 12. Validación de adaptadores con muestras remotas reales (2026-11-22)

Se ampliaron los preflights para ejecutar `src/data_adapters.py` sobre las anotaciones efectivamente descargadas, no solo comprobar formatos:

- A2D2: el workflow [44974096279](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974096279) terminó **success**. En una muestra real frontal 1920×1208 se ejecutó el decoder semántico y el de instancias. Resultado: 55 entradas del class list; IDs canónicos observados 2, 3, 5, 6, 7, 12 y ignore 255; 66 componentes/instancias reconstruidos, con labels 3, 5, 6 y 7. Se generaron máscaras (66×1208×1920) y cajas (66×4). Es una validación de una muestra, no evidencia de cobertura global ni de exactitud de instancias bajo oclusión.
- UrbanSyn: el preflight se modificó para decodificar semántica y panoptic reales en 2 muestras, validar tamaños, labels y estructura de máscaras/cajas. La ejecución corregida [44974144391](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974144391) estaba en curso al registrar; no declarar resultado hasta verificar.
- Los workflows fallidos anteriores se debieron a import path `src` no incluido en sys.path del script; se corrigió insertando la raíz del repositorio. No fueron fallos de decodificación de anotaciones.
- El preflight A2D2 ya prueba la conversión de máscara real con los decodificadores, pero todavía solo se valida una muestra frontal. La reconstrucción por componentes puede dividir objetos ocluidos/desconectados.
- No se cambió la licencia de UrbanSyn: discrepancia oficial/HF permanece en revisión. No redistribuir.
- No se activó entrenamiento. Los subconjuntos de producción y los manifiestos reproducibles aún no están listos; `RUN_TRAINING=False`.


### Resultado final del preflight UrbanSyn (2026-11-22)

El workflow [44974144391](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974144391) terminó **success**. El mirror lista 7,539 IDs de muestra y los 7,539 tienen RGB, semseg, panoptic y bbox2D asociados por identificador. Se descargaron solo dos muestras completas (IDs 0001 y 0002), no los archivos completos:

- En ambas muestras se ejecutó `decode_urbansyn_semantic` y se comprobaron IDs/shape.
- En ambas se ejecutó `decode_urbansyn_panoptic`; la muestra 0001 produjo 5 instancias y la 0002 produjo 17, con arrays de máscara y cajas coherentes con la imagen.
- Resultado explícito del script: `UrbanSyn remote sample + project adapters PASSED`; 2 muestras reales validadas.
- Este resultado prueba integridad y ejecución de los adaptadores en esas muestras, pero no valida aún mapeo semántico canónico completo ni equivalencia de instancias/bbox2D del dataset. La licencia sigue en revisión.


## 13. Subconjuntos reproducibles — preparación por manifiestos (2026-11-22)

Se incorpora `scripts/prepare_reproducible_subsets.py` para descubrir pares remotos y generar manifiestos JSONL sin descargar imágenes ni máscaras:

```bash
python scripts/prepare_reproducible_subsets.py --dataset both --seed 2026 --max-per-split 1000 --output data/manifests
```

- UrbanSyn: indexa por identificador los cuatro recursos RGB/semseg/panoptic/bbox2D y fija el commit SHA del repositorio HF usado. El split determinista 80/10/10 usa el ID de muestra como grupo porque no hay metadata de secuencia verificada en el índice consultado.
- A2D2: empareja RGB y máscara semántica de cámara frontal desde S3 anónimo. Agrupa por secuencia antes de asignar split para impedir fuga de frames correlacionados. Registra URI, tamaño y ETag de cada objeto.
- Ambos: usa SHA-256 de `seed:group_id` para asignar train/val/test; el límite por split se aplica después con orden hash estable. La semilla por defecto es 2026 y el máximo por split 1.000.
- Salidas: `{dataset}_{train,val,test}.jsonl` y `{dataset}_manifest_summary.json`. No contienen payloads del dataset.
- Estos son **splits experimentales reproducibles**, no splits oficiales. Para A2D2, el índice S3 es mutable: ETag/tamaño permiten detectar cambios, pero no garantizan snapshot inmutable. UrbanSyn queda anclado a commit SHA.
- No se generan aún manifests de SHIFT: su alineación RGB/semseg sigue sin resolverse.
- No se habilita entrenamiento. Los manifests deben generarse en el entorno remoto autorizado y pasar auditoría de conteos, clases, dimensiones, integridad y licencias antes de consumirlos. UrbanSyn permanece en revisión de licencia.

- Workflow remoto añadido: `.github/workflows/build-reproducible-subsets.yml`. Se dispara al cambiar el generador/workflow o manualmente, construye los manifiestos en GitHub Actions (solo metadatos) y publica un artifact de 30 días; no guarda manifiestos/datos en Git.


## 9. Ontología oficial UrbanSyn verificada (2026-11-22)

La página oficial de UrbanSyn y el README publicado por el propio equipo en Hugging Face describen la misma taxonomía semántica basada en las 19 clases de entrenamiento de Cityscapes, más `unlabeled`:

| trainId | Clase fuente oficial | Uso en el proyecto |
|---:|---|---|
| 0 | road | infraestructura semántica |
| 1 | sidewalk | infraestructura semántica |
| 2 | building | contexto semántico |
| 3 | wall | contexto semántico |
| 4 | fence | contexto semántico |
| 5 | pole | contexto semántico |
| 6 | traffic light | señalización semántica |
| 7 | traffic sign | señalización semántica |
| 8 | vegetation | contexto semántico |
| 9 | terrain | contexto semántico |
| 10 | sky | contexto semántico |
| 11 | person | participante dinámico; panoptic/caja |
| 12 | rider | participante dinámico; panoptic/caja |
| 13 | car | vehículo; panoptic/caja |
| 14 | truck | vehículo; panoptic/caja |
| 15 | bus | vehículo; panoptic/caja |
| 16 | train | vehículo; panoptic/caja |
| 17 | motorcycle | vehículo; panoptic/caja |
| 18 | bicycle | participante dinámico; panoptic/caja |
| 19 | unlabeled | ignore, no clase de entrenamiento |

El sitio oficial especifica que panoptic cubre Person, Rider, Car, Truck, Bus, Train, Motorcycle y Bicycle; las cajas 2D cubren objetos dinámicos hasta 110 m y con tamaño superior a 150 píxeles. No hay clase dedicada a carril/lane marking en esta taxonomía. Esta tabla es el mapeo fuente→nombre verificado; la asignación a una ontología reducida del proyecto debe seguir siendo explícita y versionada, sin confundir `rider` con `bicycle`.

### Licencia: criterio operativo

La fuente primaria del proveedor (urbansyn.org) indica **CC BY-NC-SA 4.0** y declara que el dataset se proporciona para investigación y uso comercial sujeto a esos términos; la página del mirror Hugging Face muestra **CC BY-SA 4.0**, sin la cláusula NC. Por discrepancia entre distribuidor y proveedor, se adopta el término más restrictivo **CC BY-NC-SA 4.0** como regla operativa hasta obtener aclaración escrita. El uso académico no comercial del proyecto puede continuar sujeto a atribución y compartir-igual; no redistribuir archivos ni derivados. La licencia no impide validar localmente las muestras ni generar métricas agregadas permitidas por los términos.

Fuentes consultadas: [sitio oficial UrbanSyn](https://urbansyn.org/) y [README del dataset en Hugging Face](https://huggingface.co/datasets/UrbanSyn/UrbanSyn).


## 14. Ontología versionada y plan de balanceo — 2026-11-22

La definición operativa posterior a las auditorías queda fijada en `configs/urban_ontology_v1.json` (`urban-v1`), con cargador/validación en `src/urban_ontology.py`. Esta versión sustituye la tabla conceptual provisional de la sección 3 para las nuevas preparaciones:

- Semántica: UrbanSyn trainId 0–18 conserva su significado; 19 (`unlabeled`) pasa a ignore 255. Se añade semantic ID 19 para `lane marking`, disponible desde las variantes A2D2 que correspondan.
- Instancias: IDs 1–8 = person, rider, car, truck, bus, train, motorcycle, bicycle; background 0.
- `rider` y `bicycle` no se fusionan. `lane marking` no es una clase de instancia. IDs de instancia son locales por imagen.
- A2D2 se mapea por nombre normalizado; clases fuente no incluidas quedan en ignore. Su extracción de instancias continúa siendo una aproximación por componentes conectados.

Se añadió `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md` y `scripts/build_balanced_training_plan.py`. El planificador exige estadísticas por imagen (píxeles semánticos y número de instancias por clase), selecciona train con un algoritmo greedy multilabel determinista y conserva validation/test completos, sin mover registros entre splits. Los outputs se mantienen separados por dataset y tarea: UrbanSyn es la fuente primaria de instancias y A2D2 queda como ablation/complemento. No se concatena A2D2 con UrbanSyn automáticamente.

**Bloqueo explícito:** el informe de auditoría de 150 muestras contiene agregados por split, no estadísticas completas por imagen. Por tanto, el planificador y la ontología están implementados y probados con fixtures, pero aún no existe un plan balanceado real ni los índices per-image. Debe generarse ese índice desde las anotaciones remotas antes de invocar el planificador con datos reales. No se deben inventar etiquetas ni asumir que las clases ausentes en la muestra están ausentes del dataset completo.

La definición de ontología no altera retroactivamente los IDs legacy por defecto de `src/data_adapters.py`; la integración de los nuevos mapas en cada experimento debe pasar explícitamente el mapa correspondiente y probarse antes de entrenamiento. Esto evita cambiar silenciosamente la semántica de los pipelines anteriores.

**Entrenamiento:** `RUN_TRAINING=False`; no se descargaron datasets completos ni se inició entrenamiento. UrbanSyn conserva criterio de licencia CC BY-NC-SA 4.0, atribución y no redistribución de imágenes/máscaras/derivados.


## Protocolo experimental versionado — 2026-11-23

El diseño operativo de entrenamiento, matriz de experimentos, hiperparámetros iniciales, métricas, checkpoints, reanudación y puertas de autorización queda centralizado en [docs/PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md](PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md). La matriz mantiene A2D2 y UrbanSyn separados y prioriza UrbanSyn para instancias; A2D2 instancias es complementario por sus componentes conectados reconstruidos. El documento es una propuesta técnica, no una orden de ejecución: `RUN_TRAINING=False` sigue vigente y se requiere autorización expresa para piloto y entrenamiento completo.
