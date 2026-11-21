# Detección y segmentación semántica en escenas urbanas

Proyecto académico del Equipo 2 para detectar y segmentar objetos de escenas viales y evaluar modelos de percepción urbana.

## Estado actual

La rama `urban-models-and-benchmark` incorpora infraestructura para:
- Entrenar **DeepLabV3+ ResNet-50** en las 11 clases semánticas de Cityscapes.
- Ajustar **Mask R-CNN** desde pesos COCO a siete clases de instancia de Cityscapes.
- Preparar máscaras de carriles desde polígonos anotados de BDD100K y entrenar un segmentador binario.
- Ejecutar segmentación semántica y carriles exportados mediante **ONNX Runtime**.
- Medir latencia p50/p95/p99 y FPS con warm-up y sincronización CUDA.

**Pruebas automatizadas:** GitHub Actions ejecutó compileall, smoke tests de CLI y `pytest -q`: **19 pruebas aprobadas** en Python 3.11 / CPU. Esto no equivale a entrenar modelos ni a medir métricas con los datasets reales.

**Importante:** estos scripts no descargan automáticamente Cityscapes/BDD100K ni entrenan los modelos al instalar el repositorio. Los checkpoints deben generarse localmente con los comandos de abajo. No se han ejecutado entrenamientos ni benchmarks como parte de estos cambios.

## Arquitecturas

| Componente | Arquitectura | Datos / estado |
|---|---|---|
| Segmentación semántica | DeepLabV3+ ResNet-50 | Script de entrenamiento Cityscapes; requiere checkpoint local |
| Segmentación de instancias | Mask R-CNN ResNet-50 FPN V2 | Fine-tuning Cityscapes implementado; requiere checkpoint local |
| Carriles | DeepLabV3+ binario | Conversión de polígonos BDD100K + entrenamiento implementados; requiere checkpoint |
| ONNX | ONNX Runtime | Inferencia semántica/carriles; no produce cajas ni instancias |
| Detector híbrido | Faster R-CNN COCO | Sigue preentrenado COCO; no está fine-tuned en Cityscapes |
| Backend `onnx_cv2` | HOG + OpenCV | Modo demostrativo; no es ONNX |

## Instalación

Python 3.10+ recomendado. Instala PyTorch/Torchvision compatibles con tu CPU/GPU y luego:

```bash
pip install -r requirements.txt
python scripts/verify_setup.py
pytest -q
```

## Datasets

### Cityscapes

Descarga el paquete de imágenes `leftImg8bit` y las anotaciones `gtFine` desde el portal oficial de Cityscapes y conserva su estructura:

```text
data/cityscapes/
├── leftImg8bit/{train,val}/<city>/*_leftImg8bit.png
└── gtFine/{train,val}/<city>/*_gtFine_labelIds.png
                              *_gtFine_instanceIds.png
```

Entrenar DeepLabV3+:

```bash
python scripts/train_urban_segmentation.py --task cityscapes --data-root data/cityscapes --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_urban.pt
```

Entrenar Mask R-CNN:

```bash
python scripts/train_maskrcnn_cityscapes.py --data-root data/cityscapes --epochs 20 --batch-size 2 --output data/processed/maskrcnn_cityscapes.pt
```

DeepLabV3+ predice 11 clases: road, sidewalk, person, rider, car, truck, bus, motorcycle, bicycle, traffic light y traffic sign. Mask R-CNN predice siete clases de instancia: person, rider, car, truck, bus, motorcycle y bicycle.

## Segmentación de carriles con BDD100K

Descarga imágenes y anotaciones *lane marking* de BDD100K. Genera máscaras binarias:

```bash
python scripts/prepare_bdd100k_lane_masks.py --labels data/bdd100k/labels/lane/train.json --images-dir data/bdd100k/images/100k/train --masks-dir data/bdd100k/lane_masks/train
python scripts/prepare_bdd100k_lane_masks.py --labels data/bdd100k/labels/lane/val.json --images-dir data/bdd100k/images/100k/val --masks-dir data/bdd100k/lane_masks/val
python scripts/train_urban_segmentation.py --task lanes --images-dir data/bdd100k/images/100k/train --masks-dir data/bdd100k/lane_masks/train --val-images-dir data/bdd100k/images/100k/val --val-masks-dir data/bdd100k/lane_masks/val --epochs 30 --batch-size 2 --output data/processed/deeplabv3plus_lanes.pt
```

Prepara una partición de validación independiente por secuencia/video. No dividas fotogramas adyacentes aleatoriamente entre train y validation.

## Preparación automatizada de datasets

La preparación puede ejecutarse con GitHub Actions y Google Drive sin almacenar datos en Git. Consulta [docs/DATASETS_GITHUB_ACTIONS.md](docs/DATASETS_GITHUB_ACTIONS.md) para configurar rclone mediante OAuth y guardar el archivo de configuración en el secreto `GDRIVE_RCLONE_CONFIG`.

El workflow manual `.github/workflows/prepare-datasets.yml` valida BDD100K y genera máscaras de carriles para train/val. Los archivos fuente deben estar previamente en Drive. Cityscapes permanece bloqueado hasta completar el registro y confirmar el acceso autorizado; no se intenta descargarlo automáticamente. Esta fase prepara datos, no entrena modelos.

## Inferencia

```bash
# Mask R-CNN fine-tuned en Cityscapes
python main.py --source ruta/video.mp4 --approach instance --backend torch --no-gui

# DeepLabV3+ + Faster R-CNN COCO + segmentador de carriles (si existe su checkpoint)
python main.py --source ruta/video.mp4 --approach hybrid --backend torch --no-gui
```

El archivo `configs/config.yaml` apunta a:
- `data/processed/maskrcnn_cityscapes.pt`
- `data/processed/deeplabv3plus_urban.pt`
- `data/processed/deeplabv3plus_lanes.pt`

Si falta el checkpoint DeepLabV3+, el enfoque híbrido se detiene con un error explícito. Si falta el checkpoint de carriles, devuelve una máscara vacía y marca `lane_model_loaded=false`; no finge segmentación aprendida.

### Evaluar precisión

```bash
python scripts/evaluate_cityscapes.py --task semantic --data-root data/cityscapes --checkpoint data/processed/deeplabv3plus_urban.pt
python scripts/evaluate_cityscapes.py --task instance --data-root data/cityscapes --checkpoint data/processed/maskrcnn_cityscapes.pt
python scripts/evaluate_lanes.py --images-dir data/bdd100k/images/100k/val --masks-dir data/bdd100k/lane_masks/val --checkpoint data/processed/deeplabv3plus_lanes.pt
```

El AP de Mask R-CNN implementado en esta evaluación es AP de cajas, no AP de máscaras.

## Exportar a ONNX

```bash
python scripts/export_deeplabv3plus_onnx.py --checkpoint data/processed/deeplabv3plus_urban.pt --output data/processed/urban_semantic.onnx
python scripts/export_deeplabv3plus_onnx.py --checkpoint data/processed/deeplabv3plus_lanes.pt --classes 2 --output data/processed/urban_lanes.onnx
python main.py --source ruta/video.mp4 --approach hybrid --backend onnx --no-gui
```

ONNX Runtime carga logits semánticos y del segmentador de carriles. Esta ruta no ejecuta Mask R-CNN ni genera detecciones de instancias.

## Protocolo de evaluación

Consulta [docs/PROTOCOLO_EXPERIMENTAL.md](docs/PROTOCOLO_EXPERIMENTAL.md). Resume:
- Cityscapes train/val para segmentación semántica y máscaras de instancias.
- BDD100K para carriles y condiciones reales, separando secuencias.
- mIoU por clase, AP@0.5 por clase y evaluación de máscaras cuando esté disponible el evaluador correspondiente.
- Benchmark con warm-up, sincronización CUDA, latencia media/mediana/p95/p99, resolución y hardware.

Benchmark de inferencia (no incluye decodificación, GUI ni escritura):

```bash
python scripts/benchmark.py --source data/benchmark/urban.mp4 --approach instance --backend torch --warmup 30 --frames 300 --output data/outputs/benchmark.json
```

No comparar métricas de datasets distintos ni presentar los escenarios sintéticos como robustez real bajo clima adverso.

## Estructura principal

```text
configs/                 Configuración del sistema y checkpoints
docs/                    Auditoría y protocolo experimental
scripts/                 Entrenamiento, preparación BDD, exportación y benchmark
src/models/              Mask R-CNN, DeepLabV3+ y ONNX Runtime
src/utils/               Cargadores Cityscapes/BDD y utilidades
src/evaluation/          Métricas y evaluación
tests/                   Pruebas unitarias y de integridad
```

## Limitaciones aún abiertas

1. Faster R-CNN dentro del enfoque híbrido continúa con pesos COCO, sin fine-tuning urbano.
2. El exportador ONNX cubre segmentación semántica y carriles, no instancias.
3. El script de benchmark mide inferencia del modelo; la medición end-to-end de captura, render y escritura es otro experimento.
4. Falta incorporar un evaluador de AP de máscaras de instancias y F1/IoU de carriles sobre un split BDD100K reservado.
5. La partición BDD100K por secuencia debe prepararse antes de entrenar.
6. No se incluyen pesos entrenados ni datos de datasets en Git.

## Documentación

- [Auditoría técnica](docs/AUDITORIA_Y_DOCUMENTACION.md)
- [Protocolo experimental reproducible](docs/PROTOCOLO_EXPERIMENTAL.md)
