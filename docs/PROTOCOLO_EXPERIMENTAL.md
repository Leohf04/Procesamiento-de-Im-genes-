# Protocolo experimental reproducible

## Objetivo

Separar tres mediciones que no deben mezclarse: (1) calidad semántica, (2) calidad de detección/instancias y (3) rendimiento. Cada resultado debe indicar dataset, split, checkpoint, resolución, umbral y hardware.

## Datos y particiones

- **Cityscapes Fine**: entrenamiento oficial `train` y validación oficial `val`. No mezclar imágenes entre splits. La evaluación final académica debe reservar el split `test` y usar el servidor oficial cuando se requieran etiquetas ocultas.
- **BDD100K lane markings**: convertir los polígonos lane a máscaras con `scripts/prepare_bdd100k_lane_masks.py`. Crear directorios de entrenamiento y validación por video/sequence, nunca por frames aleatorios adyacentes. El script de entrenamiento de carriles usa la carpeta suministrada; la partición de sus archivos debe hacerse previamente y documentarse.
- **COCO val2017**: conservarlo como benchmark auxiliar de detección COCO, no como sustituto de Cityscapes/BDD100K.
- No usar el split de validación para ajustar umbrales y después reportarlo como test. Registrar cualquier selección de hiperparámetros.

## Entrenamiento

### DeepLabV3+ semántico urbano (11 clases Cityscapes)

```bash
python scripts/train_urban_segmentation.py --task cityscapes --data-root data/cityscapes --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_urban.pt
```

Clases de salida: road, sidewalk, person, rider, car, truck, bus, motorcycle, bicycle, traffic_light y traffic_sign. Los IDs restantes se ignoran (255).

### Mask R-CNN por instancias

```bash
python scripts/train_maskrcnn_cityscapes.py --data-root data/cityscapes --epochs 20 --batch-size 2 --output data/processed/maskrcnn_cityscapes.pt
```

El checkpoint parte de pesos COCO y ajusta las cabezas de cajas y máscaras a siete clases Cityscapes: person, rider, car, truck, bus, motorcycle y bicycle. Es un entrenamiento real solo después de ejecutar el comando con las anotaciones oficiales.

### Segmentación aprendida de carriles

Descargar las anotaciones lane-marking de BDD100K y generar máscaras:

```bash
python scripts/prepare_bdd100k_lane_masks.py --labels data/bdd100k/labels/lane/train.json --images-dir data/bdd100k/images/100k/train --masks-dir data/bdd100k/lane_masks/train
python scripts/train_urban_segmentation.py --task lanes --images-dir data/bdd100k/images/100k/train --masks-dir data/bdd100k/lane_masks/train --val-images-dir data/bdd100k/images/100k/val --val-masks-dir data/bdd100k/lane_masks/val --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_lanes.pt
```

El entrenamiento exige explícitamente directorios de train y validation separados. Preparar esa partición por secuencia/video antes de entrenar; no usar frames del mismo clip en ambos grupos. El checkpoint de carriles es opcional en inferencia; si falta, el sistema devuelve una máscara vacía y no simula segmentación HSV.

## Inferencia

- PyTorch híbrido: `python main.py --source ruta/video.mp4 --approach hybrid --backend torch --no-gui`
- Mask R-CNN urbano: `python main.py --source ruta/video.mp4 --approach instance --backend torch --no-gui`
- Export semántico a ONNX: `python scripts/export_deeplabv3plus_onnx.py --checkpoint data/processed/deeplabv3plus_urban.pt --output data/processed/urban_semantic.onnx`
- Inferencia ONNX semántica: `python main.py --source ruta/video.mp4 --approach hybrid --backend onnx --no-gui`

El exportador ONNX actual cubre segmentación semántica y carriles. No exporta Mask R-CNN ni produce detecciones/cajas; no comparar esa ruta como segmentación por instancias.

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
- Carriles: reportar IoU y F1 de la clase lane_marking sobre BDD100K val.
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
- El evaluador de mAP de detección existente usa cajas; la evaluación de máscaras de instancias requiere una métrica adicional antes de presentar mask AP.
