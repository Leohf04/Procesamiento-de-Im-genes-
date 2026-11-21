# Preparación de datasets con GitHub Actions y Google Drive

## Diseño y alcance

El workflow `.github/workflows/prepare-datasets.yml` se ejecuta manualmente desde **Actions → Prepare urban datasets (Google Drive) → Run workflow**. Descarga temporalmente una carpeta de Drive en el runner, valida su estructura, genera los derivados permitidos y sube únicamente los resultados preparados y el manifiesto a Drive. Los archivos fuente no se copian al repositorio ni a los artifacts de GitHub.

El runner es efímero: su copia local se elimina al terminar el trabajo. Este workflow prepara datos; **no entrena modelos** y no requiere GPU.

## Configuración de Google Drive

Se usa una cuenta de servicio de Google Cloud con acceso limitado a una carpeta específica:

1. Crea una cuenta de servicio en un proyecto de Google Cloud y habilita Google Drive API.
2. Genera una clave JSON para esa cuenta de servicio.
3. Crea una carpeta raíz en Google Drive y compártela con el correo de la cuenta de servicio, con permiso de editor (el workflow lee fuentes y escribe resultados).
4. En el repositorio abre **Settings → Secrets and variables → Actions → New repository secret** y crea:
   - `GDRIVE_SERVICE_ACCOUNT_JSON`: contenido completo del archivo JSON de la cuenta de servicio.
   - `GDRIVE_FOLDER_ID`: ID de la carpeta raíz compartida.
5. No pegues claves privadas ni tokens en el código, issues o conversaciones. Si la clave se expone, revócala y genera otra.

La cuenta de servicio debe tener acceso explícito a la carpeta compartida. No se necesita compartir públicamente los datasets.

## Estructura esperada dentro de la carpeta raíz de Drive

Para BDD100K, sube manualmente los archivos que hayas obtenido conforme a sus términos:

```text
bdd100k/
├── images/
│   └── 100k/
│       ├── train/
│       └── val/
└── labels/
    └── lane/
        ├── train.json
        └── val.json
```

Los JSON deben ser listas de frames con `name` y `labels`; las anotaciones de carril deben incluir `category: "lane"` y polígonos `poly2d` con vértices. El nombre de cada imagen debe coincidir con `name` en el JSON. Se validan imágenes existentes/legibles y se generan máscaras binarias PNG con el rasterizador del proyecto. El grosor por defecto es 8 píxeles.

Para Cityscapes, cuando tengas una cuenta registrada y acceso autorizado, la estructura que deberá subirse será:

```text
cityscapes/
├── leftImg8bit/{train,val}/<city>/*_leftImg8bit.png
└── gtFine/{train,val}/<city>/*_gtFine_labelIds.png
```

**Cityscapes está bloqueado actualmente** porque el propietario del proyecto indicó que aún no está registrado. El workflow rechaza la opción `cityscapes` de forma explícita; no automatiza el acceso, no usa credenciales de terceros y no descarga archivos protegidos. Después del registro y de aceptar los términos oficiales habrá que revisar las condiciones vigentes y habilitar esta etapa en el código.

## Ejecutar

1. Abre la pestaña **Actions** del repositorio.
2. Selecciona **Prepare urban datasets (Google Drive)**.
3. Pulsa **Run workflow**.
4. Para BDD100K, selecciona `bdd100k`, deja `drive_source_path=bdd100k` si usaste esa carpeta y conserva `lane_thickness=8`.
5. Inicia la ejecución y revisa el log.

La salida se guarda en:

```text
<carpeta-raíz-drive>/
└── prepared/
    └── bdd100k/
        └── <run_id>-<run_attempt>/
            ├── dataset_manifest.json
            └── lane_masks/{train,val}/*.png
```

El manifiesto registra el dataset, los conteos por split y el estado de validación. Si faltan imágenes, están corruptas, no existe el JSON o no coincide el número de máscaras, el job falla y no publica una preparación incompleta.

## Límites y seguridad

- No subir datasets, checkpoints ni credenciales a Git.
- No usar GitHub Actions artifacts/cache como almacenamiento permanente de datasets grandes.
- El workflow no descarga BDD100K desde una URL no verificada: el usuario coloca en Drive los archivos descargados legítimamente.
- El split de BDD100K debe ser por video/secuencia, no por frames aleatorios adyacentes. Este workflow valida los splits entregados, pero no puede demostrar por sí solo que se construyeron sin fuga temporal.
- Los runners estándar de GitHub Actions son CPU; esta etapa no entrena DeepLabV3+ ni Mask R-CNN.
- Los resultados derivados deben usarse respetando los términos/licencias del dataset de origen.
