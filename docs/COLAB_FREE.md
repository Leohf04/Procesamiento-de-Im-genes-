# Google Colab Free — ejecución remota

Este procedimiento permite operar el proyecto desde Android sin descargar datasets al teléfono. Colab proporciona una VM temporal; Google Drive conserva checkpoints y resultados. La GPU es variable y no está garantizada.

## Notebook del proyecto

[Abrir el notebook de entrenamiento en Colab](https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/colab_free_urban_training.ipynb)

Si el enlace no abre el repositorio privado, entra en Colab con la cuenta Google, autoriza el acceso a GitHub y vuelve a abrirlo desde el navegador de GitHub.

## Requisitos de GitHub

El notebook clona el repositorio privado mediante un token de solo lectura:

1. En GitHub, crea un Fine-grained personal access token.
2. Limita el acceso al repositorio `Leohf04/Procesamiento-de-Im-genes-`.
3. Otorga únicamente **Contents: Read-only**.
4. En Colab, abre el panel **Secrets** (icono de llave) y crea `GITHUB_TOKEN` con el valor del token.
5. Habilita el acceso del notebook a ese secreto.

No pegues el token en una celda, no lo guardes en el notebook y no lo compartas en conversaciones. Si no usas Colab Secrets, el notebook solicita el token ocultando la entrada para esa sesión.

## Preparación

1. Selecciona Runtime → Change runtime type → T4 GPU si está disponible.
2. Ejecuta las celdas en orden.
3. Monta Drive; el notebook crea `MyDrive/ProcesamientoImagenes/resultados/`.
4. Clona la rama `urban-models-and-benchmark`.
5. Instala dependencias adicionales sin reemplazar PyTorch/Torchvision que ya proporciona Colab.
6. Comprueba GPU, versiones y estructura de dataset.
7. Mantén `RUN_TRAINING = False` hasta que el dataset esté autorizado y validado.

## Organización de datos y resultados

- Datos temporales de entrenamiento: `/content/datasets/` (disco de la VM Colab; se pierde al terminar la sesión).
- Resultados persistentes: `/content/drive/MyDrive/ProcesamientoImagenes/resultados/`.
- Checkpoints, historiales, métricas, gráficas e informes se guardan en Drive.
- No guardar datasets grandes en GitHub ni transferirlos desde el teléfono.

BDD100K es el dataset principal. Los datos deben llegar directamente a la VM desde una fuente oficial/autorizada; nunca descargues ni subas archivos desde el teléfono. La documentación oficial publica el mirror ETH Zürich y los tamaños aproximados: imágenes 10K 1.1 GB, máscaras semánticas 419 MB e instancias 111 MB. Las imágenes 10K no son necesariamente subconjunto exacto de las 100K. Para semántica/instancias no descargues vídeos 1.8 TB ni imágenes 100K si no vas a ejecutar detección/carriles. Consulta [descarga oficial BDD100K](https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst) y [formato oficial de etiquetas](https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst). No se configura una URL directa sin verificar primero el archivo exacto y su checksum.

## Validación acotada de muestras reales

Antes de cualquier entrenamiento, el notebook ejecuta:

```bash
python scripts/validate_bdd100k_semantic_sample.py --samples-per-split 2
```

El script recupera dos pares imagen/máscara de train y dos de validación desde el mirror público `liqijia/BDD100K-Semantic-Segmentation` en Hugging Face, usando la API de archivos para descargar solo los archivos de esas muestras. Comprueba que las imágenes sean RGB, que las máscaras sean monocanal, que coincidan sus dimensiones, que los IDs sean 0–18/255 y que `BDD100KSemanticDataset` produzca tensores válidos. La descarga se limita a unas pocas muestras temporales en la VM y se elimina al terminar.

**Alcance y cautela:** el mirror es una redistribución de terceros cuya tarjeta declara que los píxeles y máscaras de IDs se conservan sin modificar respecto a la publicación oficial y reproduce la licencia BDD100K. Esta prueba es una validación técnica provisional del cargador semántico, no una auditoría independiente de procedencia ni una validación de los loaders de instancias, detección o carriles. Esas tareas siguen pendientes de muestras oficiales correspondientes.

GitHub Actions ejecuta esta misma prueba junto con la suite automatizada. En Colab, además, permite comprobarla en el entorno real de la sesión sin descargar el paquete completo. `RUN_TRAINING` debe permanecer en `False`.

## Reanudación de entrenamientos

Los scripts de DeepLabV3+ y Mask R-CNN guardan:
- checkpoint de modelo para evaluación/inferencia;
- checkpoint `.last.pt` con estado de optimizador (y scheduler en Mask R-CNN);
- historial JSON actualizado al final de cada época.

Ejemplo para BDD100K semántico:

```bash
python scripts/train_urban_segmentation.py \
  --task bdd100k-semantic \
  --images-dir /content/datasets/bdd100k/images/10k/train \
  --masks-dir /content/datasets/bdd100k/labels/sem_seg/masks/train \
  --val-images-dir /content/datasets/bdd100k/images/10k/val \
  --val-masks-dir /content/datasets/bdd100k/labels/sem_seg/masks/val \
  --epochs 30 --batch-size 2 --workers 2 \
  --output /content/drive/MyDrive/ProcesamientoImagenes/resultados/checkpoints/deeplabv3plus_bdd100k_semantic.pt
```

Para reanudar desde el checkpoint `.last.pt`, añade `--resume` al mismo comando. El flujo de instancias usa `scripts/train_maskrcnn_cityscapes.py --dataset bdd100k` con las rutas `images/10k` y `labels/ins_seg/bitmasks`.

`--epochs` representa el total final de épocas. Por ejemplo, si el checkpoint ya completó 8 épocas y se indica `--epochs 30`, ejecutará las 22 restantes. La reanudación ocurre entre épocas, no a mitad de un lote.

## Limitaciones de Colab Free

- GPU sujeta a disponibilidad, cuotas y límites dinámicos.
- Sesiones temporales; el máximo de ejecución no está garantizado.
- El disco local de la VM es efímero.
- Google Drive tiene cuota y límites de I/O; checkpoints grandes pueden tardar en guardarse.
- No usar SSH, túneles o servicios externos para convertir Colab Free en un servidor persistente.
- Si no hay GPU, no ejecutar entrenamientos grandes.

## Estado de validación

La existencia del notebook y los scripts no significa que se haya ejecutado un entrenamiento. Antes del primer entrenamiento hay que validar acceso GitHub, GPU, compatibilidad PyTorch/Torchvision y el dataset real.


## Flujos BDD100K integrados

- Semántica: `scripts/train_urban_segmentation.py --task bdd100k-semantic` usa 19 clases y `ignore=255`.
- Instancias: `scripts/train_maskrcnn_cityscapes.py --dataset bdd100k` decodifica PNG RGBA oficiales y ajusta ocho clases.
- Colab valida presencia y conteo de imágenes/máscaras, y mantiene `RUN_TRAINING=False` por defecto.
- Aún no está integrada una descarga automática reproducible desde el mirror: antes debe verificarse el nombre exacto de cada archivo, su MD5 y las condiciones de acceso. No se deben inventar enlaces.
- Detección 2D (100K/Det_20), carriles multiatributo (categoría/dirección/estilo), evaluación BDD100K de instancias y métricas mask AP siguen pendientes. No iniciar esos experimentos hasta completar y probar sus adaptadores.
