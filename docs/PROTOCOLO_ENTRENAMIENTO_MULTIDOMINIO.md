# Protocolo de entrenamiento experimental multidominio (urban-v1)

**Estado: motor de entrenamiento parcial implementado; pipeline end-to-end aún bloqueado / no autoriza entrenamiento.**  
**Control de seguridad:** `RUN_TRAINING=False`. No cambiarlo hasta cerrar las puertas de preparación y recibir autorización explícita para iniciar el piloto.

## 1. Objetivo y alcance

Evaluar por separado segmentación semántica e instancias en los dominios A2D2 (real) y UrbanSyn (sintético), manteniendo trazabilidad de datos, configuración, checkpoints y métricas. No concatenar muestras ni estadísticas de dominios. No usar SHIFT en el benchmark mientras siga sin alineación temporal PTS. No reactivar Cityscapes/BDD100K heredados como sustitutos de esta estrategia.

Este documento define un protocolo escalonado. La prueba controlada ya aprobada (cuatro actualizaciones SGD sobre una muestra por dominio) solo verificó loss/backward/gradientes/actualización; no es evidencia de convergencia ni de calidad.

## 2. Matriz de experimentos

| ID | Tarea/modelo | Dominio | Papel y restricciones |
|---|---|---|---|
| SEM-A2D2 | DeepLabV3+ | A2D2 | Experimento semántico real; clases sin soporte se reportan como no evaluables |
| SEM-URBANSYN | DeepLabV3+ | UrbanSyn | Experimento semántico sintético, 19 clases fuente más lane-marking solo si el índice confirma soporte |
| INS-URBANSYN | Mask R-CNN | UrbanSyn | Experimento principal de instancias; panoptic/bbox auditados |
| INS-A2D2 | Mask R-CNN | A2D2 | Exploratorio/complementario; reconstrucción por componentes conectados y cobertura incompleta; no afirmar detector urbano de ocho clases |

Cada ID entrena un modelo independiente. No compartir pesos, optimizador, scheduler, sampler ni estadísticas entre dominios. La comparación A2D2 frente a UrbanSyn es por resultados separados y no por una media conjunta.

### Cobertura y ausencias

- UrbanSyn: auditoría ampliada observó 19/19 clases semánticas y 8/8 clases de instancia en los índices examinados.
- A2D2: la auditoría cap200 encontró clases esperadas ausentes en el índice: 12 semánticas y 4 de instancia. La ausencia no se resuelve aumentando el cap. Antes de entrenar, generar un informe actualizado desde los índices completos y fijar por experimento las clases con soporte real.
- Los pesos semánticos de clases sin píxeles en train son cero; dichas clases se marcan explícitamente como no entrenables/no evaluables en ese dominio. No inventar muestras ni sobreinterpretar IoU de clases sin soporte.
- Las instancias A2D2 son componentes conectados derivados de subclases de color, no IDs de instancia nativos. Pueden fragmentar objetos o fusionar semánticas; el resultado A2D2 se etiqueta como aproximado.
- No usar cap 200 como train principal. Baseline: todas las filas train disponibles y válidas. Cap 500/700 solo como ablaciones identificadas, nunca como sustituto del baseline.

## 3. Particiones y prevención de fuga

1. Usar exclusivamente los manifiestos versionados actuales y su revisión/hash; registrar SHA-256 de cada manifiesto e índice JSONL.
2. Train se usa para optimización y estadísticas de pesos/sampler. Validation se usa para selección de checkpoint, early stopping y ajustes declarados. Test queda bloqueado hasta la evaluación final.
3. A2D2 mantiene split por secuencia (18/3/2 secuencias según manifiesto experimental actual). No reagrupar ni mezclar secuencias.
4. UrbanSyn usa los splits por sample ID ya generados; dado que no hay metadata de secuencia verificada, documentar que la independencia temporal no está garantizada.
5. Verificar de nuevo IDs únicos, no solapamiento entre splits, `annotation_status=ok`, correspondencia exacta sample_id ↔ archivo y conteos por clase antes de crear loaders.
6. No calcular pesos, frecuencias, normalizaciones estadísticas ni selección balanceada usando validation/test.
7. El split test se evalúa una sola vez por configuración final elegida. Si se inspecciona para depurar, deja de ser test ciego y debe declararse.

### Estado operativo tras aprobar la suite unitaria — 2026-11-23

La suite completa se ejecutó en Colab sobre SHA `ace39a56a3b46edb0a876cf23d0ea53e67d0aaf3`: 85 passed, prueba dirigida 1 passed. Esto cierra solo la puerta de pruebas unitarias.

La siguiente puerta es `notebooks/colab_preflight_datos_reales.ipynb`: preflight remoto de tamaños y IDs, materialización limitada a una muestra train/val con instancias positivas por dataset, y smoke de los cuatro loaders, forward semántico, COCOeval real y round-trip checkpoint/RNG. El script `scripts/materialize_urban_experiment_data.py` admite dry-run, límite de muestras y presupuesto de bytes; el script `scripts/smoke_test_urban_experiment_factory.py` no llama backward ni optimizer.step. Ninguno se ha ejecutado todavía en este punto. No se considera aprobado hasta recibir el informe generado por Colab.

La materialización completa de train/validation queda para una etapa posterior, solo después del smoke limitado y de comprobar almacenamiento suficiente. Test permanece inaccesible.

## 4. Fase A — preflight antes de cualquier entrenamiento

La ejecución debe abortar si falla cualquiera de estas comprobaciones:

- HEAD/commit, versiones de Python/PyTorch/Torchvision/CUDA, GPU disponible y memoria libre registrados.
- CI pytest aprobado sobre el HEAD exacto o, mientras los runners sigan sin ejecutar jobs, suite completa ejecutada en Colab sobre ese mismo SHA y log persistido. No aceptar un job con `runner_id=0` y `steps=[]` como CI.
- Índices per-image completos para cada split y cobertura por clase actualizada; manifests/annotations emparejados por IDs exactos.
- Loader real de train y validation probado por separado en cada configuración habilitada; comprobar un lote completo, shapes, labels, boxes/masks, valores finitos y muestras no vacías.
- Confirmar licencias y condiciones de uso. UrbanSyn se trata bajo el criterio restrictivo CC BY-NC-SA 4.0 hasta aclaración escrita; no redistribuir imágenes, máscaras ni derivados.
- Confirmar destino persistente, espacio libre y prueba de escritura/lectura de checkpoint de prueba. GitHub no almacena checkpoints grandes.
- Verificar que se puede guardar un checkpoint y reanudarlo en una prueba sin entrenamiento de producción.
- Fijar resolución, batch size y workers mediante prueba de memoria de un batch. No asumir que el smoke test CPU 256×256 predice capacidad GPU.
- Generar `experiment_config.json` inmutable con parámetros, IDs de clases habilitadas, seed, rutas, hashes, origen de pesos y límites.

No empezar si no hay GPU o almacenamiento suficiente. Colab Free puede usarse solo como ejecución por etapas con checkpoints frecuentes; no se presupone duración estable ni GPU garantizada.

## 5. Fase B — piloto acotado

**Configuración inicial propuesta, sujeta al preflight y no ejecutada:**

- Una semilla inicial: 2026.
- Máximo 5 épocas por cada configuración habilitada.
- Evaluación en validation al final de cada época.
- Early stopping con paciencia 2 sobre la métrica primaria, con mínimo de mejora definido en configuración.
- Límite de tiempo por job: 90 minutos de cómputo activo; guardar estado al final de cada época y detener de forma segura al alcanzar el límite.
- Batch size inicial: el mayor que supere el preflight sin OOM, con mínimo 1; registrar el valor real. No acumular gradientes salvo que se configure y documente.
- Resolución inicial de entrenamiento: 512×512 como objetivo; reducir a 384 o 256 solo si la prueba de memoria lo exige y dejarlo como experimento distinto.
- Mixed precision solo si el hardware la soporta y se valida estabilidad; registrar dtype y scaler.
- Optimizer propuesto: SGD momentum 0.9, weight decay 1e-4 para DeepLabV3+; Mask R-CNN puede usar SGD momentum 0.9 y weight decay 5e-4. Learning rate inicial no se hereda del smoke test: debe quedar fijado por configuración y validarse en el piloto.
- Scheduler: reducción por meseta de validation o scheduler por épocas, escoger uno antes de ejecutar; no cambiarlo mirando test.
- Inicialización: declarar explícitamente pesos preentrenados y su procedencia/licencia. No comparar un modelo aleatorio con otro preentrenado. Si no hay pesos compatibles disponibles, usar inicialización aleatoria y etiquetar el piloto como tal.
- Separar optimización semántica e instancias; no entrenar ambas cabezas en un único objetivo multitarea en esta primera fase.

El piloto sirve para verificar que loss desciende de forma razonable, que métricas de validation se calculan, que checkpoints se reanudan y que los límites de recursos son realistas. Cinco épocas no garantizan convergencia.

## 6. Balanceo y pérdidas

### DeepLabV3+ semántico

- Construir un loader y pesos por dominio con `build_urban_train_loaders`; no sumar píxeles A2D2 + UrbanSyn.
- CrossEntropy con `ignore_index=255` y pesos calculados solo con train. Mantener el esquema de pesos inverse-square-root ya implementado, registrando vector completo y clases de peso cero.
- Muestreo de imágenes uniforme en el baseline. Las augmentations deben preservar la semántica y aplicarse igual en train; validation/test solo resize/normalización determinista.
- Registrar porcentaje de píxeles ignore y distribución de clases por split.

### Mask R-CNN

- Loader/sampler independiente por dominio; WeightedRandomSampler usa únicamente conteos de train.
- Excluir targets vacíos solo si el contrato del modelo/loader lo requiere; contar y reportar imágenes vacías, no descartarlas silenciosamente.
- Validar boxes (xyxy, área positiva, dentro de imagen), máscaras binarias, labels en rango y correspondencia box-mask.
- UrbanSyn es la fuente primaria para ocho clases de instancias. A2D2 debe limitar las conclusiones a clases con soporte confirmado; no convertir clases ausentes en negativos fiables.
- Registrar cada componente de loss por época además de la suma.

## 7. Métricas y selección de checkpoint

### Semántica

- Métrica primaria: mIoU macro sobre clases con soporte ground-truth en validation, con la lista de clases y soporte publicadas junto al resultado.
- Además: IoU por clase, pixel accuracy, mean accuracy, matriz de confusión y frecuencia/soporte por clase.
- Ignorar ID 255. Reportar por separado las clases sin soporte en train o validation; nunca asignarles IoU=0 como si fueran errores del modelo. En evaluación, una clase con soporte ground-truth cero tiene IoU `null` incluso si recibe falsos positivos; queda excluida del mIoU macro. Los falsos positivos permanecen visibles en la matriz de confusión y en las métricas de clases con soporte.
- Guardar mejor checkpoint por mIoU de validation y último checkpoint para reanudación.

### Instancias

- Métricas primarias: Box AP@[.50:.95] y Mask AP@[.50:.95] con protocolo COCOeval compatible, más AP50/AP75 por clase y soporte de instancias.
- Si el evaluador disponible no calcula Mask AP correctamente o no coincide con COCOeval, detener el reporte Mask AP; reportar solo la métrica realmente implementada y nombrarla como protocolo interno.
- Documentar IoU thresholds, max detections, score threshold (si aplica), clases y política de imágenes sin objetos.
- No seleccionar checkpoint usando test.

### Rendimiento

El benchmark FPS/latencia es una fase separada después de fijar checkpoint. Medir warmup, sincronizar CUDA, mismo hardware/resolución/backend/número de frames, reportar p50/p95/p99 y FPS; distinguir latencia de modelo de end-to-end. No mezclar estos valores con calidad.

## 8. Checkpoints, reanudación y trazabilidad

Guardar en almacenamiento persistente, por experimento:

- `last.pt`: modelo, optimizer, scheduler, scaler AMP, época, global_step, best_metric, early-stopping counter, RNG Python/NumPy/PyTorch/CUDA y sampler/generator cuando sea posible.
- `best.pt`: pesos del mejor checkpoint validation.
- `experiment_config.json`, `metrics.jsonl`, `class_support.json`, `environment.json`, `manifest_hashes.json`, logs stdout/stderr y resumen final.
- SHA-256 de checkpoints y config; commit Git exacto; semilla; hardware; duración; memoria pico; batches/épocas realmente completados.
- Escritura atómica: guardar temporalmente y renombrar al terminar. Verificar que el archivo puede cargarse antes de continuar.
- Reanudación: restaurar modelo, optimizer, scheduler, scaler, época/global_step y RNG. No reanudar desde `best.pt` como si fuera `last.pt`.
- No subir checkpoints ni datasets al repositorio. Conservar reportes ligeros en Git y artefactos pesados en almacenamiento autorizado persistente.

## 9. Fase C — evaluación final y experimento confirmatorio

Tras completar el piloto y revisar sus logs, **no escalar automáticamente**. Primero aprobar una configuración congelada. Para un resultado académico confirmatorio:

1. Entrenar configuración congelada con tres seeds (2026, 2027, 2028), cada una con train y validation intactos.
2. Seleccionar checkpoint por validation de cada seed.
3. Evaluar test una sola vez por seed/configuración y reportar media ± desviación estándar, además de cada resultado individual.
4. Mantener métricas por dataset/tarea/clase; no promediar dominios o taxonomías sin una definición explícita.
5. Realizar benchmark de rendimiento en un job aparte y hardware identificado.
6. Si se cambia arquitectura, resolución, augmentations, pesos o scheduler después de mirar test, crear nueva versión de experimento y nuevo test no contaminado si existe.

La fase confirmatoria de tres seeds requiere estimación de cómputo/almacenamiento y autorización separada.

## 10. Puertas de aceptación y criterios de parada

No avanzar del piloto a confirmatorio salvo que:

- Todos los batches/losses/gradientes sean finitos y no existan NaN/Inf.
- La loss y las métricas se registren correctamente por época.
- Checkpoint last/best se puedan cargar y reanudar en una prueba.
- Validation no esté contaminado por train y los IDs sigan disjuntos.
- La cobertura de clases y las limitaciones A2D2 estén reflejadas en el informe.
- El consumo de memoria/tiempo quede dentro del presupuesto y no haya OOM.
- No exista una degradación sostenida inexplicada en validation.
- Se haya inspeccionado visualmente un conjunto fijo de predicciones de validation, sin usar test para ajustar.

Detener y conservar logs/checkpoint ante OOM, loss no finita, corrupción de datos, pérdida de persistencia, IDs fuera de rango, fuga entre splits o discrepancias de anotación. No reintentar aumentando batch/resolución ni cambiar hiperparámetros a ciegas.

## 11. Variables de control y estado actual

- `RUN_TRAINING=False` se mantiene.
- Este protocolo no implementa todavía un runner completo ni ejecuta entrenamiento.
- No se inicia ningún job GPU, no se crea infraestructura de pago y no se descarga dataset completo al aplicar este documento.
- Antes de activar el piloto hacen falta: revisar/implementar runner reproducible con checkpoints y evaluación, verificar métricas de Mask AP, completar preflight de hardware/almacenamiento y recibir autorización explícita del usuario para el piloto.
- PR #3 debe permanecer abierta, draft y sin fusionar hasta autorización expresa.

## 12. Registro de ejecución

No hay ejecuciones de este protocolo todavía. Añadir aquí una entrada por cada piloto/confirmatorio con: ID, commit, config hash, manifest hashes, seed, hardware, inicio/fin, epochs/steps, best epoch, métricas validation/test, checkpoint hashes, logs, incidencias y decisión de aceptación.


## 13. Implementación del ejecutor — 2026-11-23

Se implementaron estos componentes:

- `src/urban_experiment_runner.py`: loops semántico/instancias, mIoU/IoU/mean accuracy/pixel accuracy/soporte/matriz de confusión semántica, scheduler, early stopping, límite temporal por época, AMP opcional en CUDA, clipping, métricas JSONL, checkpoints last/best atómicos y restauración de optimizer/scheduler/scaler/RNG global y generadores DataLoader/sampler con hash de configuración; el loop registra también los componentes de loss de Mask R-CNN por época.
- `scripts/materialize_urban_experiment_data.py`: materializa en el runtime remoto únicamente train y validation A2D2/UrbanSyn desde manifests/índices completos. Verifica IDs únicos y concordancia; no accede a test.
- `scripts/urban_experiment_factory.py`: construye datasets, loaders train/validation, DeepLabV3+ o Mask R-CNN y optimizador para un dominio/tarea.
- `src/urban_coco_evaluator.py`: Box AP y Mask AP mediante `pycocotools.COCOeval`, con soporte/AP por clase. Se añadió prueba sintética `tests/test_urban_coco_evaluator.py`.
- `scripts/run_urban_experiment.py`: CLI con doble bloqueo (`run_training=true` y `--execute`), sin loader test.
- Guía: `docs/EJECUTOR_ENTRENAMIENTO_MULTIDOMINIO.md`; pruebas del motor en `tests/test_urban_experiment_runner.py`.

**Estado: implementación de código completa a nivel de componentes, pero aún NO validada integralmente ni autorizada para piloto.** No se han ejecutado tests nuevos, el materializador, la factory, COCOeval ni el motor sobre datos reales/GPU. Deben ejecutarse primero las pruebas sintéticas en Colab sobre el SHA exacto; luego un smoke de materialización/loaders train+validation sin optimización; después validar COCOeval y checkpoint/resume. La factory inicia ambos modelos con pesos aleatorios (sin pretraining), lo cual queda registrado y debe congelarse o modificarse antes de un piloto.

Pendientes obligatorios:
1. Suite de tests sobre el SHA exacto y corrección de fallos.
2. Prueba COCOeval sintética y validación con muestra real de validation.
3. Materialización remota train/validation, comprobación de almacenamiento, manifests/índices, IDs disjuntos y targets para los cuatro experimentos.
4. Smoke de checkpoint/resume y recursos persistentes GPU.
5. Fijar hiperparámetros y presupuesto antes de ejecutar.

No se inició entrenamiento, no se descargaron datasets, no se generaron checkpoints experimentales y no se cambió `RUN_TRAINING=False`. La autorización previa sigue limitada a los cuatro pasos SGD aislados ya completados; no autoriza el piloto. Mantener PR #3 abierta, draft y sin fusionar.


## Fase de capacidad previa a materialización amplia

Tras el smoke PASS de cuatro muestras reales, la siguiente puerta es `notebooks/colab_auditoria_capacidad_incremental.ipynb`. Estima hasta 50 muestras por dataset/split (train/val) sin descarga, estima exactamente 10 por split, exige espacio libre >= 2× la estimación del lote + 1 GiB, materializa 40 muestras y audita decodificación de todas las muestras con las cuatro rutas dataset/tarea. Límite absoluto 2 GiB. No consume activos test, no ejecuta inferencia ni entrenamiento.

El subconjunto de 10 por split se selecciona como prefijo determinista de muestras elegibles con instancias; no es estratificado por clase y no debe usarse como benchmark. La auditoría mide bytes locales, espacio libre, RSS pico y tiempo de decodificación. Si pasa, esos resultados permiten proponer el tamaño de la siguiente etapa; todavía no autorizan materialización completa ni piloto. La disponibilidad de GPU/VRAM se registra, pero una prueba CPU no sustituye un preflight GPU posterior.

