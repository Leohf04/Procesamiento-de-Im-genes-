# Paquete de continuidad — un solo bloque

**Actualizado:** 2026-11-24  
**Repositorio:** `Leohf04/Procesamiento-de-Im-genes-`  
**Rama:** `urban-models-and-benchmark`  
**HEAD de referencia antes de este documento:** `6117ef4703f56184c6ec9dbbeef37264631a0107`  
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
