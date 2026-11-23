# Protocolo de entrenamiento experimental multidataset

**Versión:** `urban-exp-v1`  
**Estado:** propuesta técnica documentada; **no autorizada para ejecución**  
**Rama:** `urban-models-and-benchmark`  
**Ontología:** `urban-v1`  
**Regla operativa:** `RUN_TRAINING=False` hasta cerrar las puertas de entrada y recibir autorización expresa para el experimento.

## 1. Objetivo y alcance

Definir un baseline reproducible para entrenar y evaluar segmentación semántica e instancias en escenas urbanas con A2D2 y UrbanSyn. El protocolo separa dominios, tareas, métricas y checkpoints. No concatena muestras de dominios distintos ni presenta los datos sintéticos como datos reales.

El experimento inicial no incluye SHIFT: la auditoría de PTS concluyó que RGB y semseg no están temporalmente alineados. Tampoco incluye Cityscapes ni Waymo.

### Matriz de experimentos

| ID | Modelo/tarea | Train | Validación | Test final | Papel |
|---|---|---|---|---|---|
| S-A2D2 | DeepLabV3+, semántica (20 logits, ignore 255) | A2D2 train | A2D2 val | A2D2 test | Dominio real |
| S-UrbanSyn | DeepLabV3+, semántica (20 logits, ignore 255) | UrbanSyn train | UrbanSyn val | UrbanSyn test | Dominio sintético |
| I-UrbanSyn | Mask R-CNN, máscaras + cajas (9 labels incluyendo background) | UrbanSyn train | UrbanSyn val | UrbanSyn test | Baseline principal de instancias |
| I-A2D2 | Mask R-CNN, máscaras reconstruidas + cajas | A2D2 train | A2D2 val | A2D2 test | Experimento complementario/ablación |

Cada fila es un entrenamiento independiente con inicialización independiente. No compartir pesos, optimizer, scheduler, sampler ni estadísticas entre dominios en el baseline. No mezclar A2D2 y UrbanSyn en un mismo DataLoader.

**Prioridad científica:** UrbanSyn es la referencia principal para instancias porque tiene panoptic y bbox2D consistentes en las auditorías. A2D2 es complementario: sus instancias son componentes conectados reconstruidos desde subclases, pueden fragmentar objetos y la cobertura de clases es incompleta. No presentar I-A2D2 como detector equilibrado de las ocho clases.

## 2. Datos y particiones

- Usar los manifiestos completos experimentales ya auditados: A2D2 1.000 train / 1.000 val / 1.000 test; UrbanSyn 1.000 train / 751 val / 783 test.
- Train principal usa **todas las filas train válidas**, no el plan cap200. Cap200 queda reservado para ablación. Cap500/cap700 solo se ejecutan como ablaciones explícitas posteriores.
- Validation y test se conservan completos, en su split original y sin muestreo balanceado. No calcular pesos, frecuencias, umbrales, normalizaciones aprendidas ni decisiones de selección usando test.
- Respetar la separación por secuencia de A2D2 ya definida en sus manifiestos. UrbanSyn se agrupó por sample ID porque no se verificó metadata de secuencia; describir esta limitación y no afirmar independencia temporal de escenas.
- Un registro solo entra al experimento si el manifiesto y el índice de anotaciones coinciden exactamente en `sample_id`, orden, unicidad y estado `annotation_status=ok`. Cualquier discrepancia detiene el experimento.
- Verificar que todos los assets requeridos sean accesibles, que las dimensiones RGB/target coincidan y que las máscaras/cajas sean válidas. No descargar el dataset completo al Drive personal: materializar solo los splits y archivos necesarios en el almacenamiento de Colab/Drive siguiendo las condiciones de licencia.
- Mantener trazabilidad de revisión de UrbanSyn (`8599498aceee9072f1e067a4a4efed7f20b11809`) y de la fuente/versionado A2D2.

### Licencias y distribución

Aplicar el criterio conservador ya registrado: UrbanSyn CC BY-NC-SA 4.0 hasta aclaración escrita de la discrepancia publicada. A2D2 CC BY-ND 4.0. No subir RGB, máscaras, anotaciones originales ni derivados restringidos al repositorio, artifacts públicos o informes compartidos. Los checkpoints pueden incorporar información derivada de los datos: conservarlos en almacenamiento privado y revisar las condiciones antes de distribuirlos.

## 3. Ontología y tratamiento de clases

- Cargar siempre `configs/urban_ontology_v1.json`; no hardcodear IDs en el loop.
- Semántica: 20 logits, IDs 0–19, `ignore_index=255`. UrbanSyn trainId 19 (unlabeled) se convierte en ignore. Las clases A2D2 fuera del mapeo también son ignore.
- Instancias: IDs 1–8; 0 es background. `rider` y `bicycle` son clases distintas. Lane marking es semántica, nunca instancia.
- Los pesos semánticos se calculan **solo** desde `semantic_pixels` de train del dataset actual mediante `semantic_class_weights`. Clases ausentes en train tienen peso cero y se reportan como no entrenables; no se inventa cobertura.
- El sampler de instancias se construye **solo** con `instance_counts` de train del dataset actual mediante `make_instance_sampler`. Registrar semilla y distribución efectiva de muestreo.
- No aplicar pesos/samplers a val/test. No combinar estadísticas de A2D2 y UrbanSyn.
- Para I-A2D2, reportar las clases disponibles/ausentes del split. Las máscaras por componentes conectados no equivalen a IDs de instancia nativos y esta limitación debe aparecer en resultados.

## 4. Configuración inicial propuesta

Valores conservadores para un primer baseline en Colab GPU T4. Son hiperparámetros iniciales sujetos a un piloto de memoria/tiempo; no son resultados medidos ni garantía de que quepan en cualquier runtime.

| Parámetro | Semántica (DeepLabV3+) | Instancias (Mask R-CNN) |
|---|---:|---:|
| Resolución de entrada | 512×512 | 512×512 |
| Batch size inicial | 4 | 1 |
| Gradient accumulation | 1 | 2 |
| Épocas máximas | 20 | 20 |
| Optimizer | AdamW | SGD |
| Learning rate inicial | 1e-4 | 2.5e-3 |
| Weight decay | 1e-4 | 5e-4 |
| Scheduler | ReduceLROnPlateau | ReduceLROnPlateau |
| Factor scheduler | 0.5 | 0.5 |
| Paciencia scheduler | 2 validaciones | 2 validaciones |
| Early stopping | 5 validaciones sin mejora | 5 validaciones sin mejora |
| Gradient clipping | norm 1.0 | norm 1.0 |
| Semilla base | 2026 | 2026 |

Reglas de ajuste:
1. Antes del entrenamiento completo, hacer un piloto de 10 batches train por cada configuración en GPU: medir pico CUDA, RSS, tiempo/batch, loss finita y gradientes finitos. Este piloto es una ejecución de entrenamiento y requiere autorización; no se ejecuta como parte de esta documentación.
2. Si no cabe en GPU, reducir primero batch size (semántica 2; instancias mantener 1), activar mixed precision solo tras comprobar estabilidad y reducir resolución a 384×384 como último ajuste. Registrar el cambio como una nueva configuración; no cambiar parámetros a mitad de un run sin nuevo ID.
3. Para Mask R-CNN, no aumentar batch mediante duplicación artificial de imágenes. La acumulación de gradientes se debe implementar explícitamente y verificar que la loss se escala correctamente.
4. Si el sampler de instancias usa reemplazo, una época representa `len(train_dataset)` extracciones, no una pasada única por cada imagen. Documentar esta definición.
5. Registrar hardware real, versión de PyTorch/torchvision/CUDA, precisión numérica, resolución y batch efectivos. Si Colab ofrece CPU, no iniciar por defecto el baseline completo.

## 5. Entrenamiento, validación y selección del checkpoint

- Entrenar cada fila de la matriz por separado, con su propio seed, modelo, optimizer, scheduler, sampler y directorio de resultados.
- Validar al final de cada época en el split val completo, en `eval()` y sin gradientes. La evaluación no debe usar sampler ponderado.
- DeepLabV3+: calcular matriz de confusión acumulada ignorando 255; reportar IoU por clase, mIoU sobre clases presentes/definidas, pixel accuracy y frecuencia/soporte por clase. Publicar además mIoU macro sobre el conjunto fijo de clases evaluables, especificando cómo se tratan clases ausentes.
- Mask R-CNN: calcular Mask AP, AP50, AP75 y AP por clase; reportar Box AP por separado. Usar evaluador COCO-compatible con conversión verificada de IDs/cajas/máscaras. Si no puede garantizarse evaluación COCO correcta, detener y completar primero el evaluador; no sustituir AP por loss.
- Monitor primario para selección: val mIoU en semántica; val Mask AP en instancias. Guardar `best` por métrica primaria. Scheduler observa esa métrica; early stopping usa paciencia 5. Si una métrica no puede calcularse por ausencia de positivos/clases, marcarla como no disponible y no elegir checkpoint con una métrica inválida.
- Loss train/val se registra como diagnóstico, no como métrica principal de calidad.
- El test se ejecuta **una sola vez por checkpoint seleccionado** al cerrar cada experimento. No usar test para elegir hiperparámetros, épocas, umbrales o modelos. Si se modifica algo tras ver test, se necesita un nuevo protocolo/test independiente.

## 6. Métricas y análisis obligatorio

Por cada modelo/dataset:
- métricas primarias y por clase descritas arriba, soporte (número de imágenes, píxeles/instancias), clases ausentes y porcentaje de ignore;
- curva de loss train y val, mIoU o AP por época, learning rate, tiempo por época y total;
- matriz de confusión semántica y ejemplos cualitativos seleccionados desde val; predicciones de test solo después de fijar checkpoint;
- para instancias, conteos GT/predicción, AP por clase, Box AP separado y ejemplos de falsos positivos/negativos;
- memoria máxima CUDA/RSS, throughput, resolución, batch efectivo, hardware y versiones;
- seed, hash de manifiestos/índices, commit Git, versión de ontología, configuración completa y hash del checkpoint.

No promediar directamente mIoU de A2D2 y UrbanSyn como si fueran una única población. Presentar métricas separadas. Cualquier promedio agregado será secundario, con definición explícita y solo sobre clases/métricas comparables.

## 7. Checkpoints, logs y reanudación

Guardar en Drive privado, con estructura independiente:
```text
ProcesamientoImagenes/experimentos/urban-exp-v1/
  S-A2D2/{checkpoints,metrics,logs,plots,config}
  S-UrbanSyn/{checkpoints,metrics,logs,plots,config}
  I-A2D2/{checkpoints,metrics,logs,plots,config}
  I-UrbanSyn/{checkpoints,metrics,logs,plots,config}
```

Cada experimento debe guardar:
- `last.pt`: modelo, optimizer, scheduler, epoch, best metric, patience/counter, seed y estados RNG Python/NumPy/Torch/ CUDA;
- `best.pt`: checkpoint seleccionado por validación;
- `history.jsonl`: una fila por época con losses, métricas, LR, tiempos y memoria;
- `config.json`: parámetros efectivos, no solo defaults;
- `run_summary.json`: estado final, commit, hashes de datos/índices, clases evaluables, checkpoint y resultados;
- logs stdout/stderr.

Escritura atómica: escribir a archivo temporal y renombrar al finalizar. Guardar `last.pt` al final de cada época completada y antes de finalizar runtime cuando sea posible. Reanudar solo si arquitectura, ontología, manifiestos, índices y config coinciden; de lo contrario iniciar un nuevo run. Probar primero una restauración de checkpoint en una prueba aislada.

## 8. IDs, semillas y comparación

- ID de ejecución: `{experiment_id}_{dataset}_{task}_seed2026_{config_hash}`.
- Semillas iniciales: 2026; repetir con 2027 y 2028 para estimar variabilidad antes de conclusiones fuertes.
- Activar determinismo de PyTorch cuando sea compatible; registrar operaciones no deterministas y cualquier warning. No afirmar reproducibilidad bit a bit si CUDA/ops no lo garantizan.
- Comparar baseline sin pesos/sampler como control frente al baseline balanceado. Para semántica, el control usa CrossEntropy sin class weights; para instancias, sampler uniforme. Ambos usan el mismo split, arquitectura, epochs y semillas.
- Las ablaciones cap500/cap700/cap200 se ejecutan separadas y nunca sustituyen el baseline de train completo. Reportar retención/cobertura junto a métricas.

## 9. Puertas de entrada antes de autorizar ejecución

No ejecutar el baseline hasta que todas estén verificadas:

1. **Código en HEAD:** suite completa de tests y pruebas de integración del loader sobre el commit exacto. La validación previa de 79 tests y el paso controlado real son evidencia útil, pero se debe repetir la suite en el HEAD final del protocolo.
2. **CI:** resolver o documentar la indisponibilidad de runners de Actions. Los jobs recientes con `runner_id=0` y `steps=[]` no ejecutan pytest y no cuentan como CI aprobado.
3. **Materialización real:** probar dataset completo lógico (todas las filas del manifiesto, no necesariamente mantener todas las imágenes a la vez) con verificación de IDs, conteos, integridad y acceso reproducible. El smoke de una muestra por dataset no valida el ciclo de épocas.
4. **Validadores:** prueba de métricas semánticas y COCO Mask/Box AP con targets sintéticos conocidos; verificar ignore 255, clases ausentes, imágenes sin instancias y conversiones de cajas/máscaras.
5. **Checkpoint:** prueba de guardar, restaurar y reanudar, incluyendo optimizer/scheduler/RNG y detección de config incompatible.
6. **Recursos:** piloto 10 batches en GPU por configuración y confirmar memoria/tiempo; definir duración máxima y estrategia si Colab desconecta.
7. **Datos/licencia:** confirmar almacenamiento privado, no redistribución y atribución. No subir datos ni derivados restringidos.
8. **Configuración:** revisión del archivo de configuración y de las cuatro filas de la matriz; registrar hash y commit.
9. **Autorización:** pedir confirmación expresa del usuario para el piloto y, tras revisar sus resultados, otra confirmación para el entrenamiento completo. La autorización previa para cuatro pasos SGD no autoriza este entrenamiento.

## 10. Criterios de éxito y parada

Un run solo se considera técnicamente válido si completa al menos una época train y validación completa, todas las losses/métricas definidas son finitas, los IDs/targets pasan validación, se guardan checkpoints restaurables y el resumen incluye el commit/config exactos.

Detener inmediatamente ante:
- NaN/Inf en loss, gradientes o parámetros;
- IDs desalineados, targets inválidos o fuga de split;
- clase/métrica evaluada con definición inconsistente;
- OOM persistente después de un único ajuste controlado de recursos;
- checkpoint corrupto/no restaurable;
- almacenamiento insuficiente o pérdida de acceso a los datos;
- duración incompatible con el runtime sin posibilidad de reanudación.

Un experimento interrumpido se marca `INTERRUPTED`, nunca PASS. Un modelo sin métricas válidas de val no se declara mejor ni se evalúa en test.

## 11. Estado de ejecución

Este documento **no habilita entrenamiento**. En el momento de su creación:
- `RUN_TRAINING=False`;
- no se han iniciado épocas;
- no existen checkpoints entrenados;
- el paso controlado previo fue solo cuatro actualizaciones SGD aisladas con pesos aleatorios y muestras train, no entrenamiento de producción;
- la PR #3 debe permanecer abierta, draft y sin fusionar.

**Siguiente acción tras revisar este protocolo:** implementar el runner reproducible, evaluadores, guardado/reanudación y configuración ejecutable; después cerrar las puertas 1–8 y solicitar autorización específica para el piloto de 10 batches. No iniciar entrenamiento completo automáticamente.
