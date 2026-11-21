# Preparación de datasets con GitHub Actions y Google Drive

## Diseño y alcance

El workflow `.github/workflows/prepare-datasets.yml` se ejecuta manualmente desde **Actions → Prepare urban datasets (Google Drive) → Run workflow**. Descarga temporalmente una carpeta de Drive en el runner, valida su estructura, genera los derivados permitidos y sube únicamente los resultados preparados y el manifiesto a Drive. Los archivos fuente no se copian al repositorio ni a los artifacts de GitHub.

El runner es efímero: su copia local se elimina al terminar el trabajo. Este workflow prepara datos; **no entrena modelos** y no requiere GPU.

## Configurar Google Drive (OAuth de tu cuenta)

Se usa OAuth de Google Drive mediante rclone, para que las escrituras consuman el almacenamiento de tu propia cuenta y no dependan de la cuota de una cuenta de servicio.

1. Instala [rclone](https://rclone.org/install/) en tu PC o en Termux.
2. Ejecuta `rclone config` y crea un remote nuevo con:
   - Nombre: `gdrive`
   - Tipo: `drive` (Google Drive)
   - Scope: `drive` (acceso completo necesario para leer los archivos existentes y escribir los derivados)
   - Deja vacíos `client_id` y `client_secret` si no configuraste tu propia aplicación OAuth.
   - Acepta la autorización OAuth en el navegador con la cuenta de Google donde guardarás los datasets.
   - Conserva el resto de opciones por defecto, salvo que necesites una configuración particular.
3. Comprueba la conexión local con `rclone lsd gdrive:`.
4. Consulta `rclone config file` para localizar el archivo de configuración. Copia su contenido completo; incluye un token OAuth renovable.
5. En GitHub abre **Settings → Secrets and variables → Actions → New repository secret** y crea:
   - `GDRIVE_RCLONE_CONFIG`: contenido completo del archivo `rclone.conf`.
6. No compartas el contenido de ese archivo, no lo subas al repositorio ni lo pegues en conversaciones. Si se expone, revoca el acceso de rclone desde tu cuenta de Google y genera un token nuevo.

Usa preferiblemente una cuenta de Google dedicada al proyecto o una cuenta cuya unidad de Drive no contenga archivos sensibles, ya que el scope `drive` permite acceso amplio a Drive. La carpeta `bdd100k` debe existir en la raíz de ese Drive.

## Estructura esperada en Google Drive

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
<raíz-de-Drive>/
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
