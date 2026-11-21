# Ejecutar el proyecto en Kaggle Notebooks

## Objetivo

Kaggle ejecuta el código y el entrenamiento en sus máquinas remotas. El teléfono solo necesita abrir el navegador. Los datasets deben añadirse como fuentes de entrada de Kaggle o leerse desde una fuente remota autorizada; no se deben descargar al teléfono ni subirse manualmente desde él.

## 1. Crear el Notebook

1. Abre https://www.kaggle.com/code y crea un Notebook privado.
2. Nombre sugerido: `urban-semantic-instance-segmentation`.
3. En Settings / Session options:
   - Language: Python.
   - Accelerator: GPU (elige la opción disponible; T4 x2 si se ofrece).
   - Internet: On.
   - Docker image: Latest/default.
4. No selecciones TPU. El proyecto usa PyTorch/Torchvision y requiere GPU CUDA.
5. No inicies un entrenamiento largo todavía. Primero ejecuta la notebook de verificación y confirma que detecta CUDA.

Kaggle cambia la disponibilidad de aceleradores y cuotas según la cuenta y la demanda. Una GPU T4 x2 no está garantizada. La documentación oficial describe sesiones de hasta 12 horas y almacenamiento persistente de salida limitado; comprueba los límites que muestre tu cuenta.

## 2. Permitir que Kaggle lea el repositorio privado

No hagas público el repositorio.

1. En GitHub crea un Fine-grained Personal Access Token desde https://github.com/settings/personal-access-tokens.
2. Limítalo al repositorio `Leohf04/Procesamiento-de-Im-genes-`.
3. Otorga solo permiso **Contents: Read-only**. No necesita permisos de escritura.
4. En Kaggle Notebook abre Add-ons → Secrets (en algunas interfaces aparece como Secrets).
5. Crea un secreto con etiqueta exacta `GITHUB_TOKEN`, pega el token y habilítalo para este Notebook.
6. No escribas el token directamente en una celda, no lo imprimas y no publiques el Notebook con salidas que puedan contener credenciales.

La notebook `notebooks/kaggle_environment_check.ipynb` lee ese secreto y clona la rama `urban-models-and-benchmark` sin incluir el token en la URL del repositorio.

## 3. Dataset: no adjuntar copias de terceros sin validar

En el panel derecho abre Input → Add Input. Puedes adjuntar un dataset de Kaggle si verificamos primero su origen, licencia, anotaciones y estructura. No añadas todavía una copia cualquiera de BDD100K: hay redistribuciones parciales y sus etiquetas pueden no corresponder a las tareas del proyecto.

Para BDD100K, la preparación de carriles del repositorio espera:
- JSON de anotaciones lane marking con frames que contengan `name` y `labels`.
- Dentro de cada etiqueta de carril: `category: "lane"` y polígonos `poly2d`.
- Imágenes cuyo nombre coincida con `name` del JSON.
- Splits train y val independientes por secuencia/video.

El Notebook de verificación enumera los directorios montados bajo `/kaggle/input` sin copiar las imágenes a tu dispositivo.

**Estado de compatibilidad actual:** el código existente prepara y entrena segmentación binaria de carriles BDD100K. Los scripts semántico multiclase y Mask R-CNN del repositorio están basados en Cityscapes. No se debe afirmar que BDD100K ya sustituye Cityscapes para segmentación semántica multiclase e instancias: esos loaders, mapeos de clases y evaluadores aún requieren adaptación y validación.

## 4. Resultados y checkpoints

Guarda los resultados en `/kaggle/working/urban-results`. Al finalizar:
1. Usa Save Version → Save & Run All / Save Output para conservar la salida de la versión.
2. Para reutilizar resultados entre sesiones, crea un Dataset privado a partir de la salida del Notebook o usa un destino remoto seguro.
3. No guardes datasets originales, tokens ni credenciales dentro de la salida.
4. Guarda checkpoints por época o por etapas; una sesión interactiva interrumpida no debe ser el único lugar donde exista un checkpoint.

No subas checkpoints grandes a GitHub. Los resultados pueden incluir pesos entrenados, JSON de métricas, curvas y manifiestos.

## 5. Primer arranque

1. Abre `notebooks/kaggle_environment_check.ipynb` en Kaggle.
2. Habilita el secreto `GITHUB_TOKEN`.
3. Configura Internet On y GPU disponible.
4. Ejecuta todas las celdas.
5. Comprueba que la clonación termina, PyTorch detecta CUDA y se muestran los inputs disponibles.
6. Comparte aquí solo el resultado de diagnóstico (sin tokens). Con esa salida ajustaremos la ruta del dataset y activaremos el pipeline correspondiente.

## Referencias

- Kaggle Notebooks: https://www.kaggle.com/docs/notebooks
- Kaggle Datasets: https://www.kaggle.com/docs/datasets
- Kaggle API: https://www.kaggle.com/docs/api
- GitHub fine-grained tokens: https://github.com/settings/personal-access-tokens
