# Ontología común y plan de balanceo

**Versión:** `urban-v1`  
**Estado:** definición de taxonomía y planificador implementados; índices de anotaciones por muestra todavía pendientes. No habilita entrenamiento.

## Roles de las fuentes

| Tarea | Fuente | Uso |
|---|---|---|
| Semántica | A2D2 | Dominio real, especialmente carriles/marcas viales y clases urbanas disponibles |
| Semántica | UrbanSyn | Dominio sintético; mantener métricas y manifiestos separados |
| Instancias | UrbanSyn | Fuente principal de máscaras panoptic y cajas 2D |
| Instancias | A2D2 | Ablation/complemento real; no usar como detector equilibrado de todas las clases |

Los manifiestos por dataset permanecen separados. La combinación se realiza a nivel de protocolo/experimentos y no mediante concatenación ciega de imágenes de dominios distintos.

## Ontología

La definición fuente de verdad está en `configs/urban_ontology_v1.json` y se carga con `src/urban_ontology.py`.

- Cabeza semántica: IDs 0–18 conservan los 19 trainId de UrbanSyn; ID 19 se reserva para lane marking; ignore = 255.
- UrbanSyn `unlabeled` (trainId 19) se convierte a ignore 255.
- A2D2 se mapea por nombre normalizado, nunca por su color/ID de origen. Clases no contempladas quedan en ignore.
- Cabeza de instancias: IDs 1–8 = person, rider, car, truck, bus, train, motorcycle, bicycle; 0 es background.
- `rider` y `bicycle` son clases distintas. Lane marking solo pertenece a semántica, no a instancias.
- IDs de instancia son locales a cada imagen. En A2D2 se reconstruyen componentes conectados de subclases; no son IDs nativos globales y pueden fragmentar objetos.

## Formato del índice de anotaciones necesario para balancear

Para cada manifiesto `{dataset}_{split}.jsonl` se requiere un archivo gemelo `{dataset}_{split}.annotations.jsonl`, con una fila por `sample_id`:

```json
{"sample_id":"sequence/frame.png","annotation_status":"ok","semantic_pixels":{"road":120000,"car":9000},"instance_counts":{"car":3,"person":1}}
```

- `semantic_pixels`: píxeles por nombre canónico, excluyendo ignore.
- `instance_counts`: número de máscaras/objetos por nombre canónico.
- Las clases ausentes se omiten o tienen valor cero.
- No guardar imágenes, máscaras ni derivados en el repositorio.
- Un índice incompleto, duplicado o con filas de estado distinto de `ok` hace fallar el planificador; no se sustituye por ceros.

El informe ampliado disponible actualmente solo aporta estadísticas agregadas de 50 muestras por split, no un índice de cada imagen. Por eso no sería correcto inventar una selección balanceada usando esos totales.

## Selección reproducible

`scripts/build_balanced_training_plan.py`:

1. Lee los manifiestos de referencia remota existentes y el índice per-image.
2. No modifica la asignación train/val/test ni mueve secuencias entre splits.
3. Aplica selección greedy multilabel determinista por semántica (píxeles) e instancias (objetos), dando prioridad a clases con menor frecuencia de muestras y a déficits aún no cubiertos.
4. Informa cobertura disponible/seleccionada, conteos, clases no cubiertas y semilla.
5. Escribe archivos independientes por dataset/tarea/split; no mezcla A2D2 y UrbanSyn.

Ejemplo (solo cuando existan los seis índices per-image):

```bash
python scripts/build_balanced_training_plan.py \
  --manifests-dir data/manifests \
  --annotation-index-dir data/annotation_index \
  --output-dir artifacts/balanced \
  --seed 2026 --max-samples-per-split 1000
```

El algoritmo es un selector reproducible de cobertura multilabel, no un balanceador perfecto ni un sustituto de pesos de pérdida/sampler durante entrenamiento. Validación y test se conservan como particiones completas en el flujo de evaluación; el límite solo debe usarse en experimentos de desarrollo, no para reportar métricas oficiales.

## Bloqueos antes de ejecutar el plan sobre datos reales

1. Generar los índices por imagen para train/val/test decodificando las anotaciones remotas.
2. Confirmar conteos y mapeos clase por clase en ambos datasets.
3. Resolver licencia de UrbanSyn: se mantiene el criterio operativo CC BY-NC-SA 4.0, con atribución y sin redistribución de datos/derivados.
4. A2D2 tiene una muestra de auditoría sesgada: car 137/150, truck 93/150, bicycle 28/150, person 25/150; no aparecieron bus/motorcycle/rider. El planificador debe informar esas ausencias, no fabricar cobertura.
5. Repetir auditoría sobre los índices completos y comprobar no solapamiento entre splits.

`RUN_TRAINING=False` permanece obligatorio hasta cerrar estas puertas.


## Indexador remoto per-image añadido — 2026-11-22

Se implementó `scripts/index_remote_annotations.py` y el workflow `.github/workflows/index-remote-annotations.yml`. El indexador obtiene únicamente anotaciones, no imágenes RGB: A2D2 máscaras semánticas RGB desde S3 anónimo; UrbanSyn semseg y panoptic desde la revisión inmutable del manifiesto. Produce las seis filas-por-muestra JSONL que exige el planificador, con píxeles por clase semántica y conteos de instancias por clase. Los errores de origen, dimensión o decodificación detienen el proceso.

El workflow ejecuta por defecto una prueba acotada de 100 muestras por split/dataset (300 por dataset) y genera manifiestos reproducibles, índices y plan balanceado como artifact. Puede ejecutarse manualmente con un máximo mayor (hasta los 1.000 por split del manifiesto configurado). El artifact contiene solo estadísticas y referencias; no imágenes ni máscaras.

**Estado de la prueba al 2026-11-22:** los manifiestos de prueba ya se generaron correctamente; el indexado per-image del run 45002662737 seguía en ejecución al último registro. No declarar el balanceo real finalizado hasta inspeccionar los seis JSONL, los resúmenes de cobertura y el informe balanced_training_plan.json.


## Política inicial de pesos y muestreo — 2026-11-22

Se añade `src/class_balancing.py` como utilidad independiente y testeada:
- Semántica: pesos de CrossEntropyLoss con frecuencia de píxeles de train, inversa de raíz cuadrada, media uno; clases ausentes reciben peso cero y deben declararse como no entrenables en ese split.
- Instancias: `WeightedRandomSampler` con peso por imagen calculado como promedio de rareza de las clases presentes, no por cantidad de objetos. Se fija semilla y se usa solo el índice train.
- No calcular pesos con validation/test, no alterar sus distribuciones y no combinar conteos de A2D2 y UrbanSyn.
- Estos helpers aún no están conectados a los scripts de entrenamiento antiguos, que operan sobre Cityscapes/BDD100K y tienen datasets distintos. Su integración con los loaders UrbanSyn/A2D2 se hará después de inspeccionar el índice ampliado y validar las rutas locales de imágenes/anotaciones.
- Los pesos no resuelven clases ausentes: para esas clases hace falta otra fuente o redefinir explícitamente el alcance de la tarea.
