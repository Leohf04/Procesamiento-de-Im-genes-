# Ejecutor de entrenamiento multidominio

**Motor implementado; todavía no es un pipeline end-to-end listo para lanzar. No iniciar piloto.**

## Entrega

- `src/urban_experiment_runner.py`: loops por tarea, loss finita, validación semántica (mIoU/IoU por clase/soporte/matriz de confusión), AMP opcional solo CUDA, clipping opcional, scheduler, early stopping, límite temporal por época y logs JSONL.
- Checkpoints `last.pt`/`best.pt` atómicos con modelo, optimizer, scheduler, scaler, época/global step, mejor métrica, paciencia, RNG Python/NumPy/PyTorch/CUDA, hash de configuración y metadatos. La reanudación rechaza un hash de configuración diferente.
- `scripts/run_urban_experiment.py`: CLI protegido; requiere simultáneamente `run_training: true` en el JSON y `--execute`. La factory Python `module:function` entrega modelo, loaders train/validation, optimizer y tarea. No recibe test.
- `tests/test_urban_experiment_runner.py`: pruebas sintéticas de métricas, ignore 255, checkpoint, hash y bloqueo de Mask AP.

## Factory de datos/modelo

Debe devolver `model`, `train_loader`, `validation_loader`, `optimizer`, `task`; opcionalmente `class_weights`, `scheduler`, `device`. Para instancias debe devolver `detection_evaluator(model, validation_loader, device)` con `mask_ap` numérico calculado mediante COCOeval validado. AP de cajas no satisface el contrato.

La factory aún debe materializar los manifiestos completos A2D2/UrbanSyn en almacenamiento remoto, emparejar anotaciones por sample_id, usar loaders de train existentes y un loader determinista de validation. No pasar test. A2D2 conserva la limitación de instancias aproximadas por componentes conectados.

## Configuración plantilla (bloqueada)

```json
{"run_training":false,"experiment_id":"SEM-URBANSYN","dataset":"urbansyn","seed":2026,"max_epochs":5,"patience":2,"max_seconds":5400,"num_classes":20,"ignore_index":255,"amp":false}
```

## Pendiente antes de piloto

1. Factory real de las cuatro configuraciones y materializador remoto train/validation.
2. Evaluador COCO Box AP y Mask AP validado contra COCOeval; hasta entonces Mask R-CNN queda bloqueado.
3. Prueba de integración con muestras reales de train y validation, checkpoint/resume y recursos GPU/almacenamiento.
4. Suite de pruebas ejecutada en el HEAD exacto.

No se ha ejecutado el motor, no se descargaron datasets ni se creó checkpoint experimental. `RUN_TRAINING=False` permanece. Implementar el motor no autoriza el piloto. PR #3 continúa abierta y draft.
