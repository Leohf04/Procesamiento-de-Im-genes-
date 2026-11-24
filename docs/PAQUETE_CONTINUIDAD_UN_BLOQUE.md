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
