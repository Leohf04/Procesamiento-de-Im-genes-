# Protocolo experimental reproducible

## Objetivo

Separar tres mediciones que no deben mezclarse: (1) calidad semántica, (2) calidad de detección/instancias y (3) rendimiento. Cada resultado debe indicar dataset, split, checkpoint, resolución, umbral y hardware.

## Datos y particiones

- **BDD100K 10K** es el dataset principal para segmentación semántica e instancias. Usar los splits oficiales train/val y emparejar imágenes y máscaras por nombre.
- Semántica: `images/10k/{train,val}` + `labels/sem_seg/masks/{train,val}`; IDs 0–18 y 255 ignore.
- Instancias: `images/10k/{train,val}` + `labels/ins_seg/bitmasks/{train,val}`; PNG RGBA oficial, ocho categorías. No convertir a RGB o escala de grises.
- Detección 2D: usar 100K images + Detection 2020 Labels (10 categorías); adaptador/entrenador pendiente.
- Carriles: las etiquetas oficiales codifican categoría, dirección y estilo; no aplanarlas a binario hasta implementar y validar las tres salidas. Parser Bezier pendiente de corrección.
- Mantener los splits oficiales y no mezclar secuencias/frames de un mismo vídeo entre train y validation.
- **Cityscapes** queda como flujo legado opcional; no es requisito de BDD100K.
- **COCO val2017** puede conservarse como benchmark auxiliar, no como sustituto de BDD100K.
- No usar validation para ajustar umbrales y luego reportarlo como test.

## Preparación reproducible desde Google Drive

La preparación automatizada está descrita en [docs/DATASETS_GITHUB_ACTIONS.md](DATASETS_GITHUB_ACTIONS.md). El workflow manual descarga temporalmente desde Google Drive el JSON de un split y un lote acotado (hasta 4.000 imágenes), valida las imágenes y genera máscaras binarias de carriles; sube manifiestos y máscaras derivadas de vuelta a Drive. El siguiente lote se reanuda con `next_offset`. No almacena imágenes ni anotaciones en GitHub. Cityscapes permanece deshabilitado hasta que el usuario tenga registro y acceso autorizado. La preparación no sustituye el entrenamiento y no demuestra que la partición BDD100K esté libre de fuga temporal: los splits deben organizarse por secuencia/video.

## Entrenamiento

### DeepLabV3+ semántico BDD100K (19 clases)

```bash
python scripts/train_urban_segmentation.py --task bdd100k-semantic --images-dir data/bdd100k/images/10k/train --masks-dir data/bdd100k/labels/sem_seg/masks/train --val-images-dir data/bdd100k/images/10k/val --val-masks-dir data/bdd100k/labels/sem_seg/masks/val --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_bdd100k_semantic.pt
```

Clases de salida (19): road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle y bicycle. El ID 255 se ignora.

### Mask R-CNN por instancias BDD100K

```bash
python scripts/train_maskrcnn_cityscapes.py --dataset bdd100k --images-dir data/bdd100k/images/10k/train --bitmasks-dir data/bdd100k/labels/ins_seg/bitmasks/train --val-images-dir data/bdd100k/images/10k/val --val-bitmasks-dir data/bdd100k/labels/ins_seg/bitmasks/val --epochs 20 --batch-size 2 --output data/processed/maskrcnn_bdd100k.pt
```

El checkpoint parte de pesos COCO y ajusta las cabezas de cajas y máscaras a ocho clases BDD100K: pedestrian, rider, car, truck, bus, train, motorcycle y bicycle. Es un entrenamiento real solo después de ejecutar el comando con las anotaciones oficiales.

### Carriles BDD100K — bloqueado hasta adaptar las tres subtareas

No ejecutar `scripts/prepare_bdd100k_lane_masks.py` ni el entrenamiento binario antiguo para producir resultados académicos. El formato oficial codifica categoría, dirección y estilo en una máscara monocanal y el JSON `poly2d` contiene curvas Bezier. El conversor anterior trataba vértices como líneas simples y no preservaba los tres atributos.

La implementación debe usar las máscaras oficiales `labels/lane/masks/{train,val}` y entrenar/evaluar las tres salidas (9 categorías, 2 direcciones y 2 estilos evaluables, excluyendo background), o usar el conversor oficial BDD100K. Se requieren pruebas con máscaras reales y visualizaciones antes de habilitar el entrenamiento.

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

La evaluación de instancias BDD100K (box AP y mask AP) sigue pendiente. El evaluador Cityscapes existente no es compatible con los bitmasks BDD100K. El evaluador binario de carriles queda bloqueado hasta implementar las tres subtareas oficiales.

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
