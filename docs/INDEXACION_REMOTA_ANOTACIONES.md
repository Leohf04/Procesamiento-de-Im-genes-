# Indexación remota de anotaciones por imagen

## Objetivo
Generar estadísticas individuales de etiquetas para cada fila de los manifiestos A2D2 y UrbanSyn. No descarga fotografías RGB ni escribe imágenes, máscaras o derivados en Git. Los artifacts contienen identificadores y conteos de píxeles/objetos.

## Ejecución
Workflow manual: **Build per-image annotation indexes and balanced manifests**.

Parámetros por defecto: semilla 2026 y hasta 1.000 muestras por split y dataset. El job construye manifiestos remotos, descarga únicamente las anotaciones necesarias, crea seis índices y ejecuta el planificador.

El primer procesamiento puede tardar varias horas y consumir ancho de banda de GitHub Actions: cada máscara debe leerse para contar etiquetas. El límite de 1.000 muestras por split coincide con los manifiestos experimentales. Si se reduce, el resultado cubre solo el manifiesto acotado.

## Esquema por fila
    {"sample_id":"sample-001","annotation_status":"ok","semantic_pixels":{"road":120000,"car":9000},"instance_counts":{"car":3,"person":1}}

- A2D2: máscara semántica RGB de S3 anónimo; ontología común y componentes conectados con área mínima 8 px.
- UrbanSyn: semseg y panoptic desde la revisión fijada en el manifiesto; unlabeled queda en ignore.
- Un error de lectura, forma, decodificación o ID hace fallar el job; nunca se interpreta como muestra vacía.

## Salida y límites
Genera seis archivos JSONL, resúmenes de cobertura y manifiestos balanceados separados por dataset/tarea. Validation y test permanecen completos. No se mezclan dominios.

El selector prioriza clases raras por presencia en imágenes; no reemplaza un sampler ni pesos de pérdida. El informe contrasta además la cobertura observada con las clases esperadas de la ontología por dataset/tarea: `unavailable_classes` enumera clases sin presencia en todo el split indexado y `uncovered_classes` las que no quedaron representadas en la selección. El workflow manual y el smoke por cambios usan ahora 1.000 muestras por split como límite predeterminado. RUN_TRAINING permanece False. Licencia UrbanSyn: criterio conservador CC BY-NC-SA 4.0; no redistribuir datos ni máscaras.
