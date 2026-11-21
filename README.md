# Detección y segmentación semántica en escenas urbanas

Proyecto académico del **Equipo 2**: detección y segmentación de elementos urbanos mediante un enfoque de segmentación por instancias y otro híbrido de segmentación semántica más detección.

El sistema explora peatones, bicicletas, automóviles, motocicletas, autobuses, camiones, semáforos y señales de stop. Incluye preprocesamiento de iluminación y condiciones atmosféricas, clasificación fina mediante descriptores y SVM, evaluación por escenarios sintéticos y procesamiento de imágenes/vídeo.

> **Estado del proyecto:** prototipo funcional en desarrollo. La implementación actual usa COCO val2017 como fuente de evaluación, modelos preentrenados de Torchvision y degradaciones sintéticas. No debe interpretarse todavía como una validación completa sobre Cityscapes o BDD100K ni como una comparación experimental definitiva.

## Contenido

- [Objetivo](#objetivo)
- [Enfoques comparados](#enfoques-comparados)
- [Clases objetivo](#clases-objetivo)
- [Arquitectura](#arquitectura)
- [Preprocesamiento](#preprocesamiento)
- [Dataset actual y limitaciones](#dataset-actual-y-limitaciones)
- [Instalación](#instalación)
- [Uso](#uso)
- [Evaluación](#evaluación)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Auditoría y documentación](#auditoría-y-documentación)
- [Trabajo pendiente](#trabajo-pendiente)

## Objetivo

Desarrollar un sistema de percepción urbana que detecte y segmente objetos relevantes de escenas viales, compare segmentación por instancias con segmentación semántica complementada por detección y estudie su comportamiento bajo variaciones de iluminación y clima.

## Enfoques comparados

### 1. Segmentación por instancias — Mask R-CNN

Implementada en `src/models/instance_seg.py` mediante `maskrcnn_resnet50_fpn_v2` y pesos preentrenados de Torchvision.

Entrega cajas delimitadoras, clase, confianza y una máscara por instancia. También genera máscaras binarias agregadas para comparar regiones urbanas.

### 2. Enfoque híbrido — DeepLabV3 + Faster R-CNN + carriles HSV

Implementado en `src/models/semantic_hybrid.py`:

- DeepLabV3 ResNet-50 produce un mapa semántico.
- Faster R-CNN ResNet-50 FPN V2 produce cajas, clases y puntuaciones.
- OpenCV/HSV extrae una máscara heurística de marcas blancas y amarillas de carril.

**Precisión terminológica:** el código usa DeepLabV3 de Torchvision, no DeepLabV3+, y Faster R-CNN no genera máscaras de instancia. Por tanto, el enfoque híbrido entrega segmentación semántica, detección por cajas y una máscara heurística de carriles; no equivale a Mask R-CNN.

### Backend ligero

El backend denominado `onnx_cv2` no ejecuta actualmente un modelo ONNX. Utiliza HOG de OpenCV para peatones y máscaras geométricas elípticas en el modelo de instancias; en el modelo híbrido añade extracción HSV de carriles. Es un modo demostrativo de menor coste, no un sustituto equivalente de los modelos neuronales.

## Clases objetivo

La configuración declara ocho clases COCO: persona, bicicleta, automóvil, motocicleta, autobús, camión, semáforo y señal de stop. El subconjunto común usado para algunas máscaras semánticas contiene cinco clases: persona, bicicleta, automóvil, motocicleta y autobús.

Las clases realmente reconocibles dependen de las categorías de los pesos preentrenados y del filtrado configurado. Las señales, carriles y clases finas no tienen todas un modelo aprendido específico en esta versión.

## Arquitectura

1. `configs/config.yaml`: backend, dataset, umbrales, clases y escenarios.
2. `src/preprocessing/`: correcciones de iluminación y degradaciones atmosféricas.
3. `src/models/`: Mask R-CNN y enfoque híbrido.
4. `src/features/`: descriptores HOG, histograma HSV y clasificador SVM.
5. `src/pipeline.py`: orquestación de predicción por imagen y vídeo.
6. `src/evaluation/`: métricas, evaluación por escenario y visualizaciones de errores.
7. `src/utils/coco_loader.py`: carga de anotaciones COCO y construcción de cajas/máscaras.

## Preprocesamiento

Se encuentran implementadas estas operaciones:

- Ajuste lineal de exposición (`alpha`, `beta`).
- Corrección gamma y CLAHE para mejorar contraste en baja iluminación.
- Desenfoque por movimiento con kernel direccional.
- Simulación sintética de niebla mediante transmisión atmosférica.
- Simulación sintética de lluvia mediante trazos y oscurecimiento.

Las transformaciones se aplican a la imagen de entrada, no a las máscaras de verdad-terreno. La evaluación actual prueba escenarios `clear_day`, `night`, `rain`, `fog` y `motion_blur`.

## Dataset actual y limitaciones

La configuración y los scripts descargan **COCO val2017**. El cargador selecciona imágenes que contienen alguna de las ocho categorías urbanas mapeadas y decodifica polígonos/RLE (si está disponible `pycocotools`; en su ausencia, el fallback solo rasteriza polígonos).

Cityscapes, BDD100K y KITTI son alternativas relevantes para el objetivo académico, pero **no están integradas como cargadores en el estado inspeccionado del repositorio**. COCO tampoco proporciona por sí solo la separación real día/noche/lluvia/niebla que exige una evaluación por condiciones; esos escenarios se sintetizan sobre las imágenes.

## Instalación

Se recomienda Python 3.10 o superior en un entorno virtual. La disponibilidad de PyTorch/Torchvision compatible depende del sistema operativo, la versión de Python y el hardware.

```bash
git clone https://github.com/Leohf04/Procesamiento-de-Im-genes-.git
cd Procesamiento-de-Im-genes-
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python scripts/verify_setup.py
```

En Windows, activar el entorno con `.venv\\Scripts\\activate`. Para instalaciones de PyTorch específicas de CPU/CUDA, consultar la matriz oficial de compatibilidad de PyTorch y Torchvision antes de instalar las dependencias.

## Uso

Descargar COCO val2017 y sus anotaciones:

```bash
python scripts/download_coco_val2017.py
```

Procesar una imagen con Mask R-CNN:

```bash
python main.py --source ruta/imagen.jpg --approach instance --backend torch --no-gui --save-video salida.png
```

Procesar una imagen con el enfoque híbrido:

```bash
python main.py --source ruta/imagen.jpg --approach hybrid --backend torch --no-gui --save-video salida.png
```

Procesar una cámara (el índice predeterminado es 0):

```bash
python main.py --source 0 --approach instance --backend torch --max-frames 200
```

Evaluar escenarios (ejemplo exploratorio con 30 imágenes):

```bash
python evaluate_scenarios.py --approach instance --backend torch --max-samples 30
python evaluate_scenarios.py --approach hybrid --backend torch --max-samples 30
```

Los reportes se escriben en `data/outputs/`. El backend `onnx_cv2` puede probarse con `--backend onnx_cv2`, pero sus resultados no son comparables con los modelos neuronales.

> **Nota sobre vídeo:** la inspección del código detectó que la opción `--save-video` no se propaga actualmente al procesamiento de fuentes de vídeo. En el caso de imágenes, esa opción se usa para guardar una imagen mediante OpenCV. Este comportamiento está documentado como pendiente de corrección; no se debe asumir que el comando anterior guarda vídeo.

## Evaluación

El proyecto calcula actualmente:

- IoU de cajas y conteos de TP/FP/FN.
- Una aproximación denominada `mAP50` / AP por clase.
- mIoU binario (fondo frente a unión de clases urbanas).
- Precisión, recall, latencia media y FPS.
- Gráficas por escenario y AP por clase.
- Ejemplos visuales de cajas predichas frente a cajas GT.

**Advertencia metodológica:** la implementación actual de AP promedia una razón de verdaderos positivos por cantidad de objetos GT por imagen; no construye la curva precisión-recall estándar ni integra AP como COCO. Los conteos globales TP/FP/FN tampoco comprueban la coincidencia de clase. El mIoU mide una máscara binaria agregada, no mIoU multiclase. Los valores deben considerarse diagnósticos preliminares hasta corregir el protocolo.

## Estructura del repositorio

```text
.
├── configs/config.yaml
├── data/                         # datos y resultados locales (no versionados)
├── docs/
│   └── AUDITORIA_Y_DOCUMENTACION.md
├── evaluate_scenarios.py
├── main.py
├── requirements.txt
├── scripts/
│   ├── download_coco_val2017.py
│   └── verify_setup.py
├── src/
│   ├── evaluation/
│   ├── features/
│   ├── models/
│   ├── preprocessing/
│   ├── utils/
│   └── pipeline.py
└── tests/
    └── test_system_integrity.py
```

## Auditoría y documentación

La auditoría estática, el mapa de módulos, las limitaciones conocidas, la matriz de cumplimiento de la consigna y el plan de trabajo se documentan en:

- [Documentación técnica y auditoría](docs/AUDITORIA_Y_DOCUMENTACION.md)

La auditoría se realizó mediante inspección del código fuente disponible en la rama documentada. No representa una ejecución de pruebas ni una medición experimental; no se publican métricas de rendimiento no verificadas.

## Trabajo pendiente prioritario

1. Corregir el protocolo de evaluación: AP estándar con ordenamiento por confianza, emparejamiento por clase e IoU, y mIoU multiclase.
2. Separar entrenamiento, validación y prueba; no evaluar un clasificador con las mismas muestras usadas para entrenarlo.
3. Incorporar Cityscapes o BDD100K y una evaluación con condiciones reales, conservando los escenarios sintéticos como experimento adicional.
4. Definir claramente clases comunes para comparar ambos enfoques y documentar categorías no cubiertas por VOC/COCO.
5. Corregir la salida de vídeo y los parámetros CLI que hoy no se aplican a la ruta de vídeo.
6. Sustituir o renombrar el backend `onnx_cv2` para que el nombre describa lo que ejecuta.
7. Añadir una matriz de confusión de detección/clasificación basada en predicciones de prueba y ejemplos de falsos positivos/negativos.
8. Ejecutar la suite de pruebas en un entorno compatible y registrar versiones, hardware, tiempos y resultados reproducibles.

## Licencia y atribuciones

Los modelos preentrenados y datasets mantienen sus propias licencias y condiciones de uso. Antes de redistribuir pesos o datos, revisar las condiciones de Torchvision, COCO y de cada dataset utilizado. Este repositorio no declara resultados oficiales ni una certificación de benchmark.
