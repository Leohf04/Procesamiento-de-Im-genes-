# Ejecutor de entrenamiento multidominio

**Estado: pipeline de ejecución implementado en código, pendiente de validación integral; no iniciar el piloto todavía.**

## Componentes

- `src/urban_experiment_runner.py`: loops por tarea/dominio, pérdidas finitas, validación semántica (mIoU, mean/pixel accuracy, IoU/soporte por clase y matriz de confusión), early stopping, límite temporal por época, scheduler, AMP opcional solo CUDA, clipping opcional, métricas JSONL, checkpoints atómicos y reanudación.
- `scripts/materialize_urban_experiment_data.py`: descarga al almacenamiento del runtime remoto solo train/validation de A2D2 y UrbanSyn a partir de manifests completos y sus índices. No toca test ni necesita transferir archivos por el teléfono.
- `scripts/urban_experiment_factory.py`: construye datasets, loaders, modelo y optimizer para un experimento/dominio. Requiere que el materializador ya haya generado manifests locales.
- `src/urban_coco_evaluator.py`: evalúa Box AP y Mask AP con `pycocotools.COCOeval`, manteniendo RLE binario en memoria y reportando AP@[.50:.95], AP50/AP75 y soporte por clase. Si faltan `pycocotools` o ground truths de validación, falla explícitamente.
- `scripts/run_urban_experiment.py`: CLI protegida por `run_training: true` en config y `--execute`. La factory solo entrega train/validation; no se acepta test.
- Tests: `tests/test_urban_experiment_runner.py` y `tests/test_urban_coco_evaluator.py`.

## Preflight de datos reales sin entrenamiento\n\nNotebook operativo: `notebooks/colab_preflight_datos_reales.ipynb`. Recupera el artifact de anotaciones existente, reconstruye manifests e índices y realiza dos etapas limitadas: preflight remoto y descarga de una muestra train/val con instancias positivas por dominio. El límite por ejecución de muestra es 2 GiB. Los archivos de muestra quedan en el disco temporal de Colab; solo informes/logs se guardan en Drive.\n\nEl materializador `scripts/materialize_urban_experiment_data.py` ofrece `--dry-run`, `--max-samples-per-split`, `--require-instances` y `--max-total-bytes`. El dry-run consulta tamaños S3/Hugging Face y valida IDs sin descargar assets. La materialización escribe manifests e índices locales alineados por `sample_id`; nunca procesa test.\n\n`scripts/smoke_test_urban_experiment_factory.py` prueba los cuatro loaders reales, forward semántico, COCOeval real en una muestra de validación y round-trip de checkpoint/RNG. Está diseñado para cero llamadas a `backward()` y `optimizer.step()`.\n\n**Estado de esta fase:** implementada en código y notebook, aún no ejecutada por el usuario. No hay materialización confirmada ni COCOeval real aprobado.\n\n## Flujo de preparación para piloto (no ejecutar aún)

1. En el runtime remoto, reconstruir los manifests completos sin cap y tener los JSONL de anotaciones completos en carpetas separadas.
2. Instalar dependencias si faltan: `boto3`, `huggingface_hub`, `pycocotools`.
3. Materializar solo train/val:

```bash
python scripts/materialize_urban_experiment_data.py \
  --manifest-dir /RUTA/manifests \
  --annotation-index-dir /RUTA/annotation_index \
  --output-dir /RUTA/urban_data
```

El materializador verifica IDs únicos, igualdad de IDs manifest/index y `annotation_status=ok`; persiste un informe. No descargar test. El directorio resultante puede ser grande y debe estar en almacenamiento persistente remoto, nunca en el teléfono.

## Contrato de configuración y ejecución (plantilla bloqueada)

```json
{
  "run_training": false,
  "experiment_id": "SEM-URBANSYN",
  "dataset": "urbansyn",
  "task": "semantic",
  "data_dir": "/RUTA/urban_data",
  "annotation_index_dir": "/RUTA/annotation_index",
  "image_size": 512,
  "batch_size": 1,
  "validation_batch_size": 1,
  "num_workers": 2,
  "num_classes": 20,
  "ignore_index": 255,
  "learning_rate": 0.001,
  "weight_decay": 0.0001,
  "momentum": 0.9,
  "seed": 2026,
  "max_epochs": 5,
  "patience": 2,
  "min_delta": 0.0,
  "max_seconds": 5400,
  "amp": false
}
```

La plantilla solo ilustra campos; LR, batch, resolución, workers, pesos iniciales y AMP deben fijarse después del preflight. La factory actual inicializa DeepLabV3+ y Mask R-CNN sin pesos preentrenados. No comparar esta inicialización con experimentos que usen pesos distintos sin declararlo.

Comando futuro, únicamente después de autorización independiente para el piloto:

```bash
python -m scripts.run_urban_experiment \
  --config /RUTA/experiment_config.json \
  --factory scripts.urban_experiment_factory:create_experiment \
  --output-dir /RUTA/resultados/SEM-URBANSYN \
  --execute
```

Para reanudar, añadir `--resume /RUTA/resultados/SEM-URBANSYN/last.pt`. El hash de configuración debe coincidir exactamente. Ejecutar cada uno de los cuatro experimentos con config y directorio propios.

## Puertas pendientes

1. Ejecutar la suite nueva en Colab sobre el SHA exacto y corregir cualquier fallo.
2. Validar el evaluador COCO con su prueba sintética y luego con una muestra real de validación; no se ha ejecutado todavía esta verificación.
3. Ejecutar materialización y smoke de loaders train/validation (sin optimización) para cada uno de los cuatro experimentos; comprobar espacio, hashes, IDs y targets.
4. Probar checkpoint/resume con esos loaders y verificar persistencia GPU/runtime.
5. Confirmar hiperparámetros, memoria y presupuesto. El materializador puede descargar miles de imágenes/etiquetas al runtime remoto, por lo que no debe lanzarse antes de tener almacenamiento suficiente.

La implementación no se ha ejecutado en datos reales ni en GPU. No hay épocas ni checkpoints experimentales. `RUN_TRAINING=False` permanece y la CLI exige además `--execute`; ninguna de estas medidas sustituye la autorización expresa del piloto. PR #3 permanece draft y sin merge.


## Auditoría de capacidad y materialización incremental (sin entrenamiento)

Notebook: `notebooks/colab_auditoria_capacidad_incremental.ipynb`.

- Reconstruye manifests/índices completos desde el artifact de anotaciones verificado; compara IDs y estadísticas para train/val/test. El acceso a test se limita a verificar metadatos; no descarga ni decodifica activos de test.
- Dry-run de hasta 50 muestras por dataset/split (200 candidatas en total), solo filas con instancias positivas; límite 2 GiB. No descarga activos.
- Segundo dry-run de 10 muestras por dataset/split (40 muestras); requiere espacio libre de al menos 2× bytes estimados + 1 GiB antes de materializar.
- Materializa solo esas 40 muestras train/val y comprueba manifiestos/índices locales alineados. Datos temporales en `/content/urban_data_capacity`; solo informes/logs se guardan en Drive.
- `scripts/audit_urban_materialized_capacity.py` recorre cada elemento de cada dataset local una vez por ruta semántica y una vez por ruta de instancias, valida tensores/targets y mide bytes materializados, espacio libre y RSS pico/tiempo de decodificación. No realiza forward, backward, optimizer.step ni entrenamiento.
- La selección usa prefijo determinista de filas elegibles con instancias, no balanceo estratificado ni muestra estadísticamente representativa. El resultado sirve para dimensionar almacenamiento/lectura, no para métricas de modelo.
- El siguiente tamaño de lote se decide tras revisar los JSON de entorno, estimaciones, materialización y auditoría. No escalar automáticamente al dataset completo ni iniciar entrenamiento.



## Preflight de hardware y Drive

Notebook: notebooks/colab_preflight_entorno_entrenamiento.ipynb

Ejecuta el notebook en Colab después de seleccionar GPU (si está disponible). El script scripts/audit_training_runtime.py registra GPU/CUDA/VRAM, RAM y disco, y prueba un checkpoint sintético de escritura/lectura en el Drive montado. No instala dependencias, no descarga datasets ni ejecuta modelos.

El informe queda en MyDrive/ProcesamientoImagenes/auditoria_entorno_entrenamiento/training_runtime_preflight.json.

Puerta de decisión: si GPU_PASS es falso, detenerse; no ejecutar piloto en CPU. DRIVE_IO_PASS solo valida el montaje actual y no sustituye una prueba de recuperación tras reconectar Drive. Incluso con PREFLIGHT_READY=True, falta la prueba de memoria con batch real de cada arquitectura y la autorización expresa del piloto. RUN_TRAINING=False permanece.
