# Ontología común y plan de balanceo

**Versión:** `urban-v1`  
**Estado:** índices remotos completos y auditados; planificador con selección train limitada por clase; validación estricta de sample_id en loaders. No habilita entrenamiento hasta validar CI y materialización local.

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

## Integración de pesos y sampler en loaders urban-v1 — 2026-11-22

Se añadió `src/urban_training.py` con `build_urban_train_loader`, una integración explícita de los helpers de `src/class_balancing.py`:

- **Semántica:** agrega `semantic_pixels` de filas train y devuelve pesos por clase para pasarlos a `torch.nn.CrossEntropyLoss(weight=...)`. El DataLoader mantiene muestreo uniforme de imágenes; el balanceo ocurre a nivel de píxel/clase.
- **Instancias:** construye un `WeightedRandomSampler` determinista con las frecuencias por imagen del índice train y usa `detection_collate_fn` para targets variables de Torchvision.
- Rechaza filas marcadas como validation/test, estados de anotación no `ok`, o longitudes distintas entre dataset e índice. No recibe estadísticas de evaluación.
- Se añadieron pruebas de integración sintéticas en `tests/test_urban_training_loader.py` para pesos semánticos, sampler/collate de instancias y rechazo de estadísticas de evaluación o índices desalineados.

**Límite de esta integración:** el helper requiere que el llamador entregue un dataset local ya materializado y filas de anotación del manifiesto train en el mismo orden. No descarga datos, no convierte referencias remotas en rutas locales y no inicia entrenamiento. Hasta auditar el artifact ampliado y probar la correspondencia exacta de IDs/rutas no debe conectarse a un entrenamiento real. A2D2 y UrbanSyn deben instanciarse como loaders separados.

Ejemplo de uso previsto (solo tras materializar y validar el split train):

```python
from src.urban_training import build_urban_train_loader

train_loader, class_weights = build_urban_train_loader(
    train_dataset,
    train_annotation_rows,
    task="semantic",
    class_to_id=semantic_name_to_id(),
    batch_size=4,
)
criterion = torch.nn.CrossEntropyLoss(weight=class_weights, ignore_index=255)
```

Para instancias, usar `task="instances"`; el loader aplica `WeightedRandomSampler` y devuelve `None` como pesos de pérdida. El cálculo de pesos y sampler sigue separado por dataset/dominio.


## Actualización de selección balanceada con límite por clase — 2026-11-22

Se reforzó el planificador para que el límite de clase tenga efecto real sobre el tamaño del conjunto train:

- `--per-class-cap` ahora tiene valor predeterminado 200; `0` desactiva explícitamente el límite.
- Una muestra se acepta solo si todas las clases presentes en ella permanecen por debajo del límite después de seleccionarla. El algoritmo termina si ninguna muestra restante cumple esa condición; por tanto puede devolver menos filas que `--max-samples-per-split`.
- El límite se aplica exclusivamente al split train. Validation y test se conservan completos y en el orden del manifiesto original.
- El resumen registra `per_class_cap` y `unselected_samples`; el informe conserva las coberturas disponibles/no cubiertas.
- El límite es una política experimental de control de dominancia por presencia de clase, no garantiza igualdad exacta de frecuencias ni balance de número de objetos/píxeles. Se debe comparar la distribución resultante antes de entrenar y ajustar el parámetro si elimina demasiada diversidad.

El workflow remoto acepta `per_class_cap` como input manual (default 200) y lo transmite al planificador.

## Validación de identidad de filas en loaders — 2026-11-22

`build_urban_train_loader` ahora exige que el dataset exponga `records` con `sample_id`. Compara la lista ordenada de IDs con la del índice de anotaciones y rechaza IDs vacíos, duplicados o diferencias de orden. La comprobación evita la asociación posicional incorrecta observada entre los manifiestos semántico y de instancias de train.

Se añadieron pruebas para:
- mismo conjunto de IDs con orden diferente;
- IDs duplicados;
- identidad y orden correctos para loaders semánticos y de instancias.

**Pendiente:** CI del nuevo HEAD, inspección del artifact generado con el límite 200 y prueba con una materialización pequeña de datos reales. No ejecutar entrenamiento hasta completar estas comprobaciones.


## Auditoría experimental cap 200 — 2026-11-23

Se recuperó el artifact `14770171764` del run `45038801547` (SHA-256 verificado). Se reconstruyeron los seis manifiestos completos a partir de los JSONL enriquecidos del plan previo sin cap, validando 5.534 filas totales, IDs únicos y coincidencia exacta de estadísticas por imagen. Se reprodujo la selección determinista con cap 200 y se auditó cobertura/retención.

**Resultado:** A2D2 semántica 206/1000 (20,6 %), A2D2 instancias 257/1000 (25,7 %), UrbanSyn semántica 200/1000 (20,0 %), UrbanSyn instancias 209/1000 (20,9 %). El límite se cumple y val/test permanecen completos. A2D2 mantiene ausencias de clases: 12 en semántica y 4 en instancias. UrbanSyn cubre las 19 clases semánticas y 8 de instancias.

**Dictamen:** cap 200 es demasiado agresivo para train principal; se conserva solo como ablación. La sensibilidad cap 500 retiene aproximadamente 50–56 % y cap 700 70–76 %. Recomendación: baseline con train completo y pesos/sampler ya implementados, sin mezclar dominios; evaluar cap 500/700 solo como ablación. No entrenar todavía. Detalles en [INFORME_AUDITORIA_BALANCEO_CAP200.md](INFORME_AUDITORIA_BALANCEO_CAP200.md).

Notebook reproducible que ejecuta el CLI real en Colab: [colab_generar_plan_cap200.ipynb](../blob/urban-models-and-benchmark/notebooks/colab_generar_plan_cap200.ipynb). La ejecución CLI en Colab queda como confirmación reproducible; la reproducción local de esta auditoría utilizó la misma función de selección del código actual. `RUN_TRAINING=False`.

## Integración multidataset con balanceo independiente — 2026-11-23

Se añadió `build_urban_train_loaders` a `src/urban_training.py` para preparar loaders por dominio en una sola llamada sin concatenar ni compartir estadísticas:

- Recibe un diccionario por dataset (`a2d2`, `urbansyn`), y cada entrada debe aportar su propio objeto Dataset, sus filas del índice de anotaciones y su propio `class_to_id`.
- Internamente invoca `build_urban_train_loader` por separado. En semántica, suma píxeles únicamente dentro del dominio y calcula sus propios pesos; en instancias, calcula frecuencias y `WeightedRandomSampler` únicamente dentro del dominio.
- Rechaza reutilizar el mismo objeto Dataset para dos dominios y detecta etiquetas de dataset ajenas cuando los manifiestos/filas las incluyen.
- Cada loader mantiene las validaciones existentes: longitud, IDs no vacíos/únicos, alineación exacta y orden de `sample_id`, `split=train` cuando el campo está presente y `annotation_status=ok`.
- Los índices actuales separan train/val/test por archivo, aunque una fila no tenga campo `split`; el llamador debe cargar exclusivamente el JSONL `{dataset}_train.annotations.jsonl` para construir el loader. No se deben concatenar índices de splits.
- `class_to_id` se suministra por entrada para permitir el mapeo específico del dominio/tarea. En la ontología común, usar `semantic_name_to_id` para semántica e `instance_name_to_id` para instancias; no usar el mapa de una tarea en la otra.

Ejemplo de interfaz (después de materializar y validar localmente cada manifiesto train):

```python
from src.urban_training import build_urban_train_loaders
from src.urban_ontology import load_urban_ontology, semantic_name_to_id

ontology = load_urban_ontology()
semantic_ids = semantic_name_to_id(ontology)
loaders = build_urban_train_loaders(
    {
        "a2d2": {
            "dataset": a2d2_train_dataset,
            "annotation_rows": a2d2_train_annotation_rows,
            "class_to_id": semantic_ids,
        },
        "urbansyn": {
            "dataset": urbansyn_train_dataset,
            "annotation_rows": urbansyn_train_annotation_rows,
            "class_to_id": semantic_ids,
        },
    },
    task="semantic",
    batch_size=4,
    seed=2026,
)
(a2d2_loader, a2d2_weights) = loaders["a2d2"]
(urbansyn_loader, urbansyn_weights) = loaders["urbansyn"]
```

Para instancias, usar `task="instances"` y `instance_name_to_id(ontology)` en cada entrada. Los pesos semánticos se conectan a la pérdida del modelo correspondiente; el sampler de instancias pertenece al loader de su dominio. No se debe combinar ambos loaders ni sus estadísticas salvo que se diseñe y documente un experimento explícito de dominio mixto.

Se añadieron pruebas sintéticas que comprueban pesos semánticos diferentes ante distribuciones opuestas, samplers de instancias calculados con frecuencias locales, rechazo de filas etiquetadas con otro dominio y rechazo de reutilizar el mismo Dataset. Estas pruebas están añadidas al repositorio, pero su ejecución CI queda pendiente de recuperar runners. No se materializaron datasets ni se entrenaron modelos.

