# Protocolo experimental reproducible

## Objetivo

Separar tres mediciones que no deben mezclarse: (1) calidad semántica, (2) calidad de detección/instancias y (3) rendimiento. Cada resultado debe indicar dataset, split, checkpoint, resolución, umbral y hardware.

## Estrategia de datasets activa

La combinación activa es **A2D2 + UrbanSyn + SHIFT**. La matriz de cobertura, el mapeo conceptual, las licencias, las métricas y las puertas de validación están en [docs/ESTRATEGIA_MULTIDATASET.md](ESTRATEGIA_MULTIDATASET.md). Ese documento prevalece sobre las secciones históricas BDD100K/Cityscapes que se conservan más abajo como referencia técnica.

- **A2D2:** escenas reales; semántica e instancias/detección solo después de decodificar los archivos oficiales. No se han confirmado atributos por imagen para estratificar clima/hora.
- **UrbanSyn:** semántica 19 clases, panoptic de objetos dinámicos y cajas 2D. Sintético; no tiene clase dedicada de carriles ni condiciones ambientales reales.
- **SHIFT:** la descarga oficial está actualmente inaccesible por DNS. Se encontró un espejo HF parcial con solo `discrete/videos`; su CSV `val/front` contiene metadatos de clima y hora, pero los archivos RGB/semseg son tar grandes. Se usa solo como candidato de evaluación sintética después de extraer y emparejar una muestra; no hay datos `continuous/` en ese espejo.
- No concatenar datasets ni comparar métricas de clases distintas sin un adaptador explícito. Mantener resultados separados por fuente y dominio.
- Mantener splits oficiales y separar por secuencia/escena para evitar fuga temporal. No ajustar umbrales en validation y reportarlos como test.
- No etiquetar como evaluación real de lluvia/noche/niebla una corrupción artificial. Los aumentos se informan por separado.

## Cobertura de tareas

- Semántica: DeepLabV3+; IDs mapeados a una taxonomía común tras validar los tres esquemas.
- Instancias: Mask R-CNN; UrbanSyn panoptic se convierte en instancias individuales; SHIFT/A2D2 requieren adaptadores validados.
- Detección: cajas 2D UrbanSyn/SHIFT. Cajas 3D A2D2 no se consideran 2D nativas; proyectarlas solo con calibración comprobada.
- Carriles y señales: evaluar únicamente cuando la fuente tenga etiquetas explícitas. UrbanSyn tiene clase semántica traffic sign, pero no lane-marking ni cajas/instancias para señales según la ficha consultada.
- Robustez: SHIFT para domain shifts sintéticos si la muestra de video/semseg se valida; A2D2 para dominio real general. El CSV del espejo SHIFT declara clima/hora a nivel de secuencia. No afirmar estratos reales día/noche/lluvia/niebla para A2D2 sin metadata comprobada.

## Preparación heredada BDD100K desde Google Drive (no activa)

La preparación automatizada está descrita en [docs/DATASETS_GITHUB_ACTIONS.md](DATASETS_GITHUB_ACTIONS.md). El workflow manual descarga temporalmente desde Google Drive el JSON de un split y un lote acotado (hasta 4.000 imágenes), valida las imágenes y genera máscaras binarias de carriles heredadas. Ese resultado binario se conserva solo por compatibilidad y no se usa en el nuevo entrenamiento multi-tarea; el flujo nuevo requiere las máscaras oficiales empaquetadas. El siguiente lote se reanuda con `next_offset`. No almacena imágenes ni anotaciones en GitHub. Cityscapes permanece deshabilitado hasta que el usuario tenga registro y acceso autorizado. La preparación no sustituye el entrenamiento y no demuestra que la partición BDD100K esté libre de fuga temporal: los splits deben organizarse por secuencia/video.

## Entrenamiento

### Referencia heredada: DeepLabV3+ semántico BDD100K (no ejecutar como flujo activo)

```bash
python scripts/train_urban_segmentation.py --task bdd100k-semantic --images-dir data/bdd100k/images/10k/train --masks-dir data/bdd100k/labels/sem_seg/masks/train --val-images-dir data/bdd100k/images/10k/val --val-masks-dir data/bdd100k/labels/sem_seg/masks/val --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_bdd100k_semantic.pt
```

Clases de salida (19): road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle y bicycle. El ID 255 se ignora.

### Referencia heredada: Mask R-CNN por instancias BDD100K

```bash
python scripts/train_maskrcnn_cityscapes.py --dataset bdd100k --images-dir data/bdd100k/images/10k/train --bitmasks-dir data/bdd100k/labels/ins_seg/bitmasks/train --val-images-dir data/bdd100k/images/10k/val --val-bitmasks-dir data/bdd100k/labels/ins_seg/bitmasks/val --epochs 20 --batch-size 2 --output data/processed/maskrcnn_bdd100k.pt
```

El checkpoint parte de pesos COCO y ajusta las cabezas de cajas y máscaras a ocho clases de instancia BDD100K. El loader entrega imágenes en [0,1], ya que Torchvision normaliza internamente. El evaluador nuevo acepta checkpoints con nueve salidas (fondo + 8 clases) y calcula Box AP y Mask AP.


### Auditoría previa obligatoria para Mask R-CNN BDD100K

Antes del primer entrenamiento, ejecutar sobre los directorios oficiales:

```bash
python scripts/audit_bdd100k_instance_splits.py \
  --train-images data/bdd100k/images/10k/train \
  --train-bitmasks data/bdd100k/labels/ins_seg/bitmasks/train \
  --val-images data/bdd100k/images/10k/val \
  --val-bitmasks data/bdd100k/labels/ins_seg/bitmasks/val \
  --output data/outputs/bdd100k_instance_preflight.json
```

La auditoría verifica que cada imagen tenga exactamente su máscara PNG, que la máscara original sea RGBA y coincida en dimensiones, que los IDs de anotación/categorías/flags sean coherentes y que no haya stems compartidos entre train y val. Informa el número de instancias por clase; por defecto bloquea el proceso si alguna de las ocho clases no aparece en train. Las clases ausentes en val se informan, pero no bloquean por sí solas el entrenamiento. El informe `ready_for_training` debe ser `true`.

La muestra GitHub alternativa usada para el smoke test de Torchvision contiene solo dos imágenes del split val y cuatro clases (bus, car, motorcycle, truck), con máscaras binarias por objeto. Sirve para validar el adaptador parcial y el forward/backward, **no** para entrenar, no para medir AP y no para reemplazar los PNG RGBA oficiales. No mover esas imágenes a train ni mezclar sus resultados con la evaluación oficial.

El notebook de Colab ejecuta esta auditoría y exige un informe aprobado antes de permitir `MODEL="instance"` con `RUN_TRAINING=True`. El entrenamiento guarda `.last.pt` (estado de modelo/optimizador/scheduler) y el checkpoint de evaluación; la reanudación es por época. Tras completar el entrenamiento, ejecutar el evaluador BDD100K de instancias sobre el split val oficial. No iniciar el entrenamiento mientras no se tenga acceso autorizado a las bitmasks oficiales.

### Referencia heredada: carriles BDD100K

Entrenar con las máscaras oficiales `labels/lane/masks/{train,val}`, no con polígonos rasterizados a una máscara binaria:

```bash
python scripts/train_bdd100k_lanes.py --train-images data/bdd100k/images/100k/train --train-masks data/bdd100k/labels/lane/masks/train --val-images data/bdd100k/images/100k/val --val-masks data/bdd100k/labels/lane/masks/val --epochs 20 --batch-size 2 --output data/processed/bdd100k_lanes.pt
```

El byte empaquetado se decodifica con bits 0–2 para categoría, bit 3 para fondo, bit 4 para estilo y bit 5 para dirección. El entrenamiento tiene una cabeza por subtarea y calcula mIoU de validación. El antiguo `scripts/prepare_bdd100k_lane_masks.py` queda obsoleto porque pierde atributos y no reproduce curvas Bezier. Antes de reportar métricas académicas se debe contrastar el decoder con máscaras oficiales reales y el evaluador oficial BDD100K.

## Inferencia

- PyTorch híbrido: `python main.py --source ruta/video.mp4 --approach hybrid --backend torch --no-gui`
- Mask R-CNN urbano: `python main.py --source ruta/video.mp4 --approach instance --backend torch --no-gui`
- Export semántico a ONNX: `python scripts/export_deeplabv3plus_onnx.py --checkpoint data/processed/deeplabv3plus_urban.pt --output data/processed/urban_semantic.onnx`
- Inferencia ONNX semántica: `python main.py --source ruta/video.mp4 --approach hybrid --backend onnx --no-gui`

El exportador ONNX actual cubre segmentación semántica y carriles. No exporta Mask R-CNN ni produce detecciones/cajas; no comparar esa ruta como segmentación por instancias.

### Evaluar precisión BDD100K

```bash
# Semántica BDD100K: IoU por clase y mIoU
python scripts/evaluate_cityscapes.py --task bdd100k-semantic --images-dir data/bdd100k/images/10k/val --masks-dir data/bdd100k/labels/sem_seg/masks/val --checkpoint data/processed/deeplabv3plus_bdd100k_semantic.pt
```

Evaluar instancias BDD100K (Box AP y Mask AP):

```bash
python scripts/evaluate_cityscapes.py --task bdd100k-instance --images-dir data/bdd100k/images/10k/val --bitmasks-dir data/bdd100k/labels/ins_seg/bitmasks/val --checkpoint data/processed/maskrcnn_bdd100k.pt --output data/outputs/bdd100k_instance_metrics.json
```

El evaluador usa matching greedy por imagen e interpolación precision-recall; su AP50/AP75/AP50:95 es un protocolo interno y no equivale a COCOeval oficial. La validación oficial y máscaras reales aún son necesarias antes de publicar resultados.

El AP de Mask R-CNN de este script corresponde a cajas, no a máscaras. No reportar mask AP hasta añadir y ejecutar una evaluación COCO-style de máscaras.

## Rendimiento (FPS y latencia)

Ejecutar `scripts/benchmark.py` sobre la misma fuente, con la misma resolución, backend, modelo y número de frames para cada alternativa:

```bash
python scripts/benchmark.py --source data/benchmark/urban.mp4 --approach instance --backend torch --warmup 30 --frames 300 --output data/outputs/benchmark_maskrcnn.json
python scripts/benchmark.py --source data/benchmark/urban.mp4 --approach hybrid --backend torch --warmup 30 --frames 300 --output data/outputs/benchmark_deeplab.json
```

El informe incluye media, mediana, p95, p99, FPS derivado de latencia media, resolución, versiones y hardware. Se excluyen decodificación, GUI y escritura del vídeo. Para medir end-to-end, realizar además una prueba separada de captura + inferencia + render + escritura e identificarla como tal. En GPU se sincroniza CUDA antes y después de cada medición. No comparar FPS entre resoluciones o hardware distintos.

## Precisión

- DeepLabV3+: reportar IoU por clase y mIoU sobre Cityscapes val, ignorando ID 255.
- Mask R-CNN: reportar AP@0.5 por clase y mAP@0.5 con matching uno-a-uno, además de métricas de máscaras si se dispone del evaluador de instancias correspondiente.
- Detección 2D: reportar Box AP50 por clase y mAP50 sobre BDD100K val.
- Instancias: reportar Box AP y Mask AP; distinguir explícitamente el protocolo interno del COCOeval oficial.
- Carriles: reportar mIoU por categoría, dirección y estilo sobre BDD100K val, y contrastar con el F1 boundary oficial.
- Reportar por separado métricas COCO y Cityscapes/BDD100K. Nunca promediar datasets incompatibles.
- Publicar número de imágenes, objetos por clase, umbrales, tamaño de entrada, checkpoint SHA-256, seed y comandos exactos.

## Criterios para aceptar resultados

1. Entrenamiento termina sin errores y produce checkpoints no vacíos.
2. La inferencia carga exactamente esos checkpoints y no pesos aleatorios.
3. El split de validación no participa en el entrenamiento ni en ajuste iterativo no documentado.
4. Se reportan métricas por clase, soporte y casos sin anotaciones.
5. Se ejecutan tests unitarios y smoke tests de inferencia CPU/GPU/ONNX por separado.
6. Los resultados deben repetirse al menos tres veces para rendimiento; reportar mediana y dispersión.

## Limitaciones actuales que deben permanecer explícitas

- Los scripts y arquitecturas se añadieron al repositorio, pero **no se han entrenado modelos ni descargado datasets** en esta modificación.
- Mask R-CNN solo queda adaptado al checkpoint Cityscapes cuando se ejecute su entrenamiento; si no existe el archivo, el código sigue usando los pesos COCO originales.
- El detector Faster R-CNN del enfoque híbrido sigue usando pesos COCO; la segmentación semántica y la segmentación de carriles sí tienen rutas de entrenamiento urbanas.
- El script de benchmark mide inferencia del pipeline del modelo, no latencia end-to-end de captura/GUI.
- Los adaptadores de detección/carriles y el evaluador Mask AP ya están implementados, pero aún requieren validación con máscaras/anotaciones oficiales reales y contraste con los evaluadores oficiales.


## Estado de preflights (2026-11-22)

- A2D2: muestra semántica aprobada (RGB+mask 1920×1208); `class_list.json` leído (55 clases/colores). El mismo mapa contiene subclases como Car 1–4, Bicycle 1–4 y Pedestrian 1–3; falta validar conversión de estas etiquetas a instancias individuales. La carpeta de instancia separada no produjo PNGs en la ruta explorada.
- UrbanSyn: dos muestras completas RGB/semseg/panoptic/bbox aprobadas a 2048×1024; IDs semánticos 0–19 y panoptic dinámico verificados. Ver [workflow 44971557432](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971557432).
- SHIFT: servidor oficial no resuelve DNS. El espejo HF parcial expone `seq.csv` con clima/hora (incluye rain/fog/night) y archivos grandes solo de `discrete/videos/val/front`; sin `continuous/`. Preflight de video por HTTP Range pendiente.
- No ejecutar los comandos BDD100K de las secciones posteriores: son referencia heredada, no parte de la estrategia activa.
