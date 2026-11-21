# Registro de trabajo y estado del proyecto

> **Documento de continuidad.** Este archivo es la fuente principal para recuperar el contexto, las decisiones, el estado real y los próximos pasos del trabajo. Debe consultarse al comenzar cada nueva intervención relacionada con el proyecto y actualizarse al terminarla, registrando también cuando una acción no se haya podido completar.
>
> Última actualización: **2026-11-21**.

## 1. Identidad y objetivo del proyecto

- **Repositorio:** [Leohf04/Procesamiento-de-Im-genes-](https://github.com/Leohf04/Procesamiento-de-Im-genes-)
- **Rama de trabajo:** `urban-models-and-benchmark`
- **Pull request principal de implementación:** [PR #3](https://github.com/Leohf04/Procesamiento-de-Im-genes-/pull/3). Mantener abierto y en draft hasta que el usuario autorice expresamente otra cosa.
- **Proyecto académico:** Equipo 2 — Detección y segmentación semántica en escenas urbanas (multiclase + instancias).

### Objetivo técnico

Construir y evaluar un sistema de percepción urbana que detecte y segmente elementos de escenas viales (peatones, vehículos, ciclistas, señales y carriles), compare arquitecturas y mida calidad y rendimiento en condiciones representativas.

### Objetivo operativo actual (prioritario)

Ejecutar **todo el flujo pesado en infraestructura remota**, sin que el usuario tenga que descargar datasets en su teléfono ni transferirlos desde su conexión:

1. Obtener/acceder a los datasets desde una fuente remota autorizada.
2. Preparar datos, validar anotaciones, crear máscaras y particiones.
3. Entrenar modelos utilizando GPU remota.
4. Evaluar los modelos y ejecutar benchmarks.
5. Conservar checkpoints, métricas, gráficas, predicciones, manifiestos y documentación.
6. Permitir que el usuario controle el proceso desde Android mediante navegador, sin almacenar datasets originales en el dispositivo.

El resultado esperado no es solamente un repositorio de datasets: se necesita un **entorno de cómputo remoto** capaz de ejecutar preparación, entrenamiento GPU y evaluación, además de un destino persistente para resultados.

## 2. Restricciones y preferencias confirmadas

- El usuario no dispone de espacio ni conexión suficiente para descargar datasets en su dispositivo.
- No pedir que descargue los datasets a su teléfono ni que los suba manualmente desde el teléfono.
- Priorizar alternativas gratuitas; se puede comparar una opción económica de pago si es necesaria para GPU, pero no contratar ni incurrir en gastos sin autorización.
- No solicitar ni recibir contraseñas, tokens, claves API ni archivos OAuth en el chat. Usar secretos de la plataforma.
- No hacer público el repositorio privado.
- No fusionar PRs sin autorización expresa.
- Distinguir siempre entre código implementado, pruebas automatizadas, ejecuciones reales de entrenamiento y resultados experimentales. No declarar entrenamientos, métricas o pruebas como realizados sin evidencia.

## 3. Estado de datasets y acceso

### BDD100K

- Es la fuente prevista para experimentos de carriles y evaluación en condiciones reales.
- El repositorio incluye preparación de máscaras binarias a partir de anotaciones lane marking.
- La estructura que espera el flujo existente incluye imágenes y JSON de anotaciones de carriles.
- Se mencionó una copia de BDD100K alojada en Hugging Face: [liqijia/BDD100K-Semantic-Segmentation](https://huggingface.co/datasets/liqijia/BDD100K-Semantic-Segmentation).
- **Pendiente:** verificar origen, licencia/condiciones de redistribución, contenido real, particiones, correspondencia de imágenes y etiquetas, clases y compatibilidad con las tareas. No asumir que esa copia sustituye al dataset oficial ni que contiene todos los componentes requeridos.

### Cityscapes

- El usuario indicó previamente que no está registrado en Cityscapes.
- El acceso oficial requiere registro y aceptación de sus condiciones.
- No utilizar redistribuciones de terceros ni automatizar descargas protegidas sin autorización.
- **Pendiente:** decidir si el usuario se registra y obtiene acceso, o si se elige un dataset alternativo con licencia y acceso compatibles.

### Regla de diseño

Hugging Face puede servir como alojamiento/distribución de datasets y modelos, pero **no equivale por sí mismo a una máquina de entrenamiento GPU**. La arquitectura debe identificar por separado:
- fuente de datos;
- cómputo remoto GPU;
- almacenamiento persistente de resultados;
- conexión segura al repositorio privado.

## 4. Historial de decisiones y acciones

### 2026-11-21 — Necesidad de ejecución sin descargas locales

- El usuario aclaró que no puede descargar datasets por falta de espacio y conexión.
- Se identificó que el flujo previo de Google Drive + GitHub Actions todavía exigía que los datos originales se descargaran y subieran a Drive desde algún lugar.
- Se explicó que GitHub Actions estándar no es la opción adecuada como entorno principal de entrenamiento GPU de modelos grandes; puede servir para automatización y CI, pero tiene recursos y almacenamiento temporal limitados.

### 2026-11-21 — Evaluación de Kaggle

- Se propuso Kaggle Notebooks como entorno remoto con GPU, conectando el repositorio privado mediante un secreto de solo lectura.
- Se indicó crear un Notebook y configurar Internet, GPU y secreto `GITHUB_TOKEN`.
- Se creó/está presente en la rama el Notebook de diagnóstico:
  - `notebooks/kaggle_environment_check.ipynb`
  - Comprueba acceso al repositorio, entorno PyTorch/CUDA e inputs montados; no inicia entrenamiento ni descarga datasets.
- También existe `docs/KAGGLE_NOTEBOOK.md`, con instrucciones de configuración.
- El usuario informó que la verificación telefónica de Kaggle devuelve **“Permission denied”**, incluso después de introducir su número y completar el CAPTCHA.
- Conclusión operativa: Kaggle no se considera una alternativa viable por ahora. No insistir en la verificación ni solicitar otra línea telefónica.

### 2026-11-21 — Alternativa Hugging Face y necesidad de separar datos/cómputo

- Se propuso Hugging Face como posible fuente remota de datos BDD100K.
- Se mencionaron RunPod y Google Cloud como posibles entornos de cómputo GPU remoto.
- Aún **no se ha elegido ni validado** una plataforma sustituta de Kaggle.
- El usuario precisó que la solución debe cubrir:
  - entorno remoto de entrenamiento;
  - GPU;
  - preparación de datos;
  - entrenamiento;
  - evaluación;
  - conservación de resultados, modelos, métricas y documentación.
- La siguiente tarea es comparar alternativas concretas, priorizando gratuitas y explicando límites, verificación, cuotas, persistencia, disponibilidad de GPU, coste y compatibilidad con Android.

## 5. Estado de implementación existente en el repositorio

La rama `urban-models-and-benchmark` ya contiene scripts y documentación para varias tareas. Esto no significa que los entrenamientos se hayan ejecutado:

- DeepLabV3+ ResNet-50 para 11 clases semánticas Cityscapes.
- Fine-tuning de Mask R-CNN para siete clases de instancias Cityscapes.
- Preparación de máscaras binarias de carriles desde polígonos BDD100K.
- Entrenamiento de segmentador de carriles.
- Evaluadores semántico/instancias/carriles y benchmark.
- Exportación e inferencia ONNX para segmentación semántica y carriles.
- Workflow de GitHub Actions para preparar BDD100K por lotes desde Google Drive, que todavía requiere que los archivos estén previamente en Drive.
- Notebook de diagnóstico de Kaggle y documentación asociada.

### Limitaciones conocidas

- BDD100K lane pipeline no sustituye automáticamente los loaders, mapeos y evaluadores de Cityscapes para semántica multiclase e instancias.
- El AP50 existente para Mask R-CNN es AP de cajas, no AP de máscaras.
- Faster R-CNN del enfoque híbrido continúa basado en COCO y no está fine-tuned en datos urbanos.
- El pipeline ONNX actual cubre semántica y carriles, no Mask R-CNN/instancias.
- No hay evidencia en este registro de que se hayan entrenado modelos con datasets reales ni generado checkpoints experimentales.
- El workflow de Google Drive no resuelve el requisito de no transferir datasets desde el dispositivo del usuario.

Para detalles técnicos, consultar también:
- `README.md`
- `docs/PROTOCOLO_EXPERIMENTAL.md`
- `docs/KAGGLE_NOTEBOOK.md`
- `docs/DATASETS_GITHUB_ACTIONS.md`

## 6. Próxima fase: seleccionar y construir el entorno remoto

Antes de modificar el código de entrenamiento, comparar al menos estas categorías:

1. **Entornos notebook gratuitos con GPU**: verificar si permiten uso sin verificación telefónica problemática, conexión a repositorios privados, Internet, sesiones largas y persistencia.
2. **Plataformas GPU bajo demanda**: por ejemplo RunPod u otras alternativas; estimar coste real por hora y almacenamiento, sin contratar todavía.
3. **Servicios cloud generales**: considerar Google Cloud u opciones equivalentes solo si el coste/cuotas tienen sentido.
4. **Datos alojados remotamente**: verificar Hugging Face y otras fuentes oficiales/autorizadas; no confundir hosting de datos con cómputo.

### Criterios obligatorios de comparación

- ¿Permite usar GPU para PyTorch/Torchvision?
- ¿Requiere verificación telefónica, tarjeta bancaria o método de pago?
- ¿Tiene nivel gratuito real y cuáles son sus límites?
- ¿Permite Internet y clonar un repositorio GitHub privado mediante secretos?
- ¿Dónde se almacenan datasets y checkpoints entre sesiones?
- ¿Puede acceder a datasets sin que el usuario los descargue o suba desde su teléfono?
- ¿Puede ejecutar trabajos largos y reanudables con checkpoints?
- ¿Cómo se exportan resultados a un almacenamiento persistente?
- ¿Qué coste estimado tendría una ejecución representativa?
- ¿Qué condiciones/licencias aplican a los datasets?

### Arquitectura objetivo

```text
Repositorio GitHub privado
        |
        | código + configuración (token de solo lectura)
        v
Entorno de cómputo remoto con GPU
        |
        +---- Acceso remoto/autorizado a datasets
        |
        +---- Preparación y validación de datos
        |
        +---- Entrenamiento con checkpoints reanudables
        |
        +---- Evaluación y benchmark
        |
        v
Almacenamiento persistente de resultados
        |
        +---- Modelos/checkpoints
        +---- Métricas JSON/CSV
        +---- Gráficas y predicciones
        +---- Manifiestos y logs
        +---- Informe experimental
```

El usuario accede desde Android al panel/notebook y consulta los resultados. Los datasets originales no deben pasar por el teléfono.

## 7. Protocolo de actualización de este documento

En cada intervención futura relacionada con este proyecto:

1. Leer este documento antes de proponer o ejecutar cambios, para recuperar el objetivo y el punto exacto de continuidad.
2. Identificar qué solicitó el usuario en ese mensaje y si modifica una decisión o restricción.
3. Registrar la decisión, investigación, cambio de código, prueba, error o bloqueo producido.
4. Actualizar la sección de estado y los próximos pasos cuando corresponda.
5. Guardar los cambios en la rama `urban-models-and-benchmark` con un mensaje de commit descriptivo.
6. Informar al usuario qué se actualizó y enlazar el documento.
7. Si no fue posible actualizar GitHub, decirlo explícitamente y no afirmar que el registro quedó guardado.

Este registro debe ser conciso pero suficiente para que una conversación nueva pueda continuar sin volver a preguntar al usuario lo que ya está decidido. Registrar hechos verificables; separar claramente decisiones, hipótesis y tareas pendientes.
