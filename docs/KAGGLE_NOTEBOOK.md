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

## 5. Entrenamiento Urban-v1 en Kaggle

La notebook de entrenamiento ya adaptada es:

- `notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb`
- URL del archivo: https://github.com/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb

Como el repositorio es privado, descarga ese archivo pequeño `.ipynb` desde GitHub e impórtalo en un Notebook nuevo de Kaggle (File → Import Notebook, o la opción equivalente disponible). Esto no implica descargar datasets al teléfono. Los datasets se obtienen directamente desde el runtime remoto.

### Configuración obligatoria

1. Notebook privado.
2. Settings → Session options: Python, Accelerator = GPU disponible, Internet = On.
3. Add-ons → Secrets: secreto `GITHUB_TOKEN`, habilitado para este Notebook. Fine-grained PAT limitado a este repositorio, con Contents: Read-only y Actions: Read-only.
4. No pegues el token en celdas ni compartas salidas que puedan contenerlo.
5. Ejecuta las celdas en orden. La celda de GPU detiene el proceso antes de descargar datos si CUDA no está disponible.

### Qué hace la notebook

- Sincroniza la rama `urban-models-and-benchmark`.
- Ejecuta `pytest -q` y bloquea el flujo si falla.
- Recupera el artifact de metadatos de GitHub Actions y verifica digest/expiración.
- Reconstruye los manifiestos e índices completos TRAIN/VAL.
- Ejecuta dry-run de los 3.751 registros y comprueba espacio.
- Materializa los datos en `/kaggle/temp`, nunca en el teléfono.
- Audita assets e IDs; ejecuta el piloto de 10 batches para cada experimento.
- Solo si los cuatro pilotos pasan, ejecuta S-A2D2, S-UrbanSyn, I-UrbanSyn e I-A2D2.
- Guarda checkpoints, métricas y resumen bajo `/kaggle/working/urban-results`.
- No abre ni evalúa TEST.

**Alcance de datos:** esta configuración corresponde a A2D2 + UrbanSyn, según `configs/urban_experiment_v1.json`. No debe describirse como entrenamiento BDD100K. El pipeline BDD100K de carriles es independiente y no sustituye las tareas semánticas/instancias de estos cuatro experimentos.

### Límites y persistencia de Kaggle

La documentación de Kaggle indica sesiones de notebook de hasta 12 horas y hasta 20 GB de salida guardable en `/kaggle/working`; la GPU gratuita puede estar limitada o en cola. No se garantiza un tipo de GPU concreto ni una cuota semanal fija. Antes de entrenar, confirma en Settings que tu cuenta permite seleccionar GPU.

Al terminar correctamente, utiliza **Save Version** y conserva la salida del Notebook. La notebook limita cada experimento a 5.400 segundos por sesión y escribe checkpoints en la carpeta de resultados. Si una sesión se interrumpe antes de guardar una versión, no des por hecho que los checkpoints quedaron persistidos: revisa la pestaña Output y guarda una versión cuando sea posible.

### Primer arranque seguro

Primero confirma que puedes crear/abrir el Notebook, activar Internet y seleccionar GPU. Después ejecuta las celdas iniciales de sincronización y diagnóstico. Si aparece cualquier error, comparte el traceback completo sin incluir el token. No continúes saltándote una celda fallida.

## 6. Notebook de diagnóstico mínimo

`notebooks/kaggle_environment_check.ipynb` permanece disponible para diagnosticar acceso privado al repositorio, PyTorch/CUDA e inputs montados sin descargar datasets ni iniciar entrenamiento. Si la notebook de entrenamiento falla durante el arranque, puede utilizarse para aislar el problema de cuenta, secreto o GPU.
