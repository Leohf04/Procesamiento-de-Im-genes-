# Auditoría del plan de balanceo cap 200

**Fecha:** 2026-11-23  
**Ontología:** `urban-v1`  
**Semilla:** 2026  
**Artifact fuente:** GitHub Actions run `45038801547`, artifact `14770171764`  
**SHA-256 del ZIP:** `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`

## Resultado ejecutivo

El artifact existente se recuperó y verificó. Se reconstruyeron los seis manifiestos de referencia y se reprodujo la selección determinista del planificador con `per_class_cap=200`. La auditoría **no aprueba cap 200 como configuración de entrenamiento**: conserva solo entre el 20,0 % y el 25,7 % del train, descartando entre el 74,3 % y el 80,0 % de las muestras. Se conserva como experimento de comparación.

No se volvieron a indexar máscaras, no se descargaron RGB ni máscaras, no se entrenó ningún modelo.

## Reconstrucción y validación del artifact

El ZIP original contiene seis índices por imagen y seis pares de manifiestos de tarea (semántica/instancias), además del plan previo. El plan previo tenía `per_class_cap=null`, por lo que sus JSONL enriquecidos conservan el universo completo de cada split. Se usaron los JSONL semánticos como base de manifiesto, se retiraron los campos estadísticos y se reconstruyó el orden original de `prepare_reproducible_subsets.py` con SHA-256 de `2026:sample_id`.

Se validó para los seis splits:

| Dataset | Split | Filas manifiesto | Filas índice | IDs únicos | Estadísticas |
|---|---:|---:|---:|---:|---|
| A2D2 | train | 1.000 | 1.000 | 1.000 | Coinciden |
| A2D2 | val | 1.000 | 1.000 | 1.000 | Coinciden |
| A2D2 | test | 1.000 | 1.000 | 1.000 | Coinciden |
| UrbanSyn | train | 1.000 | 1.000 | 1.000 | Coinciden |
| UrbanSyn | val | 751 | 751 | 751 | Coinciden |
| UrbanSyn | test | 783 | 783 | 783 | Coinciden |

Además, las variantes semántica e instancias tienen los mismos conjuntos de `sample_id`, los mismos metadatos fuente por ID y los mismos conteos por imagen que los índices. No se detectaron IDs duplicados o discrepancias.

## Resultado cap 200

El límite cuenta **muestras que contienen cada clase**, no objetos ni píxeles. Solo afecta a train; val/test permanecen completos.

| Dataset | Tarea | Train disponible | Seleccionado | Excluido | Retención |
|---|---|---:|---:|---:|---:|
| A2D2 | Semántica | 1.000 | 206 | 794 | 20,6 % |
| A2D2 | Instancias | 1.000 | 257 | 743 | 25,7 % |
| UrbanSyn | Semántica | 1.000 | 200 | 800 | 20,0 % |
| UrbanSyn | Instancias | 1.000 | 209 | 791 | 20,9 % |

El cap se cumple: ninguna clase supera 200 muestras seleccionadas.

### Cobertura seleccionada por clase

**A2D2 — semántica (206 imágenes):** bicycle 194, car 195, lane marking 177, person 175, sidewalk 198, sky 200, traffic sign 195, truck 129.  
No disponibles en el índice train: building, bus, fence, motorcycle, pole, rider, road, terrain, traffic light, train, vegetation y wall (12 clases). No se deben interpretar como clases presentes sin cobertura ni inventar ejemplos.

**A2D2 — instancias (257 imágenes):** bicycle 189, car 200, person 180, truck 160.  
No disponibles: bus, motorcycle, rider y train. La reconstrucción A2D2 por componentes conectados sigue siendo aproximada, no IDs nativos globales.

**UrbanSyn — semántica (200 imágenes):** 19/19 clases de la ontología presentes y cubiertas.  
Conteos de presencia: bicycle 129, building 200, bus 129, car 195, fence 137, motorcycle 128, person 200, pole 200, rider 169, road 200, sidewalk 200, sky 199, terrain 179, traffic light 186, traffic sign 200, train 99, truck 109, vegetation 199, wall 130.

**UrbanSyn — instancias (209 imágenes):** 8/8 clases presentes y cubiertas.  
Conteos: bicycle 112, bus 125, car 198, motorcycle 107, person 200, rider 135, train 57, truck 113.

A2D2 semántica conserva 15 de 18 grupos/secuencias de train; A2D2 instancias conserva 17 de 18. UrbanSyn se agrupó por sample ID, no por secuencia temporal verificada.

## Sensibilidad al valor del cap

Se reprodujo el mismo selector determinista para valores alternativos. Porcentaje del train retenido:

| Cap | A2D2 semántica | A2D2 instancias | UrbanSyn semántica | UrbanSyn instancias |
|---:|---:|---:|---:|---:|
| 200 | 20,6 % | 25,7 % | 20,0 % | 20,9 % |
| 300 | 30,6 % | 35,7 % | 30,0 % | 30,9 % |
| 400 | 40,6 % | 45,7 % | 40,0 % | 40,9 % |
| 500 | 50,6 % | 55,7 % | 50,0 % | 50,9 % |
| 700 | 70,6 % | 75,7 % | 70,0 % | 70,9 % |
| 1.000 | 100,0 % | 93,9 % | 100,0 % | 99,4 % |

Las diferencias con 100 % en instancias cap 1.000 se deben a muestras sin ninguna instancia canónica, que no son candidatas al selector cuando el cap está activo.

## Dictamen y recomendación

**No usar cap 200 como train principal.** La reducción es demasiado agresiva y sacrifica demasiada variedad. El cap de presencia tampoco equilibra la cantidad de píxeles ni de objetos, y A2D2 mantiene ausencias estructurales de clases.

Recomendación metodológica:
1. Mantener un baseline con el train completo (sin cap), sin mezclar dominios.
2. Usar los pesos semánticos y el sampler de instancias ya implementados, calculados exclusivamente con train y por dataset.
3. Si se requiere una ablación de downsampling, comparar cap 500 o 700 contra el baseline y reportar retención/cobertura; no elegirlos automáticamente como configuración final.
4. Mantener A2D2 como dominio real complementario y UrbanSyn como fuente sintética principal de instancias.
5. No iniciar entrenamiento hasta revisar la reproducción del CLI y decidir explícitamente el protocolo.

## Reproducibilidad y archivos

- Notebook para ejecutar el **script real** en Colab, recuperar el artifact, reconstruir manifiestos, generar cap 200 y comparar caps: [`notebooks/colab_generar_plan_cap200.ipynb`](../blob/urban-models-and-benchmark/notebooks/colab_generar_plan_cap200.ipynb).
- Paquete de auditoría generado en esta sesión: contiene manifiestos cap 200, informe JSON, comprobación de reconstrucción y comparación de caps. No contiene imágenes ni máscaras.
- La reproducción local realizada para esta auditoría siguió la función determinista `greedy_balanced_select` del script actual, con semilla y desempate SHA-256 idénticos. El notebook Colab permite confirmar el mismo resultado ejecutando el CLI del repositorio y guardar la evidencia en Drive.

**Estado:** plan cap 200 auditado, pero no aprobado para entrenamiento. `RUN_TRAINING=False`.
