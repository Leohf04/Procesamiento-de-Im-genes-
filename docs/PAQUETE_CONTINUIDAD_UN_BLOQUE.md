# Paquete de continuidad — un solo bloque

**Actualizado:** 2026-11-24  
**Repositorio:** `Leohf04/Procesamiento-de-Im-genes-`  
**Rama:** `urban-models-and-benchmark`  
**HEAD de referencia previo a la auditoría segura:** posterior a los commits listados en el registro (consultar HEAD de la rama al continuar).  
**Registro principal:** [REGISTRO_DE_TRABAJO_Y_ESTADO.md](REGISTRO_DE_TRABAJO_Y_ESTADO.md)  
**Revisión técnica:** [REVISION_PREVIA_AL_PILOTO.md](REVISION_PREVIA_AL_PILOTO.md)  
**Protocolo propuesto:** [PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md](PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md)

## Para continuar en otra conversación

Copia y pega únicamente el bloque siguiente. El asistente debe abrir primero el registro principal y este documento desde GitHub antes de pedir datos o proponer cambios.

```text
Continuemos el proyecto Procesamiento de imágenes. Repositorio privado: Leohf04/Procesamiento-de-Im-genes-, rama urban-models-and-benchmark.

INSTRUCCIONES OBLIGATORIAS:
1) Lee primero docs/REGISTRO_DE_TRABAJO_Y_ESTADO.md y docs/PAQUETE_CONTINUIDAD_UN_BLOQUE.md desde el repositorio. No me pidas que repita información ya documentada.
2) Antes de cualquier cambio técnico, inspecciona el HEAD actual y los archivos afectados. Al terminar, actualiza el registro y este paquete, y crea un commit en la rama indicada.
3) No ejecutes entrenamiento, epochs, validación experimental, optimizer.step(), descargas de datasets ni jobs de CI. RUN_TRAINING=False. No toques assets de test.
4) No hagas merge. PR #3 debe seguir abierta y draft.
5) Separa siempre código implementado, pruebas sintéticas, preflight de un paso y entrenamiento real. No inventes resultados ni digas que ejecutaste Colab.
6) Si Google Drive no está conectado, dilo claramente y guarda el contexto en el repositorio; no afirmes que existe un documento Drive.

ESTADO:
- La ejecución informada por el usuario en Colab el 2026-11-24 completó PASS para cuatro actualizaciones aisladas: A2D2-semantic, UrbanSyn-semantic, A2D2-instances y UrbanSyn-instances. Exactamente un optimizer.step por caso, batch 1, 512x512, AMP off, pesos aleatorios; cero batches de validation, test intacto, sin checkpoints. Resumen de Colab en Drive: ProcesamientoImagenes/preflight_un_paso_real/single_step_preflight_summary.json; timestamp 2026-11-24T15:02:15.605634+00:00; HEAD reportado en ese resumen 571b15defa2362e2b8f141aeb21991de9b10c431.
- Esto es un preflight operativo de una actualización, NO entrenamiento piloto, NO evidencia de convergencia, generalización ni calidad.
- Datos de preflight: 10 muestras por dataset/split train/val materializadas; no usar esa muestra como dataset de entrenamiento. No se descargaron datasets mediante la notebook.
- Datasets de trabajo: A2D2 y UrbanSyn. SHIFT excluido por desalineación temporal RGB/semseg; Cityscapes no accesible para el usuario; no asumir que BDD100K sea la estrategia activa. Verifica la estrategia vigente en el protocolo y registro.
- Ontología: configs/urban_ontology_v1.json, urban-v1, 20 clases semánticas, ignore_index 255; UrbanSyn source ID 19 se mapea a ignore. Instancias: 8 clases más background. A2D2 instances son aproximación por componentes conectados, no IDs nativos.
- PR #3: abierta, draft, sin merge. No lanzar Actions mientras no haya señal de recuperación de runners.

HALLAZGOS TÉCNICOS YA IDENTIFICADOS; NO LOS DES POR RESUELTOS:
A) scripts/urban_experiment_factory.py construye DeepLabV3+ con pretrained_backbone=False y Mask R-CNN con weights=None, weights_backbone=None: inicialización aleatoria, no fine-tuning preentrenado.
B) La misma factoría crea optimizer SGD para ambas tareas. docs/PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md propone AdamW para semántica y SGD para instancias: discrepancia real entre protocolo y código.
C) La factoría crea ReduceLROnPlateau con patience=1; el protocolo propone patience=2 validaciones.
D) Los adaptadores/factoría redimensionan directamente a (512,512), deformando la relación de aspecto. Falta letterbox/preservación de aspecto y transformación coordinada de máscaras/cajas.
E) configs/config.yaml es configuración heredada Cityscapes/11 clases; no confundirla con el flujo multidataset activo urban-v1/20 clases.
F) El reporte de un paso no congela hashes de manifiestos/índices/ontología, config efectiva, versiones/procedencia de pesos y soporte por clase.
G) El preflight de 10 muestras no demuestra cobertura/representatividad. Antes del piloto hacen falta manifiestos completos, soporte por clase y validación visual de adaptadores.

PRÓXIMO TRABAJO SEGURO:
- Corregir la coherencia documental/código (sin entrenar): decidir y documentar optimizador/scheduler, política de pesos, resize con aspecto preservado y configuración efectiva.
- Añadir pruebas unitarias para transforms geométricas, cajas/máscaras y serialización de config/hashes.
- Auditar soporte de clases y muestras visuales usando solo train/val; mantener test sin abrir.
- Crear artefacto inmutable de configuración/entorno/hashes antes de cualquier experimento.
- Después solicitar autorización explícita para un piloto separado. No inferir autorización del permiso anterior de cuatro pasos.

PERSISTENCIA:
- ChatGPT no tiene disponible la integración Google Drive en este entorno (aparece deshabilitada por administración). El paquete y el registro de GitHub son la copia accesible; no hay que afirmar que se creó un Google Doc.
```

## Hallazgos de revisión estática (2026-11-24)

La revisión de los archivos de la rama encontró discrepancias que deben resolverse antes de un piloto:

1. **Inicialización:** `scripts/urban_experiment_factory.py` crea DeepLabV3+ con `pretrained_backbone=False` y Mask R-CNN con `weights=None, weights_backbone=None`. El paso único se ejecutó con pesos aleatorios; no fue fine-tuning.
2. **Optimizador:** la factoría usa SGD para ambas tareas, pero el protocolo propone AdamW para semántica y SGD para instancias.
3. **Scheduler:** la factoría configura `ReduceLROnPlateau(patience=1)`, mientras el protocolo propone paciencia 2.
4. **Geometría:** los adaptadores reciben `(size,size)` y hacen resize directo a 512×512. Debe implementarse preservación de aspecto/padding y transformación coordinada de máscaras y cajas antes de comparar resultados.
5. **Configuración heredada:** `configs/config.yaml` todavía declara Cityscapes y 11 clases; no gobierna el flujo multidataset `urban-v1` de 20 clases. Mantener explícita esta separación.
6. **Reproducibilidad:** el resumen de un paso no congela configuración completa, hashes de manifiestos/índices/ontología, soporte por clase ni procedencia/versiones de pesos.
7. **Cobertura:** las 10 muestras por split/dataset solo sirven para preflight; no prueban cobertura ni representatividad para entrenamiento.

No se modificó código de entrenamiento en esta intervención. No se ejecutó Colab, no se ejecutó optimizer.step(), no se descargaron datos, no se tocó test y no se inició piloto.


## Actualización técnica — 2026-11-24

La discrepancia de optimizador/scheduler y el resize directo fueron corregidos en código:
- Semántica: AdamW; instancias: SGD; ReduceLROnPlateau `mode=max, patience=2`.
- Transformaciones letterbox con padding semántico 255 e instancias 0, y cajas xyxy coherentes.
- Notebook de auditoría segura: `notebooks/colab_preflight_un_paso_real.ipynb`.
- Pruebas sintéticas automatizadas: `tests/test_urban_geometry_optimizer.py`.

**No se ha ejecutado la notebook ni entrenamiento.** La configuración efectiva congelada y procedencia de pesos siguen pendientes; las pruebas no demuestran calidad ni generalización.

Para continuar: abre la notebook desde Colab, ejecútala completa con los archivos de TRAIN/VAL ya presentes en Drive y pega solo el bloque entre `BLOQUE_CONTINUIDAD_INICIO` y `BLOQUE_CONTINUIDAD_FIN`.


### Enlace directo a la notebook actualizada

`notebooks/colab_preflight_un_paso_real.ipynb` (ahora contiene la auditoría segura de correcciones, no el antiguo preflight de cuatro optimizer steps):
https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/colab_preflight_un_paso_real.ipynb

La notebook diferencia el resultado de las pruebas mecánicas (`PASS`) de la preparación de experimentos (`BLOCKED_PENDING_CONFIG_AND_WEIGHT_PROVENANCE`). Aunque los hashes se recojan correctamente, no existe aún una configuración efectiva congelada ni una procedencia completa de pesos.


### Incidencia Colab: celda 1 y Git fetch — 2026-11-24

Se corrigió la celda inicial de la notebook para omitir el montaje repetido de Drive, validar la carpeta Git, generar correctamente el script GIT_ASKPASS, evitar sobrescribir carpetas no Git y mostrar stderr si la sincronización falla. Commit: `ff4706f8cbe1cbde7768425c18a0efa363932173`. El error original fue código 128, pero no incluía stderr; no se confirmó si el origen fue autenticación, carpeta local o conectividad.

Vuelve a ejecutar únicamente la celda 1 de la notebook actualizada. Si falla, conserva el diagnóstico completo de Git que ahora imprime la celda y compártelo sin credenciales. No iniciar entrenamiento.


### Incidencia resuelta preventivamente — 2026-11-24

La celda 1 de Colab se ejecutó correctamente: Drive ya estaba montado, repositorio sincronizado en `urban-models-and-benchmark`, HEAD `93d0c905ba7eef26c53292d586888d03382ec3d4`, `RUN_TRAINING=False`. Antes de avanzar se detectó y corrigió un error de sintaxis en la celda de auditoría (secuencias de salto de línea literales dentro del diccionario). Commit correctivo: `8e5e53cbf1f02bcb0edbfab6b040e1d521a7014c`. La notebook fue releída y su JSON validado, pero aún no se ejecutó en Colab tras el cambio. Para continuar: ejecutar solo la celda 1 para sincronizar este commit; después ejecutar la celda 2 y compartir su salida. Mantener el resto sin ejecutar hasta revisar el resultado. No hubo entrenamiento, descargas, lectura de test ni Actions.


### Resultado Colab — pruebas sintéticas PASS 9/9 (2026-11-24)

La celda de pruebas sintéticas reportó todas las comprobaciones en `true` y `PASS: 9 / 9`. El aviso Pillow `DeprecationWarning` por el parámetro `mode` de `Image.fromarray` no es un fallo y no invalida el PASS. Las pruebas no usan datos reales ni actualizan pesos. Siguiente paso: ejecutar solo la celda de auditoría de la sección 3 (hashes y soporte TRAIN/VAL), compartir su salida; dejar la celda final para después de revisar el reporte. Sin entrenamiento, descargas ni lectura de test.


### Auditoría segura de datos — 2026-11-24

Último resultado informado por el usuario desde Colab:
- Estado de `urban_corrections_audit.json`: `PASS`.
- Ocho archivos de datos calculados con hash; cero faltantes.
- Reporte guardado en `/content/drive/MyDrive/ProcesamientoImagenes/auditoria_correcciones_segura/urban_corrections_audit.json`.
- Pruebas sintéticas anteriores: PASS 9/9.

Esto confirma la auditoría de los ocho archivos esperados y la ausencia de faltantes detectados, pero no significa que la configuración efectiva ni la procedencia de pesos estén congeladas. Tampoco es evidencia de entrenamiento o calidad. No inferir hashes individuales, soporte por clase ni versiones a partir del resumen breve.

Siguiente paso: ejecutar únicamente la última celda de la notebook para imprimir el bloque único de continuidad y pegarlo aquí. No iniciar entrenamiento ni ejecutar otras celdas experimentales. Mantener `RUN_TRAINING=False), no tocar test, no descargar datos, no crear checkpoints y no fusionar PR #3 (debe seguir abierta y draft).


### Auditoría segura de datos — resultado Colab PASS (2026-11-24)

El usuario reportó que la celda de auditoría de la sección 3 guardó `urban_corrections_audit.json` en `ProcesamientoImagenes/auditoria_correcciones_segura/` en Drive, con `status=PASS`, ocho archivos de datos con hash y cero faltantes. Esto confirma presencia de los archivos esperados revisados por la celda; no demuestra validación visual, funcionamiento end-to-end de loaders, configuración experimental congelada ni procedencia de pesos. El estado de preparación sigue bloqueado por configuración y procedencia de pesos. No se entrenó, no se actualizó ningún peso, no se descargaron datos ni se tocó test; `RUN_TRAINING=False`. Siguiente paso: ejecutar solo la última celda para generar el bloque único de continuidad y compartirlo para revisión.


## Resultado consolidado de auditoría segura — 2026-11-24

El bloque final de Colab reportó `status=PASS`, los nueve checks sintéticos en true, `missing_expected_files=[]`, `optimizer_steps=0`, `RUN_TRAINING=false` y `test_split_touched=false`. HEAD de Colab: `5ac2e82581c88a0a4bbaecf48d43756dd8839ff8`. Los cuatro índices (A2D2/UrbanSyn × train/val) contienen 10 filas cada uno; no son conjuntos representativos ni aptos para entrenamiento. Los cuatro splits reportan cero anotaciones con estado distinto de OK. En la muestra A2D2 val solo aparecen car (54) y truck (45) como instancias; bicycle/person no aparecen en esos 10 registros, lo cual debe verificarse sobre manifiestos completos y no permite concluir que falten del dataset. UrbanSyn muestra las siete clases de instancia en train y val, sin que estos conteos pequeños permitan evaluar balance. El JSON está guardado en Drive en `ProcesamientoImagenes/auditoria_correcciones_segura/urban_corrections_audit.json`.

**Bloqueo explícito:** `experiment_readiness=BLOCKED_PENDING_CONFIG_AND_WEIGHT_PROVENANCE`, `effective_experiment_config_frozen=false`, `model_weight_provenance_frozen=false`. PASS no demuestra representatividad, calidad de anotación por inspección visual, loaders end-to-end, convergencia ni generalización. No iniciar entrenamiento.

Siguientes pasos seguros: congelar configuración efectiva y hash; documentar procedencia/licencia/identidad de pesos o declarar inicialización aleatoria; auditar soporte en manifiestos completos TRAIN/VAL e inspeccionar muestras solo de TRAIN/VAL. Después preparar un piloto separado y solicitar autorización expresa. Test permanece intacto y PR #3 abierta/draft/sin merge.


## Notebook único para cerrar los tres pendientes — 2026-11-24

Se añadieron estos archivos en `urban-models-and-benchmark`:
- `configs/urban_experiment_v1.json`: configuración efectiva versionada para los cuatro experimentos Urban-v1, derivada del protocolo.
- `notebooks/urban_v1_cierre_tres_pendientes.ipynb`: auditoría integral segura, inspección visual TRAIN/VAL y salida final única.

**Decisiones:** inicialización aleatoria, sin pesos preentrenados/checkpoint; seed 2026; resolución 512; semántica batch 4/AdamW LR 1e-4; instancias batch 1/acumulación 2/SGD LR 2.5e-3; 20 épocas máximas; scheduler mode=max/factor 0.5/patience 2; early stopping 5; clipping 1.0. Valores tomados del protocolo, no autorización de entrenamiento.

La notebook verifica los conteos completos esperados (A2D2 1000/1000; UrbanSyn 1000/751), IDs/orden, estados, assets, fuga TRAIN/VAL y soporte de clases; crea hoja visual de hasta 3 muestras por split. No accede a test. `RUN_TRAINING=False` y no realiza descargas, optimizer steps, backward, epochs ni checkpoints. El batch semántico 4 y acumulación 2 de instancias requieren un piloto separado autorizado; la prueba T4 previa fue batch 1.

**No se ha ejecutado Colab desde ChatGPT.** El usuario debe ejecutar el Notebook completo, revisar la hoja visual y pegar solo el bloque final delimitado.

Notebook: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_cierre_tres_pendientes.ipynb


### Alineación de scheduler y acumulación

Antes de congelar los valores del protocolo, se corrigió una discrepancia de implementación: `src/urban_optimizer.py` consume ahora `scheduler_factor=0.5` y `scheduler_patience=2`; `src/urban_experiment_runner.py` implementa `gradient_accumulation_steps` y maneja grupos parciales. La configuración versionada usa los nombres consumidos por factoría/runner. Se añadieron pruebas sintéticas para acumulación y factor del scheduler. La notebook comprueba la presencia de esas implementaciones y hashea los archivos de código.

Las pruebas no se han ejecutado por ChatGPT; no afirmar pytest PASS. La ejecución de Colab sigue pendiente. `RUN_TRAINING=False`, sin test ni descargas; cualquier piloto requiere autorización expresa.


### Validación estática final de artefactos — 2026-11-24

Se corrigió la celda de configuración de la notebook para verificar explícitamente que las cuatro configuraciones contienen los campos consumidos por factoría/runner, inyectar rutas runtime de Drive y comprobar acumulación de gradientes y factor del scheduler. El bloque final recoge hashes SHA-256 de factoría, runner y optimizador. Se validó que el archivo es JSON nbformat 4 con 13 celdas y que la última celda contiene los delimitadores de continuidad. La configuración JSON también se parseó y contiene cuatro especificaciones completas.

Esto es validación estática del contenido del repositorio, no ejecución de Python/pytest/Colab. No se ha confirmado ejecución de tests ni de la notebook.


La última revisión de la notebook endureció la auditoría: ahora un orden distinto entre IDs de manifiesto e índice se marca como error, y se exigen las claves de assets que consumen los adaptadores actuales (A2D2: `image`, `semantic`, `instance`; UrbanSyn: `rgb`, `semantic`, `panoptic`). También verifica que existan los archivos referenciados. La inspección final permanece limitada a TRAIN/VAL.


## 2026-11-24 — Corrección de SyntaxError en auditoría de Notebook Urban-v1

El usuario reportó que la celda de auditoría falló en Colab con `SyntaxError: unexpected character after line continuation character`. La causa fue que se guardaron secuencias literales `\\n` en medio de instrucciones Python, en lugar de saltos de línea reales. Se reemplazó íntegramente el código de la celda de auditoría en `notebooks/urban_v1_cierre_tres_pendientes.ipynb`.

La versión corregida declara explícitamente `expected_rows` (A2D2 1000/1000; UrbanSyn 1000/751), compara IDs y orden, agrega soporte semántico/instancias, exige campos de anotación y verifica assets, y detecta solapamiento TRAIN/VAL. Continúa sin tocar `test`, sin descargas y sin entrenamiento.

Validación realizada: JSON nbformat 4 parseado, 13 celdas presentes, cero secuencias literales `\\n` en la celda corregida, y compilación sintáctica Python de la celda corregida con resultado `Syntax OK`. No se ejecutó la auditoría sobre los datos ni se ejecutó Colab.

Commit de corrección del Notebook: `eec3d748482b8846f1a9791c496212139ff57580`.

Para continuar, el usuario debe volver a abrir/recargar el Notebook desde el enlace GitHub-Colab para cargar esta versión corregida; la copia que ya estaba abierta en Colab no se actualiza automáticamente. Después puede ejecutar el Notebook desde el principio. El bloque único final sigue siendo la última celda.


## Incidencia de auditoría Urban-v1 — rutas históricas y cobertura incompleta (2026-11-24)

Último bloque del usuario: `status=INCOMPLETE`; cuatro splits con 10 manifiesto/índice filas cada uno; protocolo exige A2D2 1000 train/1000 val y UrbanSyn 1000 train/751 val. IDs únicos, conjuntos y orden coinciden; estados de anotación OK; sin solapamiento train/val. Assets fueron marcados ausentes con rutas históricas `/content/urban_data_capacity/...`, mientras la ubicación persistente configurada es `/content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity/`. El resultado anterior no distingue entre ruta mal resuelta y archivo no materializado.

**Corrección en HEAD:** notebook `notebooks/urban_v1_cierre_tres_pendientes.ipynb`, commit `81cbd6486f6f302106ee71a245a877d054ec6b1d`. El resolvedor ahora comprueba ruta original y su equivalente en Drive, informa método/candidatos, separa remapeo exitoso de archivo no localizado y alimenta la hoja visual. El bloque de continuidad incluye `asset_resolution_summary` y `manifest_source_diagnostics`.

Esta corrección no descarga datos ni inventa/expande manifiestos. Los 10 registros siguen siendo solo muestras de preflight; no son aptos como dataset completo. Deben prepararse manifiestos e índices completos TRAIN/VAL de acuerdo con el protocolo. `RUN_TRAINING=False`; no backward, optimizer steps, epochs, checkpoints, descargas ni acceso a test. PR #3 permanece abierta, draft y sin merge.

**Acción Colab:** recargar la notebook desde el enlace GitHub-Colab, ejecutar desde el principio y pegar un único bloque de continuidad. El nuevo bloque determinará si las rutas antiguas se resuelven en Drive o si faltan realmente los assets. No iniciar entrenamiento.


## Continuidad actual — auditoría Urban-v1 con remapeo de assets (2026-11-24)

Último resultado de Colab:
- Config/ontología hashes: `faa68c39f042c1aa8313123501fa25c280212d9f261236eb99fb4d6fd01f7e7f` / `a65a3c6735c146b59fc361e29e595adc2f6b00d3e3d10d10923feaf56786ab64`.
- Cuatro configuraciones completas declaradas; inicialización aleatoria; sin checkpoint; `RUN_TRAINING=False`.
- Assets de las 40 muestras: 120 campos encontrados tras remapeo, 100 archivos físicos únicos, cero ausentes. Hoja visual creada; 12 imágenes inspeccionadas por la notebook; falta revisión humana.
- Manifiestos/índices configurados: 10 filas en cada uno de los cuatro splits, no cumplen el protocolo (A2D2 1000/1000; UrbanSyn 1000/751). IDs alineados/únicos, annotation status OK, sin campos obligatorios ausentes ni solapamiento train/val en la muestra.
- No backward, no entrenamiento, no checkpoint y no acceso a test.

La causa de los 10 registros está localizada en el flujo de capacidad: `notebooks/colab_auditoria_capacidad_incremental.ipynb` sección 4 reconstruye manifiestos completos desde el artifact GitHub Actions `14770171764` (run `45038801547`, plan `per_class_cap=null`) en `/content/cap200_input/manifests` y extrae los índices completos; sección 8 selecciona deliberadamente solo 10 filas por split y persiste ese subconjunto en Drive. El bloque de cierre está auditando ese subconjunto, no necesariamente el universo de metadatos disponible. La disponibilidad actual del artifact no se ha verificado y puede expirar.

**Próxima intervención:** verificar/recuperar artifact completo; reconstruir y persistir en un directorio separado solo manifiestos e índices TRAIN/VAL completos; verificar conteos, IDs y hashes; hacer dry-run de materialización completa (sin límite de filas, sin descargar) para estimar tamaño. Mantener intacta la carpeta de las 40 muestras. No leer/materializar test, no descargar el dataset completo ni iniciar entrenamiento sin revisión y autorización.

Enlace notebook de cierre: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_cierre_tres_pendientes.ipynb


## Próxima ejecución — recuperar manifiestos completos y estimar almacenamiento (2026-11-24)

Artifact comprobado en GitHub: ID `14770171764`, run `45038801547`, disponible al 24-nov-2026 (`expired=false`), expira 22-dic-2026, digest SHA-256 `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`.

Notebook creada: `notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb`. Enlace: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb

En Colab montará Drive y sincronizará la rama; recuperará/verificará el ZIP por run, expiración y SHA-256; leerá exclusivamente miembros TRAIN/VAL de manifiestos semánticos/instancias e índices, sin extraer ni leer TEST; validará conteos A2D2 1000/1000 y UrbanSyn 1000/751, IDs/estadísticas/anotaciones/assets y no solapamiento train/val; guardará manifiestos e índices completos en `MyDrive/ProcesamientoImagenes/urban_v1_full_metadata_20261124`, carpeta separada de las 40 muestras existentes; ejecutará dry-run sin cap ni filtro de instancias para estimar los 3.751 registros, mediante consultas de metadatos/HEAD y sin descargar RGB/máscaras; y guardará hashes/reportes y producirá un bloque único.

La notebook se guardó en commits `6e0e350c9ceacf4c8b2b57fdfb6f4874e23f1575` y `f1bb84121a7cc47056db84e17387407b6c99e70c`. JSON nbformat 4 y 13 celdas verificados tras releer desde GitHub; no se ejecutó Python/Colab ni el dry-run desde ChatGPT.

Importante: `--dry-run` solo estima bytes consultando metadatos remotos; no descarga archivos. No ejecutar una materialización real todavía. No tocar TEST, no entrenar, no escribir checkpoints, no lanzar Actions. Si el artifact expira, detenerse. PR #3 permanece abierta, draft y sin merge.


## Error de celda 4 y corrección idempotente (2026-11-24)

El directorio `urban_v1_full_metadata_20261124` ya existía en Drive, por lo que la celda 4 original se detenía para proteger los datos. No sabemos desde ChatGPT si esa carpeta contiene una ejecución completa o parcial.

La celda fue corregida en commit `ff70758c679bd7c1785d316c72f5f47b85f39b14`: ahora compara contenido/orden de los cuatro manifiestos y cuatro índices esperados. Si todos coinciden exactamente, reutiliza la carpeta. Si falta alguno o el contenido difiere, conserva íntegramente la carpeta existente y crea otra con sufijo UTC. Comprueba los ocho archivos tras la operación y registra si reutilizó los metadatos. No borra ni sobrescribe datos existentes.

Recarga la notebook desde GitHub-Colab y vuelve a ejecutar desde la celda 4 (si reiniciaste el runtime, ejecuta desde el principio). Enlace: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb

No ejecutar materialización real ni entrenamiento; no tocar TEST. El dry-run permanece sin descargas. PR #3 abierta, draft y sin merge.


Ajuste final de la misma corrección: commit `ed656be7baa77f646716eed50dae98c2f3d7e327` deja explícita la escritura del reporte con `chr(10)` para evitar ambigüedades de escapes en la celda. La versión final fue releída desde GitHub; la celda registra `reused_existing_metadata` y valida los ocho JSONL antes de continuar.
