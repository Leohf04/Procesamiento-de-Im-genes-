# Revisión previa al piloto — 2026-11-24

**Estado:** revisión estática inicial completada; piloto NO autorizado ni iniciado.  
**Rama:** `urban-models-and-benchmark`  
**Evidencia de ejecución disponible:** preflight de cuatro pasos reales informado por Colab el 2026-11-24. Esta revisión no vuelve a ejecutar entrenamiento.

## 1. Alcance revisado

Se inspeccionaron el notebook `colab_preflight_un_paso_real.ipynb`, el script `urban_single_step_preflight.py`, la factoría `urban_experiment_factory.py`, adaptadores de datos, ontología `urban-v1`, loader/balanceo, runner, evaluador COCO y protocolos experimentales multidominio.

## 2. Hallazgos que bloquean un piloto reproducible

### H1. La prueba de un paso usa pesos aleatorios

La factoría construye DeepLabV3+ con `pretrained_backbone=False` y Mask R-CNN con `weights=None, weights_backbone=None`. Por tanto, los cuatro resultados del preflight corresponden a inicialización aleatoria. Es válido para comprobar forward/backward/optimizer, pero no constituye fine-tuning ni establece una línea base comparable con un modelo preentrenado.

**Acción requerida:** decidir por arquitectura si se usarán pesos preentrenados compatibles (registrar origen, versión y licencia) o inicialización aleatoria; congelar esa decisión en la configuración del experimento. No cambiarla después de empezar sin crear otro ID de experimento.

### H2. La muestra materializada es demasiado pequeña para un piloto

El preflight actual usa 10 muestras por split y dataset y solicita solo el primer batch de TRAIN para cada combinación. Esto demuestra compatibilidad de una muestra, no cobertura de clases, estabilidad de batches, entrenamiento representativo ni validez de métricas. A2D2 tiene ausencias de clases documentadas en auditorías anteriores.

**Acción requerida:** generar manifiestos completos/representativos, informe actualizado de soporte por clase y split, verificar IDs disjuntos y cobertura. Definir un subconjunto de piloto explícito solo si el conjunto completo no cabe; registrar criterio, seed y limitaciones. No interpretar las 10 muestras de preflight como dataset de entrenamiento.

### H3. El resize a 512×512 deforma la relación de aspecto

Los adaptadores redimensionan directamente imagen y máscara a `(512,512)`. A2D2 y UrbanSyn tienen relaciones de aspecto originales distintas de 1:1. La deformación puede alterar geometría de vehículos, peatones y objetos, además de cajas derivadas de máscaras.

**Acción requerida:** comparar y elegir resize con preservación de aspecto + padding (letterbox) o una resolución rectangular común; transformar imagen, máscara y cajas de forma coordinada. Registrar el método como parte de la configuración y repetir smoke/preflight después del cambio. No reutilizar resultados de 512×512 como si fueran equivalentes.

### H4. Instancias A2D2 son aproximaciones por componentes conectados

El adaptador convierte colores/subclases como `Car 1–4` en componentes conectados, con área mínima de 8 píxeles tras el resize. No son IDs de instancia nativos; objetos fragmentados pueden convertirse en varias instancias y componentes pequeños se descartan.

**Acción requerida:** auditar visualmente un conjunto fijo de máscaras reconstruidas, medir fragmentación y objetos descartados, validar el umbral y etiquetar INS-A2D2 como exploratorio. No combinar sus métricas con UrbanSyn como si el ground truth tuviera la misma semántica.

### H5. La ontología tiene soporte desigual por dominio

La ontología `urban-v1` define 20 IDs semánticos. UrbanSyn mapea su ID fuente 19 a `ignore_index=255`, por lo que lane marking no se aprende allí; A2D2 sí puede mapear líneas/crosswalk a la clase 19. Las clases no presentes en un dominio deben quedar como no soportadas, no como resultados cero ni como negativos implícitos.

**Acción requerida:** emitir soporte por clase calculado desde máscaras reales de TRAIN y VALIDATION; comprobar que coincide con el índice de anotaciones; excluir del mIoU únicamente clases sin soporte GT según el protocolo, y publicar la lista exacta de clases evaluables por dominio. No promediar dominios/tareas.

### H6. El reporte del paso único no congela toda la configuración

El JSON actual registra hardware, pérdida, gradientes, resolución, batch y algunos límites, pero no incluye todos los detalles necesarios para reproducir un experimento (hashes de manifiestos/índice/ontología, parámetros completos, lista de clases habilitadas, versión de código/configuración y procedencia de pesos).

**Acción requerida:** antes del piloto generar `experiment_config.json` inmutable, `environment.json`, hashes SHA-256 de manifests/índices/ontología, soporte por clase, seed, transformaciones, optimizer/scheduler/AMP y origen de pesos. Los reportes automáticos añadidos al notebook conservan la evidencia del preflight, no sustituyen esos artefactos experimentales.

## 3. Aspectos positivos observados

- La factoría valida que los IDs de manifiesto y anotaciones coincidan, no se repitan y no se solapen entre train/validation.
- El loader de entrenamiento usa estadísticas de TRAIN; las estadísticas de clases no se calculan mezclando dominios.
- El script de un paso solicita un único batch de TRAIN; no itera validation ni abre test.
- El runner experimental implementa guardado atómico, checkpoint last/best, estado del optimizador/scheduler/RNG y reanudación; requiere validación end-to-end antes de confiar en él.
- El evaluador de instancias usa `pycocotools.COCOeval` para Box AP y Mask AP. Falta completar una prueba end-to-end representativa en GPU y verificar clases/soporte/casos sin instancias.
- La ejecución de cuatro pasos reportada terminó PASS, con parámetros modificados, cero batches de validation, test intacto y sin checkpoints.

## 4. Orden recomendado de trabajo

1. Corregir/preparar transformaciones geométricas con aspecto preservado y pruebas para máscaras/cajas.
2. Auditar visualmente los adaptadores A2D2/UrbanSyn y el soporte real por clase en manifiestos completos.
3. Congelar política de inicialización/preentrenamiento y configuración por cada ID dataset/tarea.
4. Ejecutar smoke test sin optimización sobre muestras train/validation representativas y COCOeval; revisar checkpoint round-trip.
5. Hacer prueba de memoria/tiempo con el tamaño de imagen y batch que se propone para el piloto.
6. Congelar `experiment_config.json`, hashes y presupuesto; revisar artefactos persistentes y política de reanudación.
7. Solicitar autorización explícita para el piloto. Mantener `RUN_TRAINING=False` hasta entonces.

## 5. Decisiones de seguridad

- No se inicia entrenamiento piloto ni se ejecutan nuevos optimizer steps como parte de esta revisión.
- No se toca el split test.
- No se suben datasets, máscaras, imágenes ni checkpoints al repositorio.
- PR #3 permanece abierta y en draft.
- La conexión de Google Drive de ChatGPT aparece deshabilitada por la administración; el notebook mantendrá los reportes en Drive y ofrecerá una copia ligera en este repositorio privado para lectura automatizada futura.
