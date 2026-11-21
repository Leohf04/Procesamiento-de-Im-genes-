# Documentación técnica y auditoría del proyecto

**Proyecto:** Equipo 2 — Detección y segmentación semántica en escenas urbanas (multiclase + instancias)  
**Repositorio:** `Leohf04/Procesamiento-de-Im-genes-`  
**Rama auditada:** `main`  
**Tipo de revisión:** inspección estática del código fuente y configuración disponibles  
**Alcance:** documentación del comportamiento observado, cumplimiento de la consigna, riesgos metodológicos y plan de mejora.

---

## 1. Resumen ejecutivo

El repositorio contiene un prototipo de percepción urbana con dos rutas principales:

1. **Instancias:** Mask R-CNN ResNet-50 FPN V2 de Torchvision, que entrega cajas, clases, puntuaciones y máscaras individuales.
2. **Híbrida:** DeepLabV3 ResNet-50 para mapa semántico, Faster R-CNN ResNet-50 FPN V2 para detección por cajas y extracción heurística HSV de carriles.

También hay transformaciones de iluminación/clima, extracción de características HOG e histogramas HSV, un clasificador SVM, un pipeline de imagen/vídeo y un evaluador por escenarios sintéticos.

La base modular es útil para el proyecto académico, pero el estado actual **no demuestra todavía una comparación experimental rigurosa** ni el cumplimiento completo de la evaluación solicitada. Las principales brechas son el protocolo de AP, la evaluación multiclase de segmentación, la ausencia de entrenamiento/validación separados y el uso de COCO val2017 con degradaciones sintéticas en lugar de un dataset urbano con condiciones reales.

No se ejecutaron los modelos ni las pruebas en un entorno de ejecución durante esta auditoría. Las conclusiones siguientes derivan de leer los archivos; no son resultados de ejecución.

## 2. Objetivo académico y alcance

La consigna solicita detectar y segmentar peatones, vehículos, ciclistas, señales y carriles; comparar segmentación por instancias con segmentación semántica complementada por detección; evaluar robustez en día/noche, lluvia y niebla; extraer características para clasificación fina; y reportar mAP, IoU/mIoU y FPS.

La configuración actual declara estas ocho clases COCO:

| ID COCO | Nombre usado por el proyecto |
|---:|---|
| 1 | person |
| 2 | bicycle |
| 3 | car |
| 4 | motorcycle |
| 6 | bus |
| 8 | truck |
| 10 | traffic light |
| 13 | stop sign |

Para las máscaras semánticas comparables se usa un subconjunto de cinco clases: persona, bicicleta, automóvil, motocicleta y autobús.

## 3. Arquitectura y flujo

### 3.1 Configuración

Archivo: `configs/config.yaml`

Centraliza:
- Backend y dispositivo (`auto`, `torch`, `onnx_cv2`).
- COCO val2017 y rutas locales.
- Parámetros de corrección gamma, exposición, niebla, lluvia y motion blur.
- Umbrales de detección y máscaras.
- Categorías objetivo y mapa de nombres para clasificación fina.
- Escenarios y directorio de resultados.

### 3.2 Pipeline principal

Archivo: `src/pipeline.py`

`UrbanPerceptionPipeline` carga la configuración, elige el modelo según `approach`, ejecuta predicción por frame y aplica el clasificador fino a cada caja detectada.

Rutas:
- `approach="instance"`: Mask R-CNN cuando el backend es Torch.
- `approach="hybrid"`: DeepLabV3 + Faster R-CNN cuando el backend es Torch.
- Backend ligero: instancia HOG; no ejecuta las redes neuronales.

El pipeline también procesa streams de vídeo con OpenCV y puede escribir una salida cuando recibe `output_video_path`.

### 3.3 Segmentación por instancias

Archivo: `src/models/instance_seg.py`

Con Torch:
- Inicializa `maskrcnn_resnet50_fpn_v2` con pesos preentrenados.
- Filtra detecciones por confianza y clases permitidas.
- Devuelve cajas, IDs, nombres, puntuaciones y máscaras binarias individuales.
- Construye máscaras agregadas para cinco clases compartidas y para el conjunto de ocho clases.

Limitación: se cargan pesos preentrenados, pero no existe en el flujo inspeccionado una rutina de fine-tuning de Mask R-CNN sobre un dataset de escenas urbanas.

### 3.4 Enfoque semántico/híbrido

Archivo: `src/models/semantic_hybrid.py`

- DeepLabV3 ResNet-50 produce logits semánticos y se obtiene la clase por píxel.
- Se seleccionan IDs VOC [2, 6, 7, 14, 15] para formar una máscara urbana binaria.
- Faster R-CNN produce detecciones con cajas y puntuaciones.
- HSV separa marcas de carril blancas y amarillas en una región inferior de la imagen.

Aclaraciones:
- La arquitectura implementada es **DeepLabV3**, no DeepLabV3+.
- Faster R-CNN es un detector de cajas, no un segmentador de instancias.
- La máscara de carril es heurística, no una predicción aprendida.
- El conjunto de categorías VOC de DeepLab no coincide exactamente con las ocho clases objetivo; por ejemplo, no cubre camión, semáforo ni señal de stop como clases semánticas específicas.

### 3.5 Backend `onnx_cv2`

Aunque el nombre sugiere inferencia ONNX, el código inspeccionado no carga archivos ONNX ni usa ONNX Runtime. En su lugar:
- HOG de OpenCV detecta peatones.
- El modelo de instancias genera una elipse aproximada dentro de cada caja, no una máscara segmentada por una red.
- El híbrido genera máscara de peatones desde las cajas y usa HSV para carriles.

Debe describirse como backend clásico/demostrativo o implementarse realmente ONNX. Sus resultados no deben compararse como si fueran equivalentes a Mask R-CNN o DeepLabV3.

## 4. Preprocesamiento

Archivos: `src/preprocessing/illumination.py` y `src/preprocessing/atmospheric.py`.

| Operación | Implementación | Observación |
|---|---|---|
| Exposición | `cv2.convertScaleAbs` con alpha/beta | Ajuste lineal |
| Gamma | LUT de 256 valores | Rechaza gamma no positivo |
| Baja iluminación | CLAHE en canal L de LAB | Mejora contraste local |
| Motion blur | Kernel direccional normalizado | Desenfoque sintético |
| Niebla | Modelo de transmisión y luz atmosférica | Profundidad aproximada por perfil vertical |
| Lluvia | Trazos aleatorios, blur y oscurecimiento | Simulación visual sintética |

El evaluador transforma la imagen, pero conserva la máscara GT original, lo cual es correcto para evaluar robustez ante degradaciones aplicadas a la entrada.

La consigna menciona aumentos realistas. Las transformaciones implementadas son útiles como aproximación, pero conviene documentar parámetros y límites de realismo y, sobre todo, añadir condiciones capturadas realmente en lluvia, niebla y noche.

## 5. Dataset y anotaciones

Archivos: `scripts/download_coco_val2017.py`, `src/utils/coco_loader.py`.

La configuración utiliza COCO val2017. El cargador:
1. Lee el JSON de instancias.
2. Filtra las ocho categorías definidas en `COCO_URBAN_ID_TO_NAME`.
3. Selecciona imágenes con al menos una anotación urbana.
4. Convierte bbox COCO [x, y, ancho, alto] a [x1, y1, x2, y2].
5. Decodifica segmentaciones poligonales o RLE si está disponible `pycocotools`.
6. Crea una máscara agregada de ocho categorías y otra de cinco clases compartidas.

Consideraciones:
- El script descarga COCO val2017 y el archivo de anotaciones trainval2017; el proyecto evalúa el subconjunto val.
- En ausencia de pycocotools, el fallback rasteriza polígonos, pero no decodifica RLE comprimido. Algunas máscaras pueden quedar vacías si el dataset usa esa representación.
- Cityscapes, BDD100K y KITTI no aparecen como loaders integrados en el árbol revisado.
- COCO no tiene una etiqueta de escenario meteorológico para cada muestra en el flujo actual. Noche, lluvia, niebla y motion blur se crean sintéticamente.
- Usar val2017 para ajustar el clasificador SVM y después reportar la misma colección como evaluación introduce fuga de evaluación si no se separan explícitamente los datos.

**Recomendación:** incorporar BDD100K para variabilidad de clima/iluminación y Cityscapes para segmentación urbana a nivel de píxel. Separar train/validation/test por secuencia o identidad de escena, no por fotogramas aleatorios contiguos.

## 6. Clasificación fina

Archivos: `src/features/descriptors.py`, `src/features/fine_classifier.py`.

Características:
- HOG con ventana 64×128.
- Histograma HSV con 8×4×2 bins.
- Concatenación de ambos descriptores.
- Pipeline StandardScaler + LinearSVC.

El entrenamiento extrae ROIs a partir de cajas GT y limita el número de ROIs por clase. La función devuelve una matriz de confusión calculada sobre las mismas muestras usadas para ajustar el SVM.

Riesgos y mejoras:
- La matriz de entrenamiento no estima generalización; se necesita un conjunto hold-out o validación cruzada.
- La calidad de clasificación depende de las etiquetas finas disponibles. En la configuración hay prefijos/nombres de subclase, pero no se observa un dataset anotado con subclases como sedán/SUV, tipos de señal, etc.
- Cuando no hay modelo entrenado, la predicción devuelve una etiqueta marcada como `svm_untrained`; no es una clasificación fina válida.
- Para clasificación de señales se necesita dataset y anotación de tipos de señales; COCO solo ofrece `stop sign` y `traffic light` en el mapeo usado.

## 7. Evaluación y métricas

Archivos: `src/evaluation/metrics.py`, `src/evaluation/trainer.py`, `src/evaluation/error_analysis.py`, `evaluate_scenarios.py`.

### 7.1 IoU de cajas

`compute_box_iou` implementa intersección sobre unión de dos cajas. Es una base correcta para el emparejamiento.

### 7.2 mAP / AP

La función llamada `compute_average_precision_per_image` no calcula AP estándar:
- Obtiene TP por imagen y divide por el número de objetos GT de esa clase.
- Promedia ese valor entre imágenes.
- No construye curva precisión-recall.
- No ordena globalmente las detecciones por confianza.
- No integra el área bajo la curva ni reproduce el protocolo COCO AP.
- El emparejamiento greedy sigue el orden de las predicciones y no el orden de confianza.

Por tanto, el campo `mAP50` es una aproximación interna y **no debe presentarse como mAP oficial comparable con papers o benchmarks**.

Además, los contadores globales TP/FP/FN de `ScenarioEvaluator` emparejan cajas sin exigir igualdad de clase. Una caja predicha de una clase podría emparejarse con GT de otra clase. Esto sesga precisión y recall globales.

### 7.3 mIoU

`compute_semantic_miou` convierte cualquier valor positivo en foreground y evalúa dos clases: fondo y unión de objetos. Es mIoU binario agregado, no mIoU multiclase por clase.

La evaluación híbrida compara la unión de clases seleccionadas por DeepLab con la unión GT del subconjunto común de cinco categorías. Para Mask R-CNN también se usa una máscara agregada, por lo que se pierde la identidad semántica por clase.

### 7.4 FPS y latencia

El evaluador mide tiempo de llamada a `model.predict` y calcula FPS como inverso de la latencia media. No incluye necesariamente carga de vídeo, decodificación, visualización ni escritura. En GPU no hay sincronización explícita antes de detener el cronómetro, por lo que la latencia CUDA podría subestimarse según el comportamiento asíncrono.

Para resultados comparables, medir warm-up, sincronizar CUDA cuando corresponda, fijar resolución y hardware, e informar latencia p50/p95 además de FPS.

### 7.5 Matriz de confusión y fallos

La matriz de confusión actual se crea durante el entrenamiento del SVM y no representa el detector/segmentador completo. La visualización de fallos dibuja GT y predicciones, pero no clasifica de forma exhaustiva falsos positivos, falsos negativos y errores de clase.

Se recomienda:
- Matriz de confusión de clasificación fina sobre test.
- Matriz de confusión de detección con emparejamiento por IoU y clase.
- Muestras separadas por escenario y tipo de error.
- Métricas por clase y soporte de cada clase.

## 8. Revisión del CLI y ejecución

### 8.1 Entrada de imagen

`main.py` permite procesar una imagen, aplicar un escenario y guardar una imagen resultante. El argumento se llama `--save-video`, pero en la ruta de imagen se utiliza `cv2.imwrite`; el nombre no describe su función.

### 8.2 Entrada de vídeo/cámara

La función `process_video_source` llama a `pipeline.process_video_stream` con `output_video_path=None`. Por ello, el argumento CLI `--save-video` no se transmite al writer para vídeo/cámara y no se guarda el vídeo procesado desde esa ruta.

También existe un parámetro `gui` en `process_video_source` que no se utiliza. La lógica de CLI debe separarse en opciones claras, por ejemplo `--save-image` y `--save-video`, y pasar la ruta de salida al pipeline.

## 9. Pruebas y verificación

Archivos: `tests/test_system_integrity.py`, `scripts/verify_setup.py`.

La suite contiene pruebas de:
- Carga de configuración y resolución de backend.
- Error cuando no existe dataset.
- Carga COCO sintética y construcción de máscaras.
- Decodificación de polígonos.
- IoU y mIoU.
- Clasificador SVM no entrenado y entrenamiento básico.
- Escritura de vídeo con un modelo simulado.
- Exportación de imagen de fallo.
- Ruta de inferencia Torch, condicionada a disponibilidad de PyTorch.

No se ejecutaron estas pruebas durante esta auditoría. La prueba Torch puede descargar pesos preentrenados y depender de conectividad y compatibilidad Torch/Torchvision. El test del SVM evalúa y predice sobre las mismas muestras sintéticas, por lo que verifica el flujo de ejecución, no la calidad de generalización.

Comandos recomendados:

```bash
python scripts/verify_setup.py
pytest -q
```

## 10. Matriz de cumplimiento de la consigna

| Requisito | Estado observado | Evaluación |
|---|---|---|
| Ajuste de exposición | Implementado | Parcial: función existe; integración configurable no completa en todos los flujos |
| Corrección gamma | Implementada | Cumple funcionalmente como transformación |
| Aumentos de motion blur | Implementado | Sintético |
| Aumentos de niebla | Implementado | Sintético |
| Variación de brillo/iluminación | Implementada | Gamma, exposición y CLAHE |
| Mask R-CNN | Implementado con pesos preentrenados | No se observa fine-tuning urbano |
| DeepLabV3+ | No | Se usa DeepLabV3 |
| Segmentación semántica | Implementada | Solo máscara urbana binaria para evaluación |
| Detector complementario | Implementado | Faster R-CNN en enfoque híbrido |
| Segmentación de carriles | Heurística HSV | No es segmentador aprendido |
| Extracción de características | Implementada | HOG + histograma HSV |
| Clasificación fina | Parcial | SVM, pero sin evidencia de dataset fino separado |
| Tracking básico | No observado | Opcional según consigna |
| Evaluación día/noche | Parcial | Día limpio y noche sintética |
| Evaluación lluvia/niebla | Parcial | Degradaciones sintéticas, no datos reales |
| mAP por clase | Parcial/no estándar | Debe corregirse antes de reportar como mAP |
| IoU/mIoU | Parcial | IoU de caja y mIoU binario |
| FPS | Implementado | Requiere protocolo de medición reproducible |
| Matriz de confusión | Parcial | Solo SVM y sobre entrenamiento |
| Ejemplos de fallo | Parcial | Se pueden guardar imágenes, falta clasificación de errores |

## 11. Hallazgos priorizados

### Críticos — corregir antes de presentar resultados

1. **Métrica AP no estándar:** renombrar como indicador aproximado o implementar AP de verdad.
2. **Emparejamiento sin clase en TP/FP/FN globales:** corregir para exigir clase correcta.
3. **mIoU binario presentado como mIoU general:** reportar explícitamente que es binario o implementar métricas multiclase.
4. **Fuga de evaluación del SVM:** crear particiones independientes para entrenamiento y prueba.
5. **Condiciones meteorológicas sintéticas solamente:** añadir evaluación real o limitar las conclusiones a robustez sintética.

### Altos — coherencia funcional

6. Corregir propagación de `--save-video` en procesamiento de vídeo.
7. Cambiar nombre/documentación del backend `onnx_cv2` o implementar ONNX real.
8. Documentar que DeepLabV3 no es DeepLabV3+ y que Faster R-CNN no produce máscaras.
9. Definir el alcance real de clases: señales, semáforos y carriles requieren fuentes/anotaciones adecuadas.
10. Añadir matriz de confusión de detección/clasificación sobre test.

### Medios — reproducibilidad y calidad

11. Registrar versiones exactas de dependencias, hardware, dispositivo y resolución.
12. Medir latencia después de warm-up y sincronizar GPU.
13. Documentar el fallback de máscaras COCO sin pycocotools, especialmente para RLE.
14. Añadir pruebas unitarias para métricas por clase, falsos positivos, falsos negativos, cajas vacías y máscaras multiclase.
15. Evaluar BDD100K/Cityscapes y documentar la correspondencia de etiquetas.

## 12. Plan de trabajo recomendado

### Fase 1 — Corregir evaluación
- Implementar matching por clase e IoU.
- Calcular AP por clase con ranking de confianza y curva precisión-recall.
- Calcular mIoU por clase sobre mapas de etiquetas enteras.
- Crear matrices de confusión y métricas de clasificación sobre conjunto de test.
- Mantener nombres diferenciados entre métricas aproximadas históricas y métricas estándar nuevas.

### Fase 2 — Dataset urbano y particiones
- Integrar BDD100K para detección/condiciones y Cityscapes para segmentación semántica.
- Definir mapeo de clases y política de clases ignoradas.
- Crear train/validation/test evitando contaminación entre secuencias.
- Mantener COCO como baseline auxiliar, no como único benchmark urbano.

### Fase 3 — Comparación justa de modelos
- Establecer las mismas clases, imágenes, resolución y umbrales de evaluación.
- Comparar Mask R-CNN contra DeepLabV3 + detector.
- Separar resultados de segmentación semántica, instancias y detección.
- Aclarar qué clases no puede predecir cada arquitectura.

### Fase 4 — Clasificación fina y robustez
- Anotar subclases de vehículos y señales.
- Entrenar SVM/otro clasificador con partición independiente.
- Evaluar condiciones reales y sintéticas por separado.
- Analizar errores por clase y escenario.

### Fase 5 — Rendimiento y entrega
- Corregir salida de vídeo.
- Medir FPS/latencia en hardware documentado.
- Ejecutar pruebas y guardar logs.
- Añadir ejemplos visuales y tablas reproducibles a la memoria académica.

## 13. Comandos de referencia

```bash
# Verificar dependencias y módulos
python scripts/verify_setup.py

# Descargar COCO val2017
python scripts/download_coco_val2017.py

# Ejecutar pruebas
pytest -q

# Inferencia con Mask R-CNN
python main.py --source ruta/imagen.jpg --approach instance --backend torch --no-gui

# Inferencia con el enfoque híbrido
python main.py --source ruta/imagen.jpg --approach hybrid --backend torch --no-gui

# Evaluación exploratoria
python evaluate_scenarios.py --approach instance --backend torch --max-samples 30
python evaluate_scenarios.py --approach hybrid --backend torch --max-samples 30
```

## 14. Conclusión

El repositorio ya tiene una estructura modular y un prototipo que integra modelos de detección/segmentación, transformaciones de imagen, extracción de características y evaluación por escenarios. Es una base aprovechable para la entrega universitaria.

Sin embargo, las métricas actuales y el conjunto de datos no permiten afirmar todavía que se haya completado una comparación científica de segmentación urbana multiclase y robustez real. La prioridad debe ser corregir el protocolo de evaluación, separar los datos de entrenamiento y prueba, integrar datasets urbanos apropiados y dejar claro el alcance real de cada arquitectura.

**No se incluyen valores de mAP, mIoU o FPS en este documento porque no se ejecutó un experimento reproducible durante la auditoría.**
