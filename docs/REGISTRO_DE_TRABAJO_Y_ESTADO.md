# Registro de trabajo y estado del proyecto

> **Documento de continuidad.** Este archivo es la fuente principal para recuperar el contexto, las decisiones, el estado real y los próximos pasos del trabajo. Debe consultarse al comenzar cada nueva intervención relacionada con el proyecto y actualizarse al terminarla, registrando también cuando una acción no se haya podido completar.
>
> Última actualización: **2026-11-24**.

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


### 2026-11-21 — Creación del registro de continuidad

- El usuario solicitó un documento dentro del repositorio que conserve el objetivo, las decisiones, las acciones y el punto de continuidad, y que se actualice en cada mensaje relacionado con el proyecto.
- Se creó este archivo como fuente principal de contexto y se enlazó desde el README.
- Compromiso operativo: consultar y actualizar este registro al trabajar en futuras intervenciones del proyecto; informar con transparencia si alguna actualización no puede guardarse.

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


## 8. Investigación de infraestructura remota completa — 2026-11-21

El usuario indicó que quiere retomar la selección de un entorno remoto completo de aprendizaje automático. El objetivo sigue siendo que preparación, entrenamiento GPU, evaluación y persistencia de resultados se ejecuten en la nube, controlados desde Android, sin transferir datasets por el teléfono.

### Plataformas investigadas (precios y condiciones consultados el 2026-11-21)

**RunPod — candidato principal para estación de trabajo GPU remota**
- Ofrece Pods GPU dedicados, plantillas/contenedores, acceso a puertos y almacenamiento persistente/Network Volumes.
- La documentación permite exponer JupyterLab por el puerto 8888 y configurar volúmenes en `/workspace`; el volumen de red desacopla los datos de una máquina GPU concreta.
- Precios publicados en la página oficial: RTX 3090 24 GB desde USD 0.50/h, A40 48 GB desde USD 0.59/h, L4 24 GB desde USD 0.69/h y RTX 4090 24 GB desde USD 0.89/h (pueden variar por Community/Secure Cloud, región y disponibilidad).
- Network Storage Standard: USD 0.07/GB/mes bajo 1 TB; otros tipos tienen tarifas distintas.
- Ventaja: se comporta más como una máquina Linux completa con GPU, adecuada para clonar el repositorio, instalar dependencias, preparar datos, entrenar, evaluar y conservar checkpoints.
- Riesgo/pendiente: es de pago por uso; antes de registrarse hay que comprobar método de pago/recarga, disponibilidad de GPU y coste total. No se ha verificado que evite la verificación telefónica, por lo que no prometerlo.
- Fuentes: https://www.runpod.io/pricing ; https://docs.runpod.io/ ; https://docs.runpod.io/pods/troubleshooting/zero-gpus

**Modal — candidato para pipeline automatizado**
- Plataforma serverless Python para ejecutar funciones y contenedores CPU/GPU, procesamiento de datos, entrenamiento y evaluación; dispone de Volumes para guardar datos/checkpoints y Secrets para credenciales.
- Plan Starter: USD 0 de cuota de plataforma + USD 30/mes de crédito de cómputo incluido; uso extra facturado según consumo. Publica GPU T4 a USD 0.000164/s (aprox. USD 0.59/h), L4 USD 0.000222/s (aprox. USD 0.80/h), A10 USD 0.000306/s (aprox. USD 1.10/h) y A100 80GB USD 0.000694/s (aprox. USD 2.50/h). Volumes incluyen hasta 1 TiB/mes según la página de precios.
- Ventaja: muy adecuado para automatizar jobs reproducibles desde GitHub y detener cómputo al terminar.
- Limitación: no es una estación de trabajo Jupyter persistente tradicional; exige adaptar el pipeline al SDK/contenedores Python. El crédito no implica GPU gratuita ilimitada.
- Pendiente: verificar requisitos de alta, facturación, tarjeta y disponibilidad regional antes de recomendar crear cuenta.
- Fuentes: https://modal.com/pricing ; https://modal.com/products/training

**Lightning AI Studios — no priorizar por el problema de verificación**
- Ofrece Studios tipo Jupyter/IDE, GPUs, ejecución de trabajos y almacenamiento persistente. La página consultada muestra 50 horas GPU gratuitas promocionadas, Studio gratuito con reinicio cada cuatro horas y almacenamiento persistente según plan.
- Sin embargo, su FAQ oficial dice que solicita número telefónico para prevenir abuso. Dado el problema actual del usuario con la verificación telefónica, no es la primera opción.
- Fuente: https://lightning.ai/pricing

**Google Colab gratuito — alternativa limitada, no solución principal**
- Ofrece notebooks alojados y acceso gratuito variable a GPU, pero recursos no garantizados; duración máxima habitual de 12 horas y límites dinámicos.
- La FAQ oficial restringe SSH/control remoto y workers distribuidos en el nivel gratuito sin saldo de compute units; no es apropiado como servidor remoto persistente ni para operar una interfaz web/servicio continuo.
- Fuente: https://research.google.com/colaboratory/faq.html

**Google Cloud Compute Engine — no es gratuito para GPU**
- El Free Tier de Compute Engine incluye una VM e2-micro en regiones determinadas, pero no incluye GPU/TPU; GPU/TPU se cobran aparte.
- Fuente: https://docs.cloud.google.com/free/docs/free-cloud-features

### Recomendación provisional

1. **RunPod Pod con JupyterLab + Network Volume** como estación de trabajo remota principal si el usuario acepta un coste bajo y confirma que puede completar el alta/pago. Es la experiencia más parecida a tener un servidor Linux completo con GPU.
2. **Modal Starter** como alternativa de automatización del pipeline si se prefiere ejecutar jobs por código y aprovechar el crédito mensual, una vez comprobados requisitos de cuenta y facturación.
3. Mantener Hugging Face como posible origen remoto de datasets/modelos, no como sustituto de cómputo GPU.
4. No volver a depender de Kaggle ni de Lightning AI como solución primaria sin resolver previamente sus requisitos de verificación.

### Arquitectura objetivo recomendada (pendiente de aprobación y prueba)

- GitHub privado: código, scripts, configuración y documentación.
- RunPod: Pod GPU con JupyterLab, contenedor PyTorch/CUDA y Network Volume montado en `/workspace`.
- Fuentes autorizadas de datasets: acceso remoto directo desde el Pod; validar licencia, integridad, clases y splits antes de descargar en el servidor.
- Pipeline: preparación/validación → entrenamiento con checkpoints reanudables → evaluación → benchmark.
- Network Volume: checkpoints, logs, métricas JSON/CSV, gráficas, manifiestos y predicciones.
- GitHub: guardar código y reportes ligeros; no subir datasets ni checkpoints grandes.
- Acceso del usuario desde Android mediante navegador a JupyterLab y panel de resultados.

### Estado y próxima acción

- Esta fase es investigación comparativa; no se ha creado cuenta, Pod, Volume ni se ha incurrido en gasto.
- No se ha descargado ningún dataset ni entrenado ningún modelo.
- Próximo paso: confirmar si el usuario acepta una opción de bajo coste bajo demanda (RunPod) o exige exclusivamente servicios gratuitos. Antes de desplegar nada, mostrar presupuesto estimado y verificar los requisitos de alta/pago.


## 9. Alternativas gratuitas y open source — 2026-11-21

El usuario pidió priorizar alternativas gratuitas u open source, manteniendo el requisito de no descargar datasets en el teléfono y controlar el trabajo desde Android. Se investigaron las siguientes opciones:

### Cómputo gratuito o con créditos incluidos

**Google Colab Free**
- Ofrece notebooks alojados con acceso gratuito y variable a GPU/TPU; la duración máxima de notebook es de hasta 12 horas, pero la disponibilidad y los límites cambian dinámicamente y no se garantiza GPU.
- Adecuado para adaptar el pipeline a ejecuciones por etapas, guardar checkpoints con frecuencia y reanudar cuando se obtenga otra sesión.
- No se debe tratar como servidor persistente: en el nivel gratuito están restringidos SSH/control remoto, workers distribuidos y el uso principalmente mediante una interfaz web externa. La interacción debe realizarse desde el notebook y cumplir sus políticas.
- Fuente oficial: https://research.google.com/colaboratory/faq.html

**Modal Starter**
- Plan de plataforma sin cuota mensual e incluye USD 30 mensuales de crédito de cómputo, aplicable a CPU, memoria y GPU. La tarifa T4 publicada es USD 0.000164/s (aprox. USD 0.59/h); L4 USD 0.000222/s (aprox. USD 0.80/h); A10 USD 0.000306/s (aprox. USD 1.10/h); A100 80 GB USD 0.000694/s (aprox. USD 2.50/h).
- Es una opción de crédito gratuito renovable, no GPU ilimitada ni software open source. El exceso se factura; revisar límites y facturación antes de ejecutar. Starter no debe confundirse con un notebook Jupyter persistente.
- Modal anuncia además un programa de créditos académicos de hasta USD 10,000 para estudiantes de posgrado, laboratorios e investigadores; la concesión depende de solicitud y elegibilidad, no está garantizada.
- Fuentes oficiales: https://modal.com/pricing

**Lightning AI**
- La página actual anuncia hasta 30 créditos gratuitos iniciales y hasta aproximadamente 80 horas GPU interrumpibles según hardware/consumo.
- La FAQ oficial indica que solicita número de teléfono para prevenir abuso. Además, para recibir los créditos adicionales hasta 30, la página explica que se debe añadir una tarjeta. Por la incidencia previa del usuario con verificación telefónica, no priorizar.
- Fuentes: https://lightning.ai/pricing ; https://support.lightning.ai/pricing/

**Hugging Face ZeroGPU**
- Proporciona GPU compartida para Spaces; la cuota gratuita indicada en su documentación es de 5 minutos GPU diarios para cuenta gratuita.
- No proporciona una VM o notebook libre para ejecutar entrenamientos largos; es útil para demos e inferencia breve, no para entrenar DeepLabV3+ o Mask R-CNN.
- Fuente oficial: https://huggingface.co/docs/hub/spaces-zerogpu

**Amazon SageMaker Studio Lab**
- Aunque históricamente fue gratuito y basado en JupyterLab, AWS indica actualmente que ya no acepta nuevos clientes. No considerarlo opción de alta nueva.
- Fuentes oficiales: https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lab.html ; https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lab-availability-change.html

### Herramientas open source para el flujo del proyecto

- JupyterHub/JupyterLab: interfaz notebook y administración multiusuario; JupyterHub es portable y open source, pero requiere infraestructura anfitriona. https://jupyter.org/hub
- PyTorch y Torchvision: frameworks para los modelos actuales.
- MLflow OSS: tracking de experimentos, métricas, artefactos y registro/versionado de modelos. https://mlflow.org/docs/latest/self-hosting/
- DVC: versionado y gestión de datos/artefactos separado de Git.
- Docker: entorno reproducible y portable.
- Estas herramientas no incluyen GPU gratuita; necesitan ejecutarse sobre Colab, Modal, una máquina universitaria o un servidor propio.

### Recomendación actualizada

1. Probar primero Google Colab Free como opción sin coste directo, adaptando scripts para ejecuciones cortas/reanudables y checkpoints persistentes. No intentar convertirlo en servidor SSH ni alojar un servicio web externo.
2. Solicitar, si se cumplen los requisitos, créditos académicos de Modal; es la vía más prometedora para ampliar cómputo sin desembolso inicial, aunque no es open source y el crédito no está garantizado.
3. Investigar acceso a GPU institucional/universitaria. Si se consigue, desplegar stack open source: JupyterHub, Docker, PyTorch, MLflow y DVC.
4. No recomendar ZeroGPU para entrenamientos largos, SageMaker Studio Lab para cuentas nuevas ni Lightning AI como primera opción por su verificación telefónica.
5. No se ha creado ninguna cuenta, iniciado sesión, desplegado recursos ni incurrido en gastos. No se ha ejecutado entrenamiento ni descargado datasets.

### Próximo paso

Preparar una adaptación del repositorio para Colab Free, con descarga remota autorizada de datos directamente en la sesión cloud, validación de dataset, checkpoints/reanudación, evaluación y exportación de resultados a almacenamiento persistente. Antes de implementar, revisar los scripts y requisitos reales del repositorio; no asumir que los datasets de Cityscapes o BDD100K están disponibles sin registro/licencia.


## 10. Preparación inicial del usuario para Google Colab Free — 2026-11-21

Se indicó al usuario que, antes de adaptar el repositorio, debe preparar desde Android:
1. Iniciar sesión en https://colab.research.google.com/ con una cuenta Google y crear un notebook vacío.
2. En Entorno de ejecución → Cambiar tipo de entorno de ejecución, seleccionar T4 GPU si está disponible; la asignación no está garantizada.
3. Autorizar la integración GitHub de Colab para leer el repositorio privado, utilizando la opción Include Private Repos si aparece y limitando permisos cuando la interfaz lo permita.
4. Crear en Google Drive la carpeta `ProcesamientoImagenes/resultados`, con subcarpetas para checkpoints, métricas, gráficas e informes.
5. Ejecutar únicamente pruebas de diagnóstico de GPU con `!nvidia-smi` y PyTorch `torch.cuda.is_available()`, sin descargar datasets ni iniciar entrenamiento.

### Restricciones explicadas
- Colab Free no garantiza GPU; sesiones de hasta 12 horas como máximo y límites dinámicos.
- Los datasets se descargarán directamente desde fuentes autorizadas a la máquina remota cuando se adapte el flujo, no al teléfono ni necesariamente a Drive.
- Drive se usará para persistir resultados/checkpoints, teniendo en cuenta cuota y límites de I/O.
- No compartir contraseñas ni tokens en el chat; no instalar dependencias ni ejecutar scripts del proyecto hasta verificar la cuenta, autorización GitHub y GPU.
- No se ha ejecutado ninguna acción de configuración en la cuenta del usuario ni entrenamiento.

### Punto de continuidad
Esperar a que el usuario complete los pasos de acceso, autorización y diagnóstico. Solicitar captura del resultado de `nvidia-smi` y del test PyTorch (ocultando correo/datos personales si aparecen). Después revisar el resultado y continuar con la adaptación específica del repositorio.


## 11. Aclaración sobre descarga de datasets con Colab Free — 2026-11-21

El usuario preguntó si debe descargar datasets al utilizar Colab Free, mientras estaba en el paso 5 de preparación de Google Drive.

Se aclaró:
- No necesita descargar datasets en Android ni subirlos manualmente a Drive.
- El diseño previsto descarga los datos directamente desde sus fuentes autorizadas a la máquina virtual de Colab.
- El almacenamiento local de la VM de Colab es temporal y los datasets pueden perderse al finalizar/desconectarse la sesión.
- Google Drive se propone para checkpoints, modelos, métricas, gráficas e informes; no es obligatorio guardar allí los datasets.
- Se adaptará el entrenamiento para checkpoints periódicos y reanudación. Según disponibilidad y límites, se puede re-descargar datos desde la nube o evaluar una caché remota persistente.
- Cityscapes y algunos recursos BDD100K pueden requerir registro, aceptación de licencia o credenciales. Colab no elimina esas condiciones.
- El usuario puede continuar con el paso 5 creando la carpeta de resultados; no debe descargar datasets ahora.
- No se han descargado datos ni ejecutado entrenamientos.

Punto de continuidad: completar preparación de cuenta, Drive y diagnóstico GPU/GitHub; luego diseñar la estrategia de acceso remoto a los datasets según los permisos y fuentes disponibles.


## 11. Adaptación inicial a Google Colab Free — 2026-11-21

El usuario confirmó que completó la preparación de Colab, Drive y autorización GitHub descrita en la intervención anterior, y autorizó comenzar la adaptación del repositorio. No se ha accedido a su sesión de Colab ni se han ejecutado celdas en su cuenta; el trabajo realizado es sobre el código del repositorio.

### Cambios guardados en `urban-models-and-benchmark`

- Se creó `notebooks/colab_free_urban_training.ipynb`:
  - Monta Google Drive y crea carpetas de resultados persistentes.
  - Clona la rama privada mediante token GitHub de solo lectura desde Colab Secrets (`GITHUB_TOKEN`) o entrada oculta de sesión.
  - Instala dependencias adicionales sin reinstalar PyTorch/Torchvision del runtime de Colab.
  - Diagnostica versiones de PyTorch/Torchvision, disponibilidad CUDA, GPU y estructura del dataset.
  - Mantiene el entrenamiento desactivado por defecto (`RUN_TRAINING = False)).
  - Expone configuración para entrenamiento semántico DeepLabV3+ y de instancias Mask R-CNN; BDD100K carriles queda pendiente de configurar rutas y validar fuente/particiones.
  - Almacena checkpoints e historiales en Drive; los datasets se prevén en disco temporal de Colab.
- Se creó `docs/COLAB_FREE.md` con instrucciones de acceso, token mínimo, almacenamiento, reanudación y límites del plan gratuito.
- Se actualizó README para señalar Colab Free como entorno remoto previsto y enlazar la guía/notebook. El texto de Kaggle histórico permanece como referencia de documentación antigua, pero ya no es el flujo recomendado.
- Se modificó `scripts/train_urban_segmentation.py`:
  - Guarda checkpoint de mejor mIoU para evaluación.
  - Guarda checkpoint reanudable `.last.pt` con modelo, optimizador, época e historial después de cada época.
  - Acepta `--resume` o ruta explícita de checkpoint.
  - `--epochs` representa el número total objetivo de épocas.
  - Escritura atómica de checkpoints.
- Se modificó `scripts/train_maskrcnn_cityscapes.py`:
  - Guarda estado reanudable de modelo, optimizador y scheduler al terminar cada época.
  - Conserva checkpoint compatible con evaluación/inferencia.
  - Acepta `--resume` o ruta explícita.
  - Actualiza historial JSON por época y escribe checkpoints atómicamente.

### Commits realizados

- `da12d12d175b44c929756ed9f497ce2c3f07c27e` — reanudación DeepLabV3+.
- `2cb6fc66d671e3a1e7efa3f88adcb83ef695bb06` — reanudación Mask R-CNN.
- `c11d3d38a02739b1bba76b9b8c9a06684aed3443` — notebook inicial Colab.
- `b8415e7391ae3ba753171c8aef6e7e02696a5e24` — guía Colab.
- `bfddafc70fdbfa24daf7800c9ba78bb028ee5b81` — actualización README.
- `8e3877b70cb35479c49f28fcdf39e701c1a543b7` — evita actualizar NumPy explícitamente en el notebook.
- `cb6b16773b2d55b7558a59500ced508f99176c20` — notebook con selector de entrenamiento semántico/instancias.

### Validaciones y límites

- Se comprobó que el notebook es JSON válido y contiene 17 celdas.
- GitHub Actions para el commit de Mask R-CNN `2cb6fc6` completó con conclusión `success`.
- La ejecución CI asociada al último commit del notebook `cb6b167` estaba en progreso en el momento de actualizar este registro; no declarar su resultado hasta consultarlo.
- No se ha ejecutado el notebook en la cuenta del usuario, no se ha confirmado GPU real de su sesión, no se ha descargado dataset, no se ha iniciado entrenamiento y no hay checkpoints experimentales.
- La descarga de Cityscapes no se automatiza: requiere comprobar registro, términos y mecanismo oficial de acceso. BDD100K comunitario sigue sin validación de procedencia/licencia/contenido.
- El entrenamiento de carriles BDD100K no se habilita todavía en el notebook; falta integrar la preparación y validación de sus anotaciones y splits.
- Colab puede interrumpir sesiones; los checkpoints se guardan al final de cada época y la reanudación no recupera el progreso a mitad de un lote.
- El notebook solicita un token de lectura del repositorio privado. El usuario debe guardarlo en Colab Secrets y no compartirlo en el chat. La integración OAuth de GitHub/Colab para abrir notebooks no equivale necesariamente a credenciales Git para `git clone`.

### Próximos pasos operativos

1. Abrir el notebook de Colab desde el enlace incluido en README o en `docs/COLAB_FREE.md`.
2. Ejecutar las celdas en orden hasta el diagnóstico; mantener `RUN_TRAINING=False`.
3. Confirmar que clona la rama correcta, monta Drive, importa Torch/Torchvision y detecta GPU CUDA.
4. Compartir la salida de diagnóstico sin tokens ni datos personales.
5. Confirmar acceso autorizado a Cityscapes o seleccionar dataset alternativo; después validar estructura y correspondencia de imágenes/anotaciones desde la VM cloud.
6. Hacer un smoke test de un lote pequeño antes de entrenamientos completos; verificar que los checkpoints se escriben en Drive y que `--resume` restaura estado.
7. Adaptar después el pipeline BDD100K de carriles y sus particiones por secuencia.

El usuario debe poder continuar desde Android; no solicitar descargas ni transferencias manuales de datasets desde el teléfono.


## 12. Primera ejecución del notebook Colab por el usuario — 2026-11-21

El usuario ejecutó el notebook `notebooks/colab_free_urban_training.ipynb` y compartió las salidas completas de las celdas iniciales y de diagnóstico.

### Resultados confirmados por la salida compartida

- Google Drive se montó correctamente en `/content/drive` y se crearon las carpetas de resultados.
- El repositorio privado se clonó correctamente en `/content/Procesamiento-de-Im-genes-`, en la rama `urban-models-and-benchmark`.
- El último commit mostrado por el clon fue `d0b62fa034249be9f4ecea739be8e559f495124e`, que coincide con el HEAD actual de la rama consultado en GitHub.
- La instalación de dependencias adicionales terminó sin error visible.
- `scripts/verify_setup.py` terminó con código de salida 0.
- El entorno reportó PyTorch `2.14.1+cpu`, Torchvision `0.29.1+cpu` y `torch.cuda.is_available() == False`; no se detectó GPU ni CUDA.
- Cityscapes no existe todavía en `/content/datasets/cityscapes`; BDD100K tampoco existe en `/content/datasets/bdd100k`.
- `RUN_TRAINING=False`; no se inició ningún entrenamiento ni se generaron checkpoints experimentales.

### Diagnóstico y decisión

La ejecución fue correcta como prueba de acceso, almacenamiento y verificación básica, pero la sesión actual es CPU-only. Esto no demuestra que Colab Free nunca pueda proporcionar GPU; significa que la sesión asignada al usuario no recibió una GPU o se inició con acelerador CPU.

### Próximos pasos operativos

1. En Colab, abrir **Entorno de ejecución → Cambiar tipo de entorno de ejecución**, seleccionar **T4 GPU** en Acelerador de hardware si está disponible y guardar.
2. El cambio de acelerador reinicia la máquina virtual: volver a ejecutar el notebook desde la primera celda para remontar Drive, clonar/actualizar el repositorio y reinstalar las dependencias.
3. Repetir el diagnóstico. Continuar solo si `torch.cuda.is_available()` devuelve `True` y `nvidia-smi` identifica una GPU. Si T4 GPU no aparece o Colab no la asigna, no insistir con entrenamiento; registrar la indisponibilidad y evaluar otra sesión/alternativa gratuita.
4. Mantener `RUN_TRAINING=False` hasta confirmar acceso autorizado a un dataset, verificar su estructura completa y realizar un smoke test pequeño.
5. No pedir al usuario que descargue datasets al teléfono ni que los suba manualmente.

### CI

Se consultó GitHub Actions: ejecución `44927072119` (run 138, workflow “Python tests”) finalizó con conclusión `success`. El resultado valida las pruebas automatizadas asociadas al commit `cb6b16773b2d55b7558a59500ced508f99176c20`; no representa una prueba de entrenamiento real ni de GPU/Colab.

### Estado al cierre

- Acceso al repo y Drive: confirmado.
- Verificación básica del proyecto: confirmada.
- CI: éxito.
- GPU CUDA en la sesión compartida: no disponible.
- Datasets: aún no disponibles en la VM.
- Entrenamiento y evaluación experimental: no iniciados.
- No se ha incurrido en gastos ni desplegado infraestructura de pago.


## 13. Segunda ejecución de Colab: GPU T4 disponible — 2026-11-21

El usuario volvió a ejecutar el notebook después de seleccionar un acelerador GPU en Colab y compartió las salidas.

### Resultados confirmados

- Drive montado correctamente en `/content/drive`; carpetas de resultados creadas.
- Repositorio privado actualizado/clonado correctamente en la rama `urban-models-and-benchmark`.
- El HEAD mostrado fue `0914fc7 docs: record first Colab runtime diagnostics`, correspondiente al registro anterior.
- Dependencias adicionales instaladas sin error visible.
- PyTorch `2.14.1+cu130`, Torchvision `0.29.1+cu130`.
- `torch.cuda.is_available() == True`.
- GPU asignada: NVIDIA Tesla T4, aproximadamente 14.56 GiB de VRAM (nvidia-smi muestra 15360 MiB).
- `nvidia-smi` identifica driver 580.82.07 y CUDA 13.0.
- `scripts/verify_setup.py` terminó con código de salida 0.
- Cityscapes sigue ausente en `/content/datasets/cityscapes`; BDD100K sigue ausente en `/content/datasets/bdd100k`.
- `RUN_TRAINING=False`; no se inició entrenamiento ni se generaron checkpoints.

### Diagnóstico

La asignación de GPU quedó resuelta en esta sesión: Colab Free entregó una T4 y el stack PyTorch/Torchvision ya reconoce CUDA. La sesión es adecuada para continuar con validación de datos y pruebas pequeñas, pero la GPU no garantiza persistencia ni disponibilidad en futuras sesiones.

### Próximos pasos

1. Mantener el entrenamiento desactivado.
2. Resolver el acceso autorizado a Cityscapes (registro/licencia y descarga directa desde la VM) o elegir un dataset alternativo cuya licencia y estructura sean compatibles.
3. Verificar la fuente, licencia, integridad, clases y particiones antes de utilizar cualquier copia de BDD100K.
4. Descargar/preparar los datos directamente desde la nube a `/content/datasets`, nunca al teléfono; confirmar espacio disponible y checksums.
5. Ejecutar validación de estructura y un smoke test pequeño; solo después planificar entrenamiento por etapas y persistencia de checkpoints en Drive.

### Estado al cierre

- GPU T4/CUDA: confirmada en la sesión compartida.
- Drive y repositorio privado: correctos.
- Verificación básica: correcta.
- CI del commit previo: éxito (run `44927072119`).
- Datasets: no disponibles.
- Entrenamiento/evaluación experimental: no iniciados.
- Costes: ninguno; no se desplegó infraestructura de pago.


## 14. Sustitución de Cityscapes por BDD100K — 2026-11-21

El usuario confirmó que no puede acceder a Cityscapes por no disponer de correo institucional y pidió adaptar el proyecto para prescindir de él, además de verificar BDD100K.
### Investigación verificada sobre BDD100K

- La documentación oficial del toolkit BDD100K identifica descargas oficiales para:
  - 100K Images (5.3 GB), usadas para detección, drivable area y lane marking.
  - 10K Images (1.1 GB), usadas para segmentación semántica, segmentación de instancias y panoptic.
  - Etiquetas de lane marking (434 MB), semantic segmentation (419 MB), instance segmentation (111 MB), drivable area (514 MB), y Detection 2020 Labels (53 MB).
- La documentación oficial especifica 19 clases semánticas, 10 clases de detección y las primeras 8 clases para segmentación de instancias; lane marking tiene subcategorías de tipo, dirección y estilo. Los formatos de instancias usan bitmasks RGBA; los JSON de polígonos usan curvas Bezier y no deben tratarse como polígonos COCO sin conversión.
- Importante: el conjunto 10K no es simplemente un subconjunto exacto del conjunto 100K. Para segmentación semántica/instancias deben emparejarse las imágenes 10K con sus etiquetas correspondientes; para carriles/detección se usan las imágenes 100K.
- La licencia de datos oficial permite uso, copia, modificación y distribución con fines educativos, de investigación y sin ánimo de lucro, siempre que se conserve el aviso completo de copyright/licencia y descargo de responsabilidad. El uso comercial queda restringido a miembros/afiliados BDD/BAIR o requiere licencia comercial de UC Berkeley. La licencia BSD-3-Clause del repositorio de código NO es la licencia de las imágenes/anotaciones.
- Fuentes consultadas:
  - https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst
  - https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst
  - https://github.com/bdd100k/bdd100k/blob/master/doc/source/license.rst
  - https://github.com/bdd100k/bdd100k
- La copia de Hugging Face https://huggingface.co/datasets/liqijia/BDD100K-Semantic-Segmentation se declara explícitamente no oficial; su tarjeta afirma que redistribuye el subset oficial de segmentación semántica de 10K, con 7,000 train y 1,000 validation (8,000 ejemplos etiquetados) y sin test con máscaras públicas. Afirma que no modifica píxeles y que conserva la licencia BDD100K. No se inspeccionaron ni descargaron todos los shards ni se verificaron checksums/contenido binario en esta intervención: por tanto, la procedencia declarada está documentada, pero la integridad real del mirror sigue pendiente de validación en Colab. No usarlo como fuente para instancias/carriles/detección.
- La documentación oficial indica el mirror de descarga https://dl.cv.ethz.ch/bdd100k/data/ y el portal oficial https://bdd-data.berkeley.edu/. El mirror oficial puede ser la fuente preferida desde la VM cloud, tras revisar la licencia y disponibilidad.

### Auditoría de compatibilidad del código existente

- Se confirmó leyendo el README, notebook Colab, guía Colab, protocolo experimental y scripts que:
  - DeepLabV3+ solo ofrece tareas `cityscapes` (11 clases) y `lanes` (binaria); no existe loader de semántica BDD100K.
  - Mask R-CNN depende de `CityscapesInstanceDataset` y de un mapa fijo de 7 clases; no admite todavía máscaras de instancias BDD100K.
  - El preparador de carriles `scripts/prepare_bdd100k_lane_masks.py` rasteriza polilíneas como líneas binarias, pero su docstring/implementación esperan `poly2d.vertices`; el formato oficial describe curvas Bezier, por lo que hay que contrastar el JSON real y el parser oficial antes de darlo por correcto.
  - El notebook Colab solo declara rutas Cityscapes y BDD100K genéricas, no descarga ni valida los componentes específicos del dataset.
  - El README y protocolo siguen describiendo Cityscapes como dataset semántico/de instancias principal.
- No se aplicó todavía una adaptación parcial del entrenamiento: cambiar únicamente el número de clases o rutas sería incorrecto. La adaptación debe incluir loaders, mapeos de clases/ignore=255, formatos de máscaras semánticas y RGBA de instancias, evaluadores, configuración del notebook y documentación.
- No se descargaron datos, no se ejecutaron entrenamientos y no se generaron checkpoints en esta intervención.

### Decisión recomendada y siguiente fase

- Retirar Cityscapes como requisito del proyecto.
- Adoptar BDD100K como dataset principal con estas rutas de tarea:
  1. Semantic segmentation: 10K images + semantic segmentation masks; 19 clases, ignore 255.
  2. Instance segmentation: 10K images + instance segmentation bitmasks; 8 categorías evaluadas (primeras 8 de las 10 clases de detección).
  3. Object detection: 100K images + Detection 2020 Labels; 10 categorías.
  4. Lane marking: 100K images + lane marking labels; preservar categoría/dirección/estilo en vez de colapsar a una máscara binaria en la versión final.
- La implementación debe ser por fases: validación automatizada de dataset y splits; loader semántico y DeepLabV3+ BDD; loader RGBA de instancias y Mask R-CNN; actualización de evaluación/benchmark; carriles multiatributo; notebook Colab con descarga remota oficial y comprobaciones MD5.
- Hasta completar y probar esa migración, no afirmar que el proyecto ya es independiente de Cityscapes ni habilitar RUN_TRAINING.


## 15. Aclaración sobre descarga necesaria para analizar BDD100K — 2026-11-21

El usuario preguntó si debe descargar BDD100K para que se pueda analizar el dataset.

### Respuesta y decisión operativa

- No necesita descargar BDD100K completo ni transferir archivos al teléfono.
- La auditoría de arquitectura, loaders, anotaciones documentadas, licencias, formatos, clases y adaptación del código puede continuar sin descargar el dataset.
- Para validar empíricamente los formatos reales, correspondencia de nombres, máscaras y parser sí necesitaremos inspeccionar archivos de muestra. Se obtendrán directamente desde una fuente autorizada a la VM temporal de Google Colab, no al dispositivo del usuario.
- Primero se implementará/ejecutará una inspección ligera de metadatos y estructura; después se descargará solo el mínimo subconjunto necesario para pruebas de lectura y visualización. La descarga completa se decidirá únicamente cuando los loaders superen esos smoke tests.
- Se mantiene el acuerdo: Colab T4 como entorno remoto disponible cuando el usuario lo inicie; Google Drive para resultados/checkpoints, no para datasets masivos; entrenamiento desactivado; PR #3 sin fusionar.
- No se ha descargado ningún archivo BDD100K en esta intervención.

### Estado

La migración Cityscapes → BDD100K sigue planificada y no debe considerarse implementada todavía. El próximo trabajo técnico es inspeccionar y adaptar código/formato en el repositorio, y preparar una celda de Colab para validación de muestras remotas.


## 16. Confirmación de continuidad: análisis BDD100K sin descarga local — 2026-11-21

Se volvió a leer el registro completo antes de responder. Se confirma que el usuario trabaja desde Android, no puede descargar datasets al teléfono por falta de espacio/conexión, ya dispone de una sesión Colab Free que detectó una Tesla T4, Drive funciona y el PR #3 debe permanecer abierto/sin fusionar.

Aclaración operativa:
- No hace falta descargar el dataset completo para continuar la auditoría de código, documentación oficial, clases, formatos, licencia y diseño de loaders.
- Para comprobar compatibilidad real de los parsers se requerirán muestras pequeñas descargadas directamente desde una fuente autorizada a `/content` en Colab. No deben pasar por el teléfono ni subirse a Drive.
- La descarga completa se pospone hasta que las muestras validen loaders y conversiones. Los checkpoints y resultados sí se conservan en Drive.
- No se ha descargado ningún archivo BDD100K ni se ha iniciado entrenamiento en esta intervención.


## 10. Migración inicial de loaders y flujo Colab a BDD100K — 2026-11-21

El usuario autorizó implementar la adaptación a BDD100K como dataset principal, manteniendo la ejecución remota y sin descargas al teléfono.

### Decisiones de datos confirmadas con documentación oficial

- BDD100K 10K images se utiliza para semántica e instancias; tiene splits train/val/test y no es necesariamente subconjunto exacto de 100K images.
- Semantic masks: PNG monocanal de 8 bits, train IDs 0–18 y 255 para ignore.
- Instance bitmasks: PNG RGBA; R almacena category ID (1–8), G atributos (ignore/crowd en bits menos significativos) y B el ann_id para instance segmentation. A se reserva para segmentation tracking.
- Semantic classes (19): road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle, bicycle.
- Instance classes (8): pedestrian, rider, car, truck, bus, train, motorcycle, bicycle.
- Fuentes oficiales consultadas:
  - https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst
  - https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst
  - Mirror documentado: https://dl.cv.ethz.ch/bdd100k/data/

### Cambios guardados en `urban-models-and-benchmark`

- Añadido `src/utils/bdd100k_dataset.py`:
  - `BDD100KSemanticDataset`: empareja imágenes y máscaras por nombre, valida IDs y conserva 255.
  - `BDD100KInstanceDataset`: decodifica bitmasks RGBA, crea masks/boxes/labels para Mask R-CNN y descarta flags crowd/ignore.
  - Normalización de imagen consistente con ImageNet.
- Añadido `tests/test_bdd100k_dataset.py` con fixtures sintéticos para IDs semánticos, ignore, decodificación RGBA y máscaras faltantes.
- Actualizado `scripts/train_urban_segmentation.py` para `--task bdd100k-semantic` (19 clases).
- Actualizado `scripts/train_maskrcnn_cityscapes.py` con `--dataset bdd100k`, rutas de train/val y metadatos de ocho clases en checkpoints. Se conserva el nombre histórico del script por compatibilidad.
- Actualizado `scripts/evaluate_cityscapes.py` con `--task bdd100k-semantic` y mIoU/IoU por clase. La evaluación de instancias BDD100K todavía no está implementada.
- Actualizado README, protocolo experimental, guía Colab y notebook para usar rutas BDD100K 10K en tareas semántica e instancias. El notebook sigue con `RUN_TRAINING=False` y valida los archivos sin descargarlos automáticamente.
- Commits principales de esta fase: `3ddaa864`, `3c5e243`, `58d6f1a`, `91d1a9a`, `a10edfc`, `a92937a`, `7e6d98f`, `4e13bf9`, `5e64482`, `cab1cb5`, `183f954`, `35f1154`, `db73e69`, `69f6297`, `2a6d312`.

### Validación y límites actuales

- Se añadieron pruebas unitarias, pero **no se han ejecutado** en un entorno Python ni en GitHub Actions durante esta intervención. El estado vacío de checks consultado no equivale a pruebas aprobadas.
- No se descargó BDD100K, no se ejecutó entrenamiento y no se generaron checkpoints ni métricas.
- No se ha implementado aún la descarga automática directa y verificable del mirror a `/content`; no se inventaron URLs de archivos.
- Pendiente completar:
  1. Adaptador/entrenador/evaluador de detección 2D con 100K images y Detection 2020 Labels (10 clases).
  2. Carriles oficiales con sus tres subtareas (categoría, dirección y estilo); el parser existente de `poly2d` no se debe considerar correcto para Bezier hasta corregirlo y probarlo. Preferir las máscaras oficiales o el convertidor oficial BDD100K.
  3. Evaluación de instancias BDD100K (box AP y mask AP) y validación de checkpoint.
  4. Descarga remota reproducible: archivos exactos, checksum MD5, integridad de splits y espacio temporal.
  5. Smoke tests sintéticos y pruebas en Colab T4 antes de habilitar `RUN_TRAINING`.
- Cityscapes queda como compatibilidad heredada; no es requisito del flujo BDD100K.
- PR #3 debe permanecer abierto y sin fusionar. No se ha solicitado ni realizado merge.


### Actualización de cierre de la intervención

- Se corrigió el checkpoint público de Mask R-CNN para guardar los nombres/número de clases dinámicos del dataset BDD100K (no los metadatos heredados de Cityscapes).
- Se corrigió el fixture sintético de instancias para reflejar que el canal B contiene `ann_id` para instance segmentation; el canal A se reserva para tracking.
- Se generalizó el mensaje de validación del entrenador Mask R-CNN.
- Se actualizó el notebook para comprobar presencia de imágenes 10K y máscaras semánticas/bitmasks por split, y para seleccionar entrenamiento semántico o de instancias. El notebook sigue sin descargar datos ni iniciar entrenamiento automáticamente.
- Se ajustaron README, protocolo experimental y guía Colab para dejar claro que carriles multiatributo, detección 2D, evaluación de instancias y descarga automática reproducible siguen pendientes. Se marcó como no validado el conversor antiguo de carriles basado en vértices simples.
- Últimos commits documentales/correctivos de esta continuación: `7976e6e`, `f64548f`, `ab208da`, `fb695bf`.
- No se ejecutaron pruebas Python ni GitHub Actions; los tests añadidos permanecen pendientes de ejecución. No afirmar que el código está validado.


- Último ajuste de protocolo: se retiraron los comandos antiguos de entrenamiento/evaluación binaria de carriles, porque no respetaban las tres subtareas oficiales BDD100K; commit `e03ac62`.

- Se añadió al notebook una celda para ejecutar `pytest -q tests/test_bdd100k_dataset.py` y los smoke checks `--help` de ambos entrenadores antes de cualquier descarga/entrenamiento. La celda está preparada, pero todavía no se ha ejecutado. Commit `2f6ba43`.



## 17. Auditoría técnica de continuidad — 2026-11-21

El usuario autorizó realizar la auditoría de la rama, comprobar las implementaciones y ejecutar las pruebas antes de continuar con el desarrollo.

### Archivos inspeccionados directamente en GitHub

- `src/utils/bdd100k_dataset.py`
- `tests/test_bdd100k_dataset.py`
- `scripts/train_urban_segmentation.py`
- `scripts/train_maskrcnn_cityscapes.py`
- `scripts/evaluate_cityscapes.py`
- `scripts/prepare_bdd100k_lane_masks.py`
- `notebooks/colab_free_urban_training.ipynb`
- `docs/COLAB_FREE.md`
- `requirements.txt`
- `README.md`
- Workflow `.github/workflows/tests.yml`

### Hallazgos confirmados por inspección estática

1. **Loader semántico:** existe y valida IDs 0–18/255 y emparejamiento por nombre. No se ha probado aún con archivos oficiales reales.
2. **Loader de instancias:** existe y construye targets de Mask R-CNN a partir de PNG RGBA. La decodificación y los flags requieren contraste con máscaras oficiales reales; no se debe dar por validada solo por el fixture sintético.
3. **Entrenador semántico:** acepta BDD100K 19 clases, pero conserva Cityscapes como tarea predeterminada. La ruta BDD100K requiere rutas explícitas de train/val. El checkpoint best no contiene estado del optimizador, mientras que el .last sí.
4. **Entrenador Mask R-CNN:** acepta BDD100K y ocho categorías. Crea un DataLoader de validación indirectamente solo como dataset; el entrenamiento no calcula pérdida ni métricas de validación. No se debe describir como entrenamiento con validación completa.
5. **Evaluador:** BDD100K semántico calcula mIoU/IoU por clase. La rama de instancias sigue usando Cityscapes y AP de cajas estilo VOC; no evalúa BDD100K ni mask AP.
6. **Carriles:** `scripts/prepare_bdd100k_lane_masks.py` espera `poly2d.vertices`, rasteriza una máscara binaria y no representa las tres subtareas oficiales. Mantener este conversor bloqueado/no validado.
7. **Notebook:** las celdas de prueba ejecutan pytest y `--help`, pero el notebook no implementa descarga ni verificación MD5 automática. `RUN_TRAINING=False` se mantiene correctamente.
8. **CI:** `.github/workflows/tests.yml` ejecuta compileall, smoke tests de CLI y pytest en push a `urban-models-and-benchmark`; por tanto, un commit documental en esta rama debe iniciar una ejecución de CI. El workflow instala PyTorch CPU y no valida CUDA/T4 ni datasets reales.
9. **Documentación:** README/guía Colab describen explícitamente las limitaciones de detección, carriles y evaluación de instancias; el registro se mantiene como fuente de continuidad.

### Límites de esta auditoría

- La lectura de archivos confirma presencia y lógica estática, no ejecución.
- En esta intervención todavía no se ha ejecutado pytest, compileall ni los smoke tests. Se actualizará este apartado con el resultado real de CI cuando esté disponible.
- No se descargó BDD100K, no se usó la T4, no se entrenaron modelos ni se generaron checkpoints.
- No se modificó código de entrenamiento ni se activó `RUN_TRAINING`.
- PR #3 debe permanecer abierto y sin fusionar.
- Próxima acción: provocar/observar CI de esta rama y revisar los logs; corregir fallos comprobados antes de implementar detección/carriles/AP de instancias.


### Hallazgos adicionales de compatibilidad y estado de CI

10. **Normalización de imágenes para Mask R-CNN:** el loader BDD100K reutiliza `_image_tensor`, que normaliza con media/desviación ImageNet. El loader Cityscapes de instancias entrega tensores en [0,1] y Torchvision Mask R-CNN aplica su propia normalización interna. Por tanto, la ruta BDD100K normaliza dos veces y no es compatible con el contrato esperado del modelo. Corregir separando el preprocesamiento semántico del de instancias y añadir una aserción de rango.
11. **Evaluación BDD100K de instancias:** el evaluador actual no solo carece de mask AP; su wrapper `InstanceSegmentationModel` construye un predictor de 8 salidas (background + 7 clases Cityscapes), mientras que el entrenador BDD100K guarda 9 salidas (background + 8 clases). No se puede cargar directamente ese checkpoint con el wrapper actual. Debe implementarse evaluador específico BDD100K que respete nombres/IDs y calcule box AP y mask AP.
12. **Validación durante entrenamiento de Mask R-CNN:** el script construye el dataset de validación y reporta su tamaño, pero no ejecuta evaluación ni calcula pérdida/metricas sobre ese split durante las épocas. La validación está diferida a un evaluador posterior aún no compatible con BDD100K.
13. **Pruebas:** el test sintético de instancias verifica forma/labels/boxes, pero no comprueba rango de imagen, múltiples instancias con IDs repetidos, casos de borde de flags ni equivalencia con la conversión oficial BDD100K.
14. **CI del commit de auditoría `a9403414b61ff96987a4e6a2bff65475b1a9bac4`:** ejecución GitHub Actions `44945437399` se inició por push y, al registrar esta actualización, seguía `in_progress` en el paso “Install CPU PyTorch”. Todavía no hay conclusión de compileall/CLI/pytest. Enlace: https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44945437399.
15. La ejecución CI previa `44944986268` reportó `success` para el commit de PR anterior; no sustituye el resultado del commit actual ni demuestra compatibilidad con BDD100K real o GPU.

### Cierre de auditoría de esta intervención

- Se completó auditoría estática de loaders, entrenadores, evaluador, conversor de carriles, notebook, guía, README, dependencias y workflow.
- Se disparó CI mediante un commit documental. No se afirma que las pruebas hayan pasado mientras la ejecución siga en curso.
- No se corrigió código en esta intervención; el propósito fue auditar y verificar sin introducir cambios funcionales no probados.
- No se descargaron datasets, no se inició entrenamiento ni se generaron checkpoints.
- PR #3 permanece abierto; no se realizó merge.
- Prioridad de corrección: (1) normalización de BDD100K Mask R-CNN y pruebas, (2) evaluación BDD100K box/mask AP con 9 clases, (3) validador y adaptador de carriles con bitmask empaquetado/Bezier usando toolkit oficial, (4) adaptador de detección 2D y su evaluación, (5) descarga remota exacta con MD5 y validación de estructura.


## 18. Correcciones BDD100K — 2026-11-21

El usuario autorizó corregir los problemas detectados en la auditoría. Los cambios se realizaron directamente en la rama `urban-models-and-benchmark`, que alimenta el PR #3. El PR permanece abierto y sin fusionar.

### Correcciones implementadas

1. **Contrato de imágenes de Mask R-CNN:** `_image_tensor` ahora admite normalización opcional. Los loaders semánticos mantienen normalización ImageNet; los loaders de instancias y detección devuelven RGB CHW float32 en [0,1] para que Torchvision aplique su normalización interna.
2. **Pruebas de preprocesamiento:** se añadieron pruebas para verificar rango [0,1] en instancias/detección y normalización ImageNet en semántica.
3. **Evaluación BDD100K de instancias:** `scripts/evaluate_cityscapes.py --task bdd100k-instance` construye Mask R-CNN con nueve salidas (fondo + ocho clases), valida los metadatos del checkpoint y calcula Box AP y Mask AP por clase en umbrales 0.50–0.95, incluyendo AP50 y AP75.
4. **Métrica Mask AP:** se añadió `compute_mask_average_precision_per_image` con matching greedy uno-a-uno por imagen e interpolación precision-recall. El informe declara expresamente que el protocolo es interno y no equivale a COCOeval oficial.
5. **Memoria del evaluador:** máscaras de predicción/GT se almacenan con `np.packbits`; se limita la salida a 50 detecciones por imagen y score mínimo 0.05 para reducir uso de RAM en Colab.
6. **Detector BDD100K:** se añadió `BDD100KDetectionDataset`, que lee `det_20` JSON, escala `box2d` y usa el orden oficial de diez categorías: bike, bus, car, motor, person, rider, traffic light, traffic sign, train, truck. Se añadió `scripts/train_bdd100k_detection.py` con Faster R-CNN, Box AP50 de validación y checkpoints reanudables.
7. **Carriles BDD100K:** se añadió `BDD100KLaneDataset` para decodificar los PNG monocanal oficiales: bits 0–2 categoría, bit 3 fondo, bit 4 estilo y bit 5 dirección. Se añadió `scripts/train_bdd100k_lanes.py` con una red DeepLabV3 de tres cabezas (8 categorías, 2 direcciones y 2 estilos), ignore index 255, mIoU por subtarea y checkpoints reanudables.
8. **Conversor antiguo de carriles:** `scripts/prepare_bdd100k_lane_masks.py` se marcó como obsoleto; su salida binaria pierde atributos y no se debe usar para entrenamiento ni métricas BDD100K.
9. **Entrenadores por defecto:** `train_urban_segmentation.py` ahora selecciona BDD100K semántico por defecto; `train_maskrcnn_cityscapes.py` selecciona BDD100K por defecto. El modo binario de carriles del entrenador antiguo rechaza la ejecución y dirige al nuevo entrenador multi-tarea.
10. **Inferencia de instancias:** `src/models/instance_seg.py` ahora lee `num_classes` y `class_names` del checkpoint, construye cabezas con el número correcto de clases y reconoce el label space BDD100K de instancias.
11. **CI/documentación:** el workflow añade smoke tests CLI para los nuevos entrenadores; README y protocolo experimental describen rutas, clases, comandos y límites de las métricas.
12. **Pruebas nuevas:** se añadieron fixtures para rango de imágenes, detección 2D, decodificación de los tres atributos de carriles, AP de máscaras y máscaras compactadas.

### Fallos detectados y correcciones de pruebas

- CI de commit `21b5dfb68cbfde8ba20f9a502d7db598e70519ac` completó instalación, compileall y smoke tests, pero pytest falló en dos expectativas incorrectas del test: un test suponía que una imagen gris de valor 128 debía tener algún canal normalizado negativo, y otro esperaba que el valor 255 no fuera background pese a que el bit 3 está activado.
- Se corrigió el test semántico para comparar los valores normalizados esperados por canal y el test de carriles para tratar 255 como fondo/ignore en las tres salidas.
- Los fallos de ejecución CI anteriores son evidencia de que pytest se ejecutó y encontró esos errores de fixtures; no deben contarse como pruebas aprobadas.

### Commits principales de esta fase

- `51abdf7`: corregir normalización del loader de instancias.
- `d3a1f8b`: añadir métrica Mask AP.
- `bb9265a`: añadir evaluador BDD100K Box AP/Mask AP.
- `a073913`: añadir loader de detección 2D.
- `f202b72`: añadir entrenador Faster R-CNN BDD100K.
- `218d8a2`: añadir loader de carriles y corregir clases de detección oficiales.
- `21b5dfb`: añadir entrenador multi-cabeza de carriles.
- `e24eb7e` y `1339ac4`: compactar máscaras para evaluación.
- `54e2d0e` y `d803b94`: añadir reanudación de entrenadores de detección/carriles.
- `bb10f02` y `92f3eb7`: establecer BDD100K como tarea por defecto.
- `9cf95cd` y `2548d6a`: hacer que inferencia cargue checkpoints BDD100K.
- `f1d1601`: corregir expectativas de pruebas de carriles.
- `ab64273`, `743c2c1`: actualizar protocolo y README.

### Estado de validación al cierre de esta actualización

- La CI del commit `f1d16010249ce8907631b84bcdf3f996da3162d0` seguía en ejecución en la etapa de instalación de dependencias al consultar su estado; todavía no había conclusión de pytest.
- La CI de commits posteriores también está en curso. Debe comprobarse la ejecución correspondiente al HEAD final, no asumir que los workflows de commits intermedios validan los cambios posteriores.
- No se ejecutó entrenamiento ni inferencia con BDD100K real.
- No se descargó ningún dataset ni se consumió la T4 de Colab.
- Las pruebas sintéticas no sustituyen la validación con máscaras/JSON oficiales reales.
- El evaluador Mask AP propio no sustituye COCOeval/BDD100K oficial.
- La precisión de carriles debe contrastarse con el evaluador oficial de F1 boundary (pix1/pix2/pix5); el entrenador actual registra mIoU por cabeza, no el F1 oficial.
- La validación de detección es Box AP50 propio; no equivale a COCO mAP oficial.
- PR #3 permanece abierto y sin fusionar.

### Próximos pasos obligatorios

1. Esperar y revisar la CI del HEAD final; corregir cualquier fallo.
2. Ejecutar smoke tests y loaders con muestras oficiales pequeñas en Colab.
3. Contrastar decoder de instancias, mapeos de clases y decoder lane bitfield con los paquetes oficiales y evaluadores oficiales.
4. Añadir reanudación al entrenador semántico/Mask R-CNN si se detecta que no cubre los casos de interrupción del usuario.
5. Solo tras validación real de los loaders, activar descarga remota mínima y luego entrenamiento.


### Corrección crítica adicional: layout RGBA de instancias BDD100K

La revisión directa del convertidor oficial `bdd100k/label/to_mask.py` detectó un error en la descripción/decodificación anterior del canal de instancia:

- R: category ID.
- G: flags; bit 0 = ignored, bit 1 = crowd, bit 2 = occluded, bit 3 = truncated.
- B: byte alto del annotation ID.
- A: byte bajo del annotation ID.

El loader anterior leía solo B como ID y asumía que A estaba reservado para tracking. Eso era incorrecto para las máscaras oficiales de instance segmentation. Se corrigió a `ann_id = (B << 8) | A` y se añadió un fixture con IDs 1 y 257 para verificar ambos bytes. La exclusión de crowd/ignore usa los bits bajos 0 y 1 de G.

Fuente oficial contrastada: https://github.com/bdd100k/bdd100k/blob/master/bdd100k/label/to_mask.py (función `set_instance_color`, que serializa `ann_id >> 8` en B y `ann_id & 255` en A).

### Resultado de pruebas intermedio

- GitHub Actions run `44946190235`, commit `f1d16010249ce8907631b84bcdf3f996da3162d0`: instalación, compileall, smoke tests CLI y `pytest -q` finalizaron correctamente; **32 pruebas aprobadas**.
- Ese commit es anterior a la corrección RGBA de 16 bits. La CI de los commits posteriores que contienen esa corrección debe finalizar antes de considerar validado el HEAD actual.


## Validación CI del HEAD 896a69c (21-11-2026)

- GitHub Actions run **44946350480** terminó con estado `completed` y conclusión **`success`** para la rama `urban-models-and-benchmark`, cuyo HEAD es `896a69c468cb24b78eacba19cf2418b51307ebaa`.
- La ejecución corresponde al evento `pull_request` de la PR #3; GitHub ejecutó el merge ref `6a73cad568251a428d9d02b6afa259a41eff3ac4`, que integra el HEAD anterior con la rama base.
- Pasos completados correctamente: instalación de PyTorch CPU y dependencias, `compileall`, smoke tests de CLI de entrenamiento/evaluación/preparación y `scripts/verify_setup.py`.
- **Pytest: 32 passed en 11.17 s**, confirmado en los logs del job `136974414656`.
- `scripts/verify_setup.py` reportó `pycocotools` como dependencia opcional ausente y dataset no descargado; no impidió la CI. No se validaron muestras reales ni se ejecutó entrenamiento.
- PR #3 continúa **abierta**, en borrador y sin fusionar.
- Próximo paso: iniciar validación remota acotada con muestras oficiales BDD100K en Colab, verificando estructura, loaders y decodificación antes de cualquier entrenamiento.


## 19. Inicio de validación con muestras reales BDD100K — 2026-11-21

El usuario autorizó comenzar las validaciones. Se mantuvieron las restricciones: no descargar datos en el teléfono, no obtener el dataset completo en esta fase, no iniciar entrenamiento y conservar la PR #3 abierta.

### Fuente de muestra seleccionada

- Se revisó la documentación oficial BDD100K: el paquete 10K Images (1.1 GB, MD5 `08f26aecceda982568063d3d5873378e`) y los paquetes de etiquetas semánticas (419 MB, MD5 `9a2968dde3345eeb689cffb1e26f9c78`), instancias (111 MB, MD5 `651b41f229d7327d8c4af97772de4390`), carriles (434 MB, MD5 `dfe74f9ed6800765a0047414d620a186`) y Detection 2020 Labels (53 MB, MD5 `b86a3e1b7edbcad421b7dad2b3987c94`). La documentación indica que 10K Images se usa para semántica/instancias y 100K Images para detección/carriles.
- Para no descargar paquetes completos, se seleccionó provisionalmente `liqijia/BDD100K-Semantic-Segmentation` en Hugging Face. Su tarjeta declara que redistribuye los JPEG y máscaras trainId sin modificar desde la publicación oficial, pero es un mirror de terceros y no se considera prueba independiente de procedencia.
- Esta fuente permite validar solo el cargador semántico. No se encontró/confirmó una fuente equivalente fiable de muestras oficiales para bitmasks de instancias, JSON det_20 o máscaras lane en esta intervención.

### Cambios añadidos a la rama

- Nuevo `scripts/validate_bdd100k_semantic_sample.py`:
  - Recupera por API de Hugging Face solo dos pares imagen/máscara de train y dos de validación por defecto; permite 1–8 por split.
  - Valida RGB, máscara monocanal, dimensiones coincidentes e IDs 0–18/255.
  - Ejecuta `BDD100KSemanticDataset` con resize 256x512 y comprueba formas, dtype e IDs resultantes.
  - Usa directorio temporal y elimina las muestras al finalizar.
- Nuevo workflow `.github/workflows/validate-bdd100k-sample.yml` con ejecución automática/manual.
- `.github/workflows/tests.yml` incorpora el smoke test de muestras reales después de la suite sintética.
- Notebook `notebooks/colab_free_urban_training.ipynb` incorpora sección 5.2 para ejecutar la validación en Colab.
- `docs/COLAB_FREE.md` documenta el alcance y las limitaciones.
- Commits de esta fase:
  - `3ddf0c9`: script de validación semántica con muestras reales.
  - `4fbcc7d`: workflow dedicado de muestras.
  - `3fdef5f`: integración del smoke test real en CI.
  - `ccffb96`: sección de validación en notebook.
  - `23c7198`: documentación Colab.
- HEAD actual comprobado tras los cambios: `23c7198f5a03a4bc47b7f5c8fcde0ed0edd41070`.

### Estado de ejecución

- GitHub Actions ejecuta las validaciones automatizadas. Al registrar esta actualización, el workflow dedicado `44947969722` estaba instalando PyTorch CPU/dependencias y todavía no había iniciado la descarga de muestras.
- El workflow general de CI del commit `ccffb96`, run `44948002621`, también estaba en curso; la etapa de validación de muestras reales aún estaba pendiente.
- Runs anteriores para commits intermedios también estaban en cola/en ejecución; sus resultados no sustituyen al check del HEAD más reciente.
- No se afirma todavía que el loader semántico haya pasado con archivos reales. No se han validado loaders de instancias, detección ni carriles con datos reales.
- No se inició entrenamiento, no se generaron checkpoints y no se descargó el dataset completo.
- PR #3 permanece abierta, en borrador y sin fusionar.

### Próximos pasos

1. Revisar logs y conclusión del workflow dedicado y del CI general; corregir fallos reales si aparecen.
2. Si el mirror HF valida correctamente el loader semántico, registrar el resultado como validación provisional de esa tarea.
3. Preparar acceso remoto acotado a paquetes oficiales de instancias, detección y carriles. Antes de descargarlos, confirmar nombres, checksums y mecanismo para extraer muestras pequeñas sin descargar el archivo completo; si no es posible, informar con claridad.
4. Solo después de validar loaders reales y confirmar disponibilidad de GPU, considerar entrenamiento; mantener `RUN_TRAINING=False` hasta entonces.


### Incidencia de la primera ejecución real y diagnóstico — 2026-11-21

- El primer run dedicado `44947969722` (commit `4fbcc7d`) instaló correctamente PyTorch CPU y `huggingface_hub`, pero falló antes de descargar imágenes: `HfApi.list_repo_files` no encontró rutas que coincidieran con el prefijo `data/images/train/` supuesto por el script.
- Este fallo es del adaptador de acceso al mirror; **no es un fallo del loader semántico**, que aún no llegó a ejecutarse con datos reales.
- Se modificó `scripts/validate_bdd100k_semantic_sample.py` para imprimir el listado inicial y candidatos de archivos cuando la estructura no coincide. Commit `04cc5b9`.
- El nuevo run dedicado `44948056735` (commit `04cc5b9`) se encontraba en instalación de dependencias, todavía sin ejecutar la validación, al momento de registrar esta incidencia.
- La CI general de commits recientes también estaba en curso. Se debe consultar el run de la cabeza actual y leer el diagnóstico del script antes de elegir otra ruta.
- No se descargó ninguna imagen de muestra en el primer intento, no se inició entrenamiento y no se generaron checkpoints.


### Corrección del layout real del mirror semántico — 2026-11-21

- Los logs de los runs dedicados `44948056735` y de CI general `44948060450` confirmaron que `HfApi.list_repo_files` funciona y lista archivos, pero la prueba fallaba porque el script exigía `metadata.jsonl` bajo `data/images/{split}`. Las 32 pruebas sintéticas pasaron antes de ese paso; el loader semántico todavía no había procesado muestras reales.
- Se inspeccionó el árbol de archivos público del repositorio `dronefreak/BDD100K-Semantic-Segmentation`. El layout real actual conserva los archivos originales separados:
  - imágenes: `data/images_10k/10k/{train,val}/shard_*/<id>.jpg`;
  - máscaras: `data/seg_maps/labels/{train,val}/shard_*/<id>_train_id.png`.
- El repositorio `liqijia/...` usado inicialmente es una duplicación cuyo árbol observado no coincidía con el README ni con el layout esperado por el validador. Se cambió el origen predeterminado al repositorio `dronefreak/...`, cuya estructura de archivos se inspeccionó directamente.
- Se reescribió `scripts/validate_bdd100k_semantic_sample.py` para listar archivos, emparejar imagen y máscara por identificador y descargar exclusivamente dos pares por split. Ya no requiere ni descarga `metadata.jsonl`. Comprueba modo RGB, máscara monocanal, dimensiones iguales, IDs 0–18/255 y ejecuta `BDD100KSemanticDataset` a 256x512.
- Se actualizó `docs/COLAB_FREE.md` y la sección 5.2 del notebook para documentar el layout y el origen nuevos.
- Commit de corrección del script: `564dff9350d07acbe4daf687a2328ab3551c91ad`. Los cambios de documentación y este registro se guardan en commits posteriores de la misma rama.
- **Validación pendiente:** el cambio se debe ejecutar en GitHub Actions. Hasta que el workflow complete correctamente, no se declara validado el loader con muestras reales.
- No se descargó el dataset completo, no se inició entrenamiento, no se generaron checkpoints y `RUN_TRAINING=False` sigue vigente.
- PR #3 permanece abierta, en borrador y sin fusionar.


### Resultado de la primera validación semántica con muestras reales — 2026-11-21

- El workflow dedicado **BDD100K real-sample validation**, run `44949815647`, terminó con conclusión **success** en el commit del script `564dff9350d07acbe4daf687a2328ab3551c91ad`.
- El script encontró y descargó desde Hugging Face exactamente cuatro pares: dos imágenes/máscaras del split train y dos del split val. Se verificó el emparejamiento por ID, modo RGB de las imágenes, máscaras monocanal, dimensiones iguales y valores permitidos 0–18/255.
- `BDD100KSemanticDataset` procesó las cuatro muestras tras resize a 256x512; las comprobaciones de forma, tipo `torch.int64` e IDs resultantes finalizaron correctamente. El log termina con `RESULT: BDD100K semantic sample validation PASSED`.
- Este resultado valida de forma provisional el acceso y el loader **semántico** con la redistribución Hugging Face `dronefreak/BDD100K-Semantic-Segmentation`; no certifica independientemente la procedencia y no valida instancias, detección ni carriles.
- La CI general del HEAD documental `fca1309e3b573e0fa113e8ae5d6a74165775b230` se encontraba aún en ejecución en la instalación de PyTorch CPU al registrar esta actualización. Runs: `44949848684` (push) y `44949851302` (pull_request). Se debe comprobar su conclusión antes de cerrar la fase.
- No se descargó el dataset completo, no se inició entrenamiento, no se generaron checkpoints y `RUN_TRAINING=False` sigue vigente. PR #3 permanece abierta, en borrador y sin fusionar.


## Investigación de fuente para validar instancias BDD100K — 2026-11-21

- Se revisó la documentación oficial de descarga y formato de BDD100K:
  - El paquete oficial de etiquetas de instance segmentation se denomina **Instance Segmentation**, contiene bitmasks, colormaps, polígonos y RLEs, pesa **111 MB** y publica MD5 `651b41f229d7327d8c4af97772de4390`.
  - Las máscaras bitmask se guardan como PNG RGBA: R = categoría (1..8), G = atributos (bit 0 ignore, bit 1 crowd, bit 2 occluded, bit 3 truncated), y B:A = annotation ID de 16 bits para instance segmentation. El código oficial serializa el ID como `(B << 8) | A`.
  - La segmentación de instancias utiliza el subconjunto de imágenes 10K, no el paquete 100K de detección/carriles.
- Se buscaron redistribuciones públicas Hugging Face de las máscaras de instancias. Los repositorios BDD100K identificados cubren semántica y detección; no se encontró una fuente pública verificable con el árbol `labels/ins_seg/bitmasks/{train,val}` y PNG RGBA. No se utilizará una copia no verificada ni se asumirá que las máscaras semánticas o de color equivalen a máscaras de instancias.
- El servidor oficial ETHZ publica la ruta de descarga y el checksum, pero en esta investigación no se pudo confirmar mediante una petición HTTP real que admita extracción parcial con Range ni inspeccionar el archivo ZIP. Por tanto, no se descargó el paquete de 111 MB ni se afirma que sea posible obtener una muestra sin descargarlo completo.
- Se inspeccionó el loader actual `BDD100KInstanceDataset`: espera pares de JPG y PNG RGBA con el mismo nombre base, decodifica los 16 bits de annotation ID, excluye crowd/ignore y produce cajas, labels y máscaras para Mask R-CNN. El código ya existe, pero todavía no ha sido validado con bitmasks reales.
- **Bloqueo concreto:** falta una fuente accesible y verificable de muestras RGBA, o confirmar que el archivo oficial permite lectura parcial del ZIP. El siguiente intento técnico debe comprobar soporte HTTP Range del archivo oficial en un runner remoto; si no lo soporta, se necesitará autorización/acceso oficial para descargar el paquete de etiquetas completo en infraestructura remota (111 MB), extraer unas pocas máscaras y eliminar el archivo temporal. Esto no requiere que el usuario descargue nada en el teléfono.
- CI general del HEAD `9fc543b9451c5c34641b044147da78ebd8547bf0`: run `44949913773`, job `136985347857`, conclusión **success**. Logs: `32 passed in 10.34s`, smoke tests CLI correctos y `RESULT: BDD100K semantic sample validation PASSED`.
- PR #3 se verificó como `open`, `draft=true`, `merged=false`. No se inició entrenamiento, no se generaron checkpoints y `RUN_TRAINING=False` permanece sin cambios.
- No se modificó código de loaders en esta intervención; se registró la investigación y el bloqueo para no presentar una validación sintética como validación real.


## Comprobación remota de HTTP Range para bitmasks de instancias — 2026-11-21

- Se confirmó en la documentación oficial que el paquete Instance Segmentation contiene bitmasks RGBA para el subconjunto 10K, pesa 111 MB y publica MD5 `651b41f229d7327d8c4af97772de4390`. El formato oficial se documenta en el repositorio BDD100K: R categoría, G atributos y B:A annotation ID de 16 bits. Fuentes: https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst y https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst.
- Se identificó un endpoint S3 de Berkeley que se cita en referencias de descarga como `https://bdd-data-storage-release.s3.us-west-2.amazonaws.com/bdd100k/2021/bdd100k_ins_seg_labels_trainval.zip`. El endpoint ETHZ documentado es `https://dl.cv.ethz.ch/bdd100k/data/`; la página de índice devolvió 502 desde el visor web, por lo que aún no se confirma disponibilidad.
- Se añadió `scripts/probe_bdd100k_instance_range.py`, que prueba HEAD y una petición GET `Range: bytes=0-4095` contra ambos endpoints. La respuesta se procesa en streaming y se cierra tras como máximo el primer bloque de 4 KiB; el ZIP no se guarda ni se descarga completo. El script solo considera soporte verificado si recibe HTTP 206, Content-Range desde byte 0 y firma ZIP `PK\x03\x04`.
- Se añadió el workflow `.github/workflows/probe-bdd100k-instance-range.yml` para ejecutar la comprobación en GitHub Actions. La primera consulta de ejecuciones no mostró todavía un run asociado a este workflow; se ha ajustado el filtro para que la actualización de este registro dispare la prueba. **Resultado HTTP Range: pendiente de ejecución**, no se afirma todavía que el servidor acepte rangos.
- No se descargó ningún archivo de dataset, no se extrajeron máscaras, no se validó el loader de instancias con datos reales y no se inició entrenamiento.
- PR #3 continúa abierta, en borrador y sin fusionar.
- Próximo paso: recuperar el run del workflow de sondeo; si algún endpoint admite rangos, obtener y validar un ZIP parcial solo si es posible extraer entradas completas de forma fiable (ZIP central directory puede requerir rangos finales). Si no admite rangos, evaluar acceso oficial y descarga temporal de 111 MB en infraestructura remota, sin transferir datos al teléfono.


### Resultado del sondeo HTTP Range — 2026-11-21

- GitHub Actions workflow `BDD100K instance archive range probe`, run **44950686146**, job **136987716731**, terminó en `success` (el script completó sus comprobaciones, no significa que el origen de datos haya pasado).
- Endpoint ETHZ `https://dl.cv.ethz.ch/bdd100k/data/bdd100k_ins_seg_labels_trainval.zip`: no resolvió DNS desde el runner (`NameResolutionError`), por lo que no se pudo determinar soporte Range ni disponibilidad del archivo.
- Endpoint S3 Berkeley citado en referencias externas `https://bdd-data-storage-release.s3.us-west-2.amazonaws.com/bdd100k/2021/bdd100k_ins_seg_labels_trainval.zip`: devolvió HTTP 404 tanto en HEAD como en GET Range. No se descargó el ZIP.
- Resultado del script: `RESULT: NO_VERIFIED_RANGE_SOURCE`. Ninguno de los dos endpoints permitió verificar lectura parcial.
- La ejecución no consumió el archivo de 111 MB: el cliente solo intentó leer hasta el primer bloque de 4 KiB de la respuesta Range y cerró la conexión.
- Conclusión: **no es viable extraer una máscara individual por HTTP Range con las fuentes probadas**. El endpoint S3 probado no tiene ese objeto en esa ruta y ETHZ no resolvió desde GitHub Actions. Esto no demuestra que el archivo oficial no exista en otro endpoint ni que no se pueda descargar desde Colab/RunPod.
- Próximo paso recomendado: probar la URL oficial autenticada que entrega el portal BDD100K (si el usuario tiene acceso autorizado) desde el entorno remoto; si la descarga del paquete de 111 MB está permitida, descargarlo solo en infraestructura remota, verificar MD5, extraer 2–4 máscaras RGBA y eliminar el ZIP. Si no se dispone de URL oficial funcional, buscar una fuente alternativa autorizada antes de validar.
- No se descargó ningún dataset, no se extrajeron muestras, no se validó el loader de instancias con datos reales y no se inició entrenamiento. PR #3 sigue abierta, en draft y sin fusionar.


## Preparación de validación real de instancias con URL oficial autorizada — 2026-11-21

- Se volvió a consultar la documentación primaria de BDD100K. Confirma que las anotaciones de instancia se distribuyen en el paquete **Instance Segmentation** de 111 MB, MD5 `651b41f229d7327d8c4af97772de4390`, dentro de `bdd100k/labels/ins_seg/bitmasks/{train,val}`. Las imágenes correspondientes pertenecen al paquete 10K Images. Fuente: https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst.
- La documentación de formato confirma que las máscaras deben ser PNG RGBA: R categoría 1–8, G flags (ignore/crowd en los bits bajos), B:A ID de anotación de 16 bits. Fuente: https://github.com/bdd100k/bdd100k/blob/master/doc/source/format.rst.
- El portal oficial de descarga identificado por la documentación es https://bdd-data.berkeley.edu/; el repositorio/toolkit oficial remite a ese portal para obtener los datos. Fuente complementaria: https://github.com/SysCV/bdd100k-models/blob/main/doc/PREPARE_DATASET.md.
- Se reintentó el acceso público directo desde GitHub Actions: ETHZ no resolvió DNS en el runner y el objeto de la URL S3 secundaria probada devolvió 404. El portal Berkeley tampoco pudo inspeccionarse de forma automatizada en esta sesión (timeout). No hay credenciales ni URL de descarga autenticada disponibles en el entorno, y no se intentará eludir el portal.
- Se implementó `scripts/validate_bdd100k_instance_sample.py`: recibe la URL autorizada desde la variable secreta `BDD100K_INSTANCE_LABELS_URL`, descarga el archivo únicamente en el runner efímero, verifica MD5 oficial, comprueba integridad ZIP, busca pares por stem entre las bitmasks oficiales y las imágenes del mirror ya usado, extrae como máximo 2 muestras train + 2 val, verifica RGB/RGBA y dimensiones, ejecuta `BDD100KInstanceDataset` y elimina el ZIP al terminar. Si checksum, layout o emparejamiento no coinciden, falla sin validar.
- Se añadió `.github/workflows/validate-bdd100k-instance-sample.yml`, manual (`workflow_dispatch`) y de solo lectura sobre el repositorio. No se dispara automáticamente para evitar descargar 111 MB sin que exista una URL autorizada.
- **Bloqueo restante que requiere intervención del titular de los datos:** abrir el portal oficial, aceptar la licencia/condiciones BDD100K y obtener la URL de descarga del paquete Instance Segmentation. Añadirla en GitHub → Settings → Secrets and variables → Actions como secreto `BDD100K_INSTANCE_LABELS_URL`. No pegar tokens, cookies ni enlaces firmados en el chat ni en archivos del repositorio. Después ejecutar manualmente el workflow. La URL secreta puede ser temporal; si expira, actualizar el secreto.
- No se ha descargado el paquete, no se ha ejecutado la validación real de instancias, no se ha entrenado ni generado checkpoint. No afirmar validación hasta que el workflow manual produzca `RESULT: BDD100K INSTANCE SAMPLE VALIDATION PASSED`.
- PR #3 sigue abierta, en draft y sin fusionar. El registro se actualiza con esta limitación y la ruta operativa preparada.


## Alternativa BDD100K alojada en GitHub para muestras de instancias — 2026-11-21

- Ante el error HTTP 403 del enlace de descarga de etiquetas oficiales, se investigó si GitHub contiene una copia utilizable sin autenticación.
- Se localizó el repositorio público de terceros [PETER-nguyen7506/yolo11](https://github.com/PETER-nguyen7506/yolo11), que incluye datos bajo `datasets/bdd100k-seg-100/` en blobs normales de Git (no solo código ni punteros LFS):
  - 100 imágenes JPEG de validación del subconjunto BDD100K 10K.
  - 100 JSON con referencias a máscaras por instancia.
  - 1.242 máscaras PNG binarias por objeto.
  - `manifest.csv` identifica el split como `val`; las clases incluidas son car, truck, bus y motorcycle. El propio README del repositorio declara 100 imágenes BDD100K y 1.242 etiquetas.
  - Tamaño total inspeccionado del árbol de datos: aproximadamente 15,64 MiB.
- El README del repositorio atribuye los datos a BDD100K y declara que se aplican las condiciones de Berkeley DeepDrive para uso educativo/investigación no comercial. La licencia oficial distingue el código BSD-3-Clause de la licencia de datos; no se debe interpretar la licencia del código como licencia de las imágenes/etiquetas. Fuente primaria de licencia y estructura: https://github.com/bdd100k/bdd100k/blob/master/doc/source/license.rst y https://github.com/bdd100k/bdd100k/blob/master/doc/source/download.rst.
- **Alcance y limitaciones:** esta copia es una muestra de validación reducida, no el dataset completo; contiene máscaras binarias separadas por objeto, no los PNG RGBA originales con flags y annotation IDs oficiales. No incluye las ocho clases de instancia requeridas por el loader actual (faltan pedestrian, rider, bicycle y train, entre otras clases del esquema); por tanto no sustituye el paquete oficial de Instance Segmentation ni permite declarar validado el loader completo de instancias. Sí es candidata para una prueba acotada de lectura de imágenes, máscaras por objeto, emparejamiento y cálculo de cajas/métricas para las cuatro clases vehiculares presentes, tras verificar la licencia/procedencia y adaptar el formato sin fingir que son bitmasks oficiales.
- Se confirma que el repositorio oficial https://github.com/bdd100k/bdd100k contiene toolkit, documentación y scripts de conversión, pero no aloja los paquetes de imágenes/etiquetas; su documentación remite al servidor de datos oficial y publica para Instance Segmentation el tamaño 111 MB y MD5 `651b41f229d7327d8c4af97772de4390`.
- Estado de esta intervención: se inspeccionó el árbol GitHub y se leyeron el README, un JSON de ejemplo, el manifiesto y el script de evaluación. No se descargaron imágenes ni máscaras al entorno de entrenamiento, no se ejecutó el loader del proyecto con esta copia, no se modificó código de entrenamiento y no se inició entrenamiento.
- Próximo paso recomendado: crear un validador independiente que obtenga por HTTPS desde GitHub solo 2–4 imágenes y sus JSON/máscaras referenciadas, verifique dimensiones, modo, máscaras no vacías, clases permitidas y correspondencia, y luego adapte las máscaras a targets de instancia de forma explícita. Mantener separada esta validación parcial de la validación oficial RGBA pendiente.
- HEAD comprobado antes de registrar esta investigación: `6fa089aa3dc068bd08d07c3412e302972d7ff343`. PR #3 continúa `open`, `draft=true`, `merged=false`; no fusionar.


## Adaptador y validación parcial de instancias desde copia GitHub — 2026-11-21

- Se creó `src/utils/bdd100k_github_sample.py`, un adaptador independiente para el formato de la copia pública de terceros: una imagen JPG, un JSON por imagen y una máscara PNG binaria por objeto. Convierte explícitamente las cuatro clases disponibles a IDs compatibles con el espacio BDD100K (car=3, truck=4, bus=5, motorcycle=7) y construye tensores `boxes`, `labels`, `masks`, `area`, `iscrowd` compatibles en estructura con Torchvision Mask R-CNN.
- **No modifica ni reutiliza** `BDD100KInstanceDataset`: ese loader permanece reservado a bitmasks oficiales RGBA con IDs de anotación y flags. Esta separación evita presentar máscaras binarias de terceros como si fueran las máscaras oficiales.
- Se creó `scripts/validate_bdd100k_github_instance_sample.py`: descarga desde `raw.githubusercontent.com` con revisión fija `af057234c8f010302c7fbb9807e263167693fb25`, consulta el manifiesto, elige hasta cuatro imágenes para cubrir clases, descarga únicamente imágenes/JSON/máscaras asociadas a esos frames en un directorio temporal, valida máscaras no vacías y dimensiones, ejecuta el adaptador y comprueba tensores, cajas y recuentos. No guarda datos en Git ni en Drive.
- Se añadió `tests/test_bdd100k_github_sample.py` y workflow `.github/workflows/validate-bdd100k-github-instance-sample.yml`, activado al modificar los archivos relevantes o manualmente. No inicia entrenamiento.
- Primera ejecución de validación real: run `44955961877`, falló en una expectativa incorrecta de una prueba sintética sobre el redimensionado nearest-neighbor (el adaptador produjo caja [1,1,4,3], la prueba esperaba [1,1,5,3]). El segundo test pasó. Se corrigió la expectativa de la prueba, no el adaptador, en commit `a1a6c6b57cad4383765d85deca8e64705ebacd12`.
- Nueva ejecución sobre el test corregido: run `44956039459`; al momento de registrar está en curso instalando dependencias CPU, por lo que **la descarga y validación real aún no están confirmadas**. Consultar el run antes de declarar éxito.
- Las escrituras secuenciales de cuatro archivos provocaron varios runs redundantes de CI general; no se alteraron datos del dataset. En futuras modificaciones agrupar cambios en un solo commit si la herramienta disponible lo permite.
- No se ha iniciado entrenamiento ni se han creado checkpoints. La validación oficial RGBA sigue pendiente y la muestra GitHub solo cubre cuatro clases de vehículo.
- PR #3 debe seguir abierta, draft y sin fusionar.


### Resultado de validación de la muestra GitHub de instancias — 2026-11-21

- La primera corrección de la prueba sintética permitió que ambas pruebas del adaptador pasaran (`2 passed`). La ejecución siguiente detectó que el script ejecutado directamente no tenía la raíz del repositorio en `sys.path`; se corrigió añadiendo la raíz antes de importar `src` (commit `17bf38d1fb97d412397ebe333376592479798b49`).
- Validación remota repetida sobre HEAD `8e212c417dc260c1a84e388e46002a30bed2cda9`: workflow run **44956137606**, conclusión **success**.
- Evidencia del log:
  - Se descargaron solo 2 imágenes de validación y sus JSON/máscaras: `80f308d1-e30a628d` (23 máscaras) y `82d184d4-00000000` (14 máscaras).
  - El adaptador produjo tensores imagen `(3,256,512)`, cajas `(23,4)` y máscaras `(23,256,512)` para la primera; y `(3,256,512)`, cajas `(14,4)` y máscaras `(14,256,512)` para la segunda.
  - Total: **2 imágenes, 37 instancias**, clases observadas `bus, car, motorcycle, truck`.
  - Las 2 pruebas unitarias pasaron y el script terminó con `RESULT: BDD100K GITHUB INSTANCE SAMPLE VALIDATION PASSED`.
- Los datos se descargaron únicamente al runner efímero y el script usó `TemporaryDirectory`; no se guardaron en el repositorio, Google Drive ni el dispositivo del usuario.
- **Qué queda validado:** la ruta remota GitHub, lectura JPG/JSON/PNG, emparejamiento de máscaras por objeto, dimensiones, clases mapeadas, construcción de cajas/máscaras y estructura de tensores para una muestra de 2 imágenes y 37 instancias.
- **Qué NO queda validado:** el loader oficial `BDD100KInstanceDataset` de RGBA, los annotation IDs/flags oficiales, las ocho clases oficiales completas, el entrenamiento de Mask R-CNN ni métricas de benchmark. Esta muestra no reemplaza el dataset oficial ni permite reportar AP de validación.
- El workflow general de Python asociado al HEAD `8e212c417dc260c1a84e388e46002a30bed2cda9` (run `44956141257`) seguía en ejecución al actualizar esta nota; revisar su conclusión por separado antes de afirmar que CI general pasó.
- PR #3 comprobada: `open`, `draft=true`, `merged=false`. Mantener sin fusionar.


### Preparación de smoke test de Mask R-CNN con muestra BDD100K — 2026-11-21

- Se confirmó que el CI general previo al cambio terminó correctamente: run `44956247587`, conclusión `success`, asociado al HEAD `95a3049da5438ed0e1748732bff0a6883431cfcb`.
- Se amplió `scripts/validate_bdd100k_github_instance_sample.py` con la opción `--maskrcnn-smoke-test`. La prueba vuelve a cargar una imagen a 128×256, limita el target a un máximo de 8 instancias, crea `maskrcnn_resnet50_fpn` con pesos aleatorios y 9 salidas (fondo + 8 IDs de clase), ejecuta forward, comprueba que las pérdidas sean escalares y finitas y ejecuta `backward()`.
- El smoke test no ejecuta `optimizer.step()`, no ajusta pesos y no guarda checkpoints. Su propósito es detectar incompatibilidades entre el adaptador de máscaras/cajas, Torchvision y el modelo.
- Se modificó `.github/workflows/validate-bdd100k-github-instance-sample.yml` para instalar Torchvision CPU y ejecutar la validación con el smoke test en GitHub Actions, sin GPU ni datos en el teléfono. Se corrigió la continuación multilínea del comando antes de verificar el run final.
- Runs disparados por los commits de implementación: `44956646755`, `44956655632` (validación de muestra) y varias ejecuciones de CI general. En la última consulta seguían `in_progress`; **todavía no se declara que Mask R-CNN haya pasado**. Consultar los runs posteriores al HEAD actual antes de concluir.
- HEAD de la rama al actualizar esta entrada: `8b4d30ce04e360bba29272f93fb1aa1c41413bf9`.
- PR #3 se mantiene abierta, en draft y sin fusionar. No se ha iniciado entrenamiento real ni se ha generado checkpoint.
- Próximo paso: recuperar la conclusión y los logs del run de validación posterior al commit `8b4d30c`. Si el smoke test falla, corregir la incompatibilidad detectada y repetirlo; si pasa, avanzar a preparar el protocolo de entrenamiento acotado y reanudable, sin iniciar entrenamiento completo hasta validar el acceso/licencia y cobertura de los datos.


### Resultado del smoke test de Mask R-CNN — 2026-11-21

- La primera ejecución del workflow ampliado, run `44956655632`, falló por una continuación de línea duplicada en el comando shell; las 2 pruebas unitarias sí pasaron. Se corrigió el workflow y se verificó la ejecución posterior.
- Run correcto: **`44956675144`**, job `137006210434`, conclusión `success`, sobre el código del commit `8b4d30ce04e360bba29272f93fb1aa1c41413bf9`.
- Evidencia del log:
  - Instalación de PyTorch CPU y Torchvision CPU correcta.
  - Pruebas del adaptador: **2 passed**.
  - Descarga temporal y lectura de la muestra: 2 imágenes, 37 instancias, clases bus/car/motorcycle/truck.
  - Mask R-CNN ResNet50-FPN con pesos aleatorios, 9 salidas y 8 instancias en el smoke test: forward correcto; pérdidas escalares y finitas; `backward()` completado.
  - Pérdidas observadas: `loss_classifier=2.05140`, `loss_box_reg=0.21448`, `loss_mask=3.61923`, `loss_objectness=0.69957`, `loss_rpn_box_reg=1.87054`; total `8.45520`.
  - Mensaje final del log: `MASKRCNN_SMOKE_TEST PASSED ... backward=ok optimizer_step=no checkpoint=no` y `RESULT: BDD100K GITHUB INSTANCE SAMPLE VALIDATION PASSED`.
- **Interpretación:** el adaptador de muestra y el modelo Mask R-CNN son técnicamente compatibles en un forward/loss/backward acotado sobre CPU. Los pesos eran aleatorios y no se hizo `optimizer.step()`; por tanto esto **no es entrenamiento**, no valida precisión ni AP, no produce checkpoint y no demuestra generalización.
- El CI general correspondiente a los commits de esta intervención seguía en ejecución en la última consulta; revisar sus conclusiones antes de afirmar que está aprobado.
- PR #3 comprobada: abierta, draft y sin fusionar. No se inició entrenamiento completo ni se descargó el dataset al dispositivo del usuario.
- Próximo paso: revisar CI general y preparar el entrenamiento real reanudable sobre datos con acceso/licencia confirmados. Antes de entrenar se debe resolver la cobertura limitada de la muestra de instancias (solo cuatro clases) y no presentarla como sustituto de las anotaciones oficiales RGBA.


### Preparación del preflight y protocolo de entrenamiento de instancias — 2026-11-21

- Se revisó el estado después del smoke test: CI general sobre HEAD `c8b7b83ea821ed959c3a045bf1f5c06e3a9cd73b` (run `44956778283`) terminó `success`; PR #3 continúa abierta, draft y sin fusionar.
- Se confirmó que la muestra de GitHub usada para el smoke test contiene solo 2 imágenes del split val, 37 máscaras y 4 clases (bus/car/motorcycle/truck). **No se utilizará para entrenar ni para reportar métricas**; no hay split train ni cobertura completa.
- Se añadió `scripts/audit_bdd100k_instance_splits.py`, auditoría previa de las anotaciones oficiales RGBA. Comprueba:
  - emparejamiento exacto imagen↔PNG y ausencia de máscaras huérfanas;
  - modo RGBA original y dimensiones coincidentes;
  - IDs de instancia, categorías 1–8 y flags ignore/crowd;
  - separación entre stems de train y val;
  - recuento de instancias por cada una de las ocho clases.
  Por defecto bloquea el preflight si falta alguna clase en train; la ausencia en val se reporta, pero no bloquea por sí sola.
- Se añadieron pruebas sintéticas `tests/test_bdd100k_instance_preflight.py` para conteo de instancia, rechazo de máscaras no RGBA y emparejamiento incompleto.- Se actualizó `scripts/train_maskrcnn_cityscapes.py` para validar también el orden/nombre de clases del checkpoint al reanudar y corregir el mensaje de dimensiones de clase (9 salidas: fondo + 8 clases). La reanudación continúa siendo por época; no promete restaurar aleatoriedad de lotes a mitad de época.
- Se actualizó el notebook Colab para mostrar la auditoría oficial y exigir un informe `ready_for_training=true` antes de permitir `MODEL="instance"` con `RUN_TRAINING=True`. La muestra GitHub parcial no pasa por esta ruta.- Se documentó el procedimiento en `docs/PROTOCOLO_EXPERIMENTAL.md`. Evaluación BDD100K oficial se ejecuta después del entrenamiento sobre val, con el protocolo interno de AP claramente identificado; no equivale a COCOeval.
- CI general disparado por estos commits: runs `44963069208`, `44963057605`, `44963053256` y otros asociados a commits intermedios. En la última consulta seguían en ejecución; **no se declara aún que esta modificación haya pasado CI**. Consultar el run más reciente y su conclusión.
- No se inició entrenamiento ni se generaron checkpoints. No se descargaron datos al teléfono ni se intentó acceder sin autorización a las etiquetas oficiales. El acceso a las bitmasks oficiales RGBA sigue siendo el bloqueo real para iniciar el entrenamiento de instancias.
- Próximo paso: confirmar CI; si pasa, realizar preflight con datos oficiales desde almacenamiento remoto autorizado. Si el usuario aún no dispone del paquete oficial, no entrenar con la muestra de cuatro clases: continuar con una tarea BDD100K que sí tenga train/val accesibles (por ejemplo semántica) o resolver acceso autorizado a instancias.


### Investigación de datasets alternativos de acceso más sencillo — 2026-11-21

- El usuario preguntó si se pueden sustituir BDD100K/Cityscapes por datasets de acceso más fácil. Se investigaron fuentes públicas y sus anotaciones/licencias.
- **UrbanSyn (candidato principal para una prueba técnica unificada):** dataset sintético disponible en Hugging Face, con más de 7.5k imágenes anotadas según la descripción del proyecto (el repositorio HF muestra 30.158 filas y 86,1 GB de tamaño total). Incluye RGB, segmentación semántica de 19 clases compatibles con el esquema trainId de Cityscapes, segmentación panóptica de objetos dinámicos y cajas 2D; licencia declarada CC BY-SA 4.0. Fuente: https://huggingface.co/datasets/UrbanSyn/UrbanSyn. Ventaja: no depende del portal de Cityscapes ni de credenciales Berkeley; se pueden solicitar archivos/muestras desde Colab sin pasar por el teléfono. Limitación: escenas sintéticas, no fotografías reales; no se debe asumir que representa noche/clima real. El tamaño completo no debe descargarse antes de probar acceso selectivo y loader.
- **A2D2 (candidato principal si se priorizan imágenes reales):** dataset de Audi con 41.277 fotogramas anotados, segmentación semántica, segmentación de instancias y cajas 3D. Está en buckets públicos AWS S3, accesibles sin cuenta AWS y con archivos individuales navegables. Fuentes: https://a2d2-dataset.github.io/ y https://registry.opendata.aws/aev-a2d2/. Licencia declarada CC BY-ND 4.0; revisar el alcance de las condiciones antes de redistribuir o compartir material derivado. Se debe validar el esquema concreto de etiquetas, splits y correspondencia antes de adaptar el pipeline.
- **Mapillary Vistas:** 25.000 imágenes, 124 categorías semánticas y anotaciones de instancias; variedad de ciudades, clima, estaciones y perspectivas. Sin embargo, la copia de Hugging Face consultada exige iniciar sesión y aceptar condiciones de acceso, por lo que no elimina todos los obstáculos. Fuente: https://huggingface.co/datasets/candylion/mapillary-vistas-v2. Licencia indicada CC BY-NC-SA 4.0.
- **KITTI:** se descarta como primera alternativa por ahora porque el portal oficial exige registro y declarar el propósito de uso. Fuente: https://www.cvlibs.net/datasets/kitti/user_login.php.
- Recomendación provisional comunicada al usuario: probar primero UrbanSyn con una muestra remota pequeña para comprobar descarga selectiva, layout, etiquetas y loaders; si el requisito de fotografías reales es prioritario, evaluar A2D2 mediante acceso selectivo S3. No cambiar aún el dataset principal ni modificar código de entrenamiento hasta que el usuario elija el enfoque y se valide la licencia/anotaciones.
- No se descargó ningún dataset, no se modificó código, no se inició entrenamiento ni se generaron checkpoints. PR #3 permanece abierta, en draft y sin fusionar.
- Próximo paso: recibir decisión del usuario sobre priorizar escenas reales (A2D2) o permitir dataset sintético (UrbanSyn); después ejecutar un preflight remoto pequeño, registrar evidencia y decidir la migración del pipeline.


### Selección orientada a los requisitos obligatorios del Equipo 2 — 2026-11-21

- El usuario precisó que el dataset o combinación debe cubrir el enunciado completo: detección/segmentación urbana multiclase e instancias (peatones, vehículos, ciclistas, señales y carriles), preprocesamiento y aumentos realistas, comparación semántica vs instancias, evaluación por día/noche/lluvia/niebla, matrices de confusión y mAP/IoU/mIoU/FPS.
- Se revisó la cobertura de los candidatos y se ajusta la recomendación inicial:
  - **A2D2 como dataset real principal**: 41.277 fotogramas anotados; distribución oficial en bucket público AWS S3, accesible sin cuenta AWS y con selección de archivos/subconjuntos. La documentación declara segmentación semántica, de instancias y cajas 3D. Su taxonomía incluye peatones, vehículos, bicicletas y señales; las etiquetas semánticas incluyen líneas sólidas/discontinuas y pasos peatonales, útiles para marcas viales/carriles. Fuentes: https://a2d2-dataset.github.io/ ; https://registry.opendata.aws/aev-a2d2/ ; mapeo de clases A2D2: https://openaccess.thecvf.com/content_ECCV_2024/supplemental/Cao_A2D2_class_mapping (referencia suplementaria localizada en investigación).
  - **ACDC como complemento de robustez**: 4.006 imágenes adversas equilibradas entre niebla, noche, lluvia y nieve, con anotaciones de píxel y correspondencias de escenas normales. La página oficial documenta semántica, detección y panoptic segmentation; el trabajo actualizado de 2026 describe 8.012 imágenes totales y 5.509 con anotación panóptica. Requiere aceptar términos/licencia académica no comercial y verificar acceso/descarga antes de depender de él. Fuentes: https://acdc.vision.ee.ethz.ch/ ; https://acdc.vision.ee.ethz.ch/overview ; https://pubmed.ncbi.nlm.nih.gov/41237037/.
  - **UrbanSyn queda como alternativa o complemento sintético**, no como dataset principal de robustez: ofrece 19 clases semánticas (incluye persona/rider, vehículos y señales), panoptic instances y cajas para objetos dinámicos; sin embargo, no presenta particiones etiquetadas de día/noche/lluvia/niebla y la clase semántica road no separa marcas de carril. Las imágenes RGB completas ocupan 21 GB; etiquetas semánticas 380 MB, panoptic 102 MB y cajas 6 MB. Fuente: https://www.urbansyn.org/.
- **Propuesta técnica provisional**: A2D2 para entrenamiento/evaluación principal con datos reales y etiquetas de marcas viales; ACDC para medir transferencia/robustez en condiciones adversas por separado, si se confirma acceso permitido; aumentos realistas (gamma, exposición, brillo, blur, niebla/lluvia sintéticas) durante entrenamiento en A2D2. No mezclar métricas entre datasets: reportar A2D2 y ACDC por separado con mapeo de clases explícito. Comparar DeepLabV3+ (semántica) contra Mask R-CNN (instancias) y, si el diseño lo requiere, detector de cajas complementario. Extraer atributos finos solo donde las anotaciones permitan supervisión; no inventar subclases sin etiquetas.
- **Riesgos que deben resolverse en preflight**: verificar en el bucket oficial A2D2 el layout real de train/val y disponibilidad de máscaras de instancia para las imágenes escogidas; validar licencia CC BY-ND 4.0 para el uso académico y no redistribuir derivados no permitidos. En ACDC, comprobar acceso y condiciones de uso; si no es posible, las condiciones adversas solo podrán estudiarse mediante aumentos sintéticos y/o subconjuntos reales accesibles, declarando esa limitación.
- El usuario no pidió todavía cambiar el código ni ejecutar descargas/entrenamientos. No se modifica aún el dataset principal en el repositorio hasta completar preflight remoto selectivo y confirmar que las anotaciones cubren las tareas. Ningún dataset se descargó al dispositivo; no hubo entrenamiento ni checkpoints.
- Próximo paso recomendado: ejecutar desde un entorno remoto un preflight de bajo volumen del bucket A2D2 (listado + pocas imágenes/labels + comprobación de anotaciones de carriles/instancias), y comprobar el proceso de acceso a ACDC. Después adaptar loaders, mapeos, split y evaluación; mantener BDD100K/Cityscapes como legado hasta migración validada.


### Selección de datasets según requisitos académicos del Equipo 2 — 2026-11-21

- El usuario detalló los requisitos obligatorios del Equipo 2: preprocesamiento (exposición/gamma y aumentos de desenfoque, niebla y brillo), comparación de segmentación por instancias (p. ej. Mask R-CNN) y semántica (p. ej. DeepLabV3+ con detector), extracción de características/clasificación fina, evaluación por condición día/noche/lluvia/niebla, análisis de errores, mAP, IoU/mIoU y FPS.
- La selección no debe basarse únicamente en facilidad de descarga; debe cubrir las clases y tareas requeridas.
- **UrbanSyn propuesto como dataset principal de entrenamiento/comparación:** >7.5k imágenes sintéticas fotorealistas; segmentación semántica de 19 clases siguiendo IDs de Cityscapes, con traffic light y traffic sign; panoptic instance segmentation y cajas 2D para clases dinámicas (person, rider, car, truck, bus, train, motorcycle, bicycle). La página oficial publica tamaños separados: RGB 21 GB, semantic masks 380 MB, panoptic masks 102 MB, bounding boxes 6 MB. Esto permite descargar selectivamente etiquetas y subconjuntos RGB desde infraestructura remota, sujeto a verificar los enlaces/muestreo. Licencia/condiciones deben citarse y respetarse; la página contiene redacción no uniforme sobre CC BY-SA/CC BY-NC-SA, por lo que comprobar el texto completo de términos antes de fijar la atribución/licencia final. Fuente: https://www.urbansyn.org/.
- **ADUULM propuesto como conjunto externo de robustez real:** 3.482 imágenes anotadas para segmentación semántica, 12 clases incluyendo car/truck/bus/motorbike/pedestrian/bicyclist/traffic-sign/traffic-light/road/sidewalk/pole; training 1.414 y validation 508 bajo buen tiempo; test 1.559 en condiciones meteorológicas adversas. La documentación menciona escenarios sunny/rainy/foggy/night. También contiene una tarea separada de drivable area con siete clases de carril/zona de conducción (2.226 imágenes). Fuente: https://github.com/uulm-mrm/aduulm_dataset_tools.
- **Limitación importante:** ADUULM documenta segmentación semántica y drivable-area, no máscaras de instancias por objeto para Mask R-CNN. Por tanto, se propone usarlo para mIoU/IoU por condición adversa, no reportar AP de instancias con ADUULM sin anotaciones de cajas/instancias adecuadas. UrbanSyn permite mAP/AP y segmentación por instancias, pero sus escenarios sintéticos no deben presentarse como evidencia de condiciones reales de lluvia/noche salvo que se demuestre que esos atributos están presentes.
- **Plan experimental propuesto (pendiente de validación):**
  1. UrbanSyn: entrenar DeepLabV3+ semántico y Mask R-CNN de instancias sobre clases compatibles; comparar mIoU/IoU y mAP por clase. Extraer embeddings/crops para clasificación de tipos de vehículos con las clases dinámicas disponibles.
  2. UrbanSyn: generar splits controlados con aumentos realistas (exposición, gamma, brillo, motion blur y niebla) para medir degradación controlada; registrar claramente que son condiciones simuladas.
  3. ADUULM: evaluar generalización semántica en datos reales adversos, separando los subconjuntos/atributos que el dataset realmente permita identificar. Mantener separado el resultado de carriles/drivable-area.
  4. Medir FPS/latencia en hardware identificado y fijo; matrices de confusión y ejemplos de error.
- **Limitaciones académicas por resolver antes de declarar cobertura completa:** confirmar acceso remoto/licencia y layout de ambos datasets; comprobar qué condiciones específicas contiene cada split de ADUULM; definir si la clasificación fina exigida será de tipos de vehículos (clases ya disponibles) o subtipos de señales (UrbanSyn/ADUULM solo etiquetan traffic sign como clase general); determinar si el profesor exige mAP de instancias también bajo lluvia/noche real. Si exige AP de instancias en clima real, se necesitará un dataset adicional con cajas/máscaras y atributos ambientales.
- La recomendación comunicada al usuario es UrbanSyn + ADUULM, condicionada a una prueba remota pequeña. No se ha cambiado aún el dataset principal, no se han descargado datos, no se modificó código ni se inició entrenamiento.
- PR #3 permanece abierta, en draft y sin fusionar.
- Próximo paso técnico propuesto: preflight remoto de ambos datasets (acceso selectivo, licencia, anotaciones, emparejamiento, cobertura por clase/condición) antes de adaptar loaders o retirar BDD100K.


### Revisión de datasets frente a los requisitos completos del Equipo 2 — 2026-11-21

- El usuario precisó que la selección debe satisfacer el enunciado completo: preprocesamiento (exposición/gamma/aumentos de blur, niebla y brillo), comparación de segmentación semántica frente a instancias/detección, extracción de características para clases finas, evaluación por día/noche/lluvia/niebla, matrices de confusión y métricas mAP, IoU/mIoU y FPS.
- Se revisó la cobertura exacta de tres candidatos:
  - **Waymo Open Dataset – Perception**: candidato más completo como dataset real único. Su subconjunto de panoptic 2D incluye 100k imágenes y 28 clases (vehículos, peatones, ciclistas, señales, semáforos, carretera, acera, road marker y lane marker); las instancias están disponibles para Vehicle, Pedestrian y Cyclist. Incluye además 2D boxes para Vehicles, Pedestrians, Cyclists y Signs, y diversidad geográfica/ambiental/horaria. Fuentes oficiales: https://waymo.com/open/data/perception/ y https://waymo.com/open/about/. Requiere iniciar sesión y aceptar licencia no comercial; no es Open Source. No se debe prometer acceso anónimo ni ausencia de registro. Dataset completo de gran tamaño; el flujo deberá obtener segmentos seleccionados desde almacenamiento remoto, no descargar todo. Términos: https://waymo.com/open/terms/.
  - **UrbanSyn**: buena alternativa de acceso público sin login para un prototipo unificado semántico + instancias + detección. Tiene 19 clases semánticas (incluye traffic sign y road) y panoptic/bbox para clases dinámicas (person, rider, car, truck, bus, train, motorcycle, bicycle). Sus archivos de etiquetas son mucho más pequeños que RGB (semántica 380 MB, panoptic 102 MB, boxes 6 MB), pero las imágenes RGB suman 21 GB. La fuente no declara particiones etiquetadas por clima/hora; por tanto no permite afirmar evaluación real estratificada día/noche/lluvia/niebla. Se pueden crear corrupciones sintéticas para probar robustez, pero deben reportarse como pruebas controladas, no como condiciones reales observadas. Licencia CC BY-SA 4.0. Fuente: https://urbansyn.org/ y https://huggingface.co/datasets/UrbanSyn/UrbanSyn.
  - **SHIFT**: candidato específico para robustez, pues introduce cambios de intensidad de lluvia, niebla, nubosidad y hora del día; es sintético. Debe verificarse la cobertura exacta de tareas/formatos de etiquetas antes de incorporarlo al pipeline. Fuentes: https://www.vis.xyz/shift y paper CVPR https://openaccess.thecvf.com/content/CVPR2022/html/Sun_SHIFT_A_Synthetic_Driving_Dataset_for_Continuous_Multi-Task_Domain_Adaptation_CVPR_2022_paper.html.
  - **A2D2**: acceso público individual por AWS sin cuenta AWS, con segmentación semántica y de instancias; útil como respaldo real. Sin embargo, no se ha confirmado que permita una partición fiable por día/noche/lluvia/niebla ni que su anotación cubra exactamente todas las clases requeridas en un mismo esquema. Licencia CC BY-ND 4.0. Fuentes: https://a2d2-dataset.github.io/ y https://registry.opendata.aws/aev-a2d2/.
- Conclusión provisional: Waymo Perception es el mejor ajuste funcional de un solo dataset, pero tiene barrera de registro/licencia y volumen; UrbanSyn es la vía más simple para una primera prueba end-to-end, aunque no demuestra robustez meteorológica real. Una combinación UrbanSyn + SHIFT podría cubrir semántica/instancias y escenarios sintéticos, pero el informe debe reconocer el dominio sintético. A2D2 queda como alternativa real si Waymo no es accesible.
- Requisito metodológico transversal: el pipeline debe registrar los atributos disponibles por muestra y construir subconjuntos por escenario solo cuando existan etiquetas/metadata verificables. Los aumentos sintéticos de niebla/lluvia/noche se evaluarán por separado de los datos capturados realmente en esas condiciones. La extracción de características finas (tipo de vehículo/señal) se limita a las clases/subclases que estén realmente anotadas; no se inventan subclases.
- No se ha cambiado dataset principal, no se ha modificado código, no se descargaron datos ni se inició entrenamiento. PR #3 permanece abierta, en draft y sin fusionar.
- Próximo paso: decidir si se puede aceptar registro de Waymo y licencia no comercial. En paralelo, validar de forma remota una muestra pequeña de UrbanSyn para no bloquear el desarrollo. Antes de migrar loaders, ejecutar un inventario de anotaciones y tamaños de los candidatos seleccionados.


### Preflight remoto inicial de UrbanSyn y revisión de acceso Waymo — 2026-11-21

- Se volvió a leer este registro antes de continuar. HEAD previo: `ac07ac1ee656b504219ee66f6c42683ac36e4905`. PR #3 se comprobó abierta, en draft, sin fusionar.
- **UrbanSyn:** se contrastó la estructura con la ficha oficial de Hugging Face y la página del proyecto. La ficha declara un único split `train`, carpetas `rgb`, `ss`, `panoptic`, `bbox2d` (además de `ss_color` y `depth`), RGB/etiquetas de 2048×1024, 19 IDs semánticos de Cityscapes (más unlabeled ID 19), panoptic RGB donde el canal azul codifica la clase y JSON de cajas con bbox/label/color/occlusion. El repositorio HF anuncia 30.158 filas y 86,1 GB, por lo que queda prohibido usar `snapshot_download` o clonar el dataset completo para este preflight.
- Se añadieron `scripts/validate_urbansyn_sample.py` y `.github/workflows/validate-urbansyn-sample.yml`. El script lista metadatos/rutas remotas y descarga a un directorio temporal únicamente 1–4 muestras que tengan RGB + semantic + panoptic + bbox2D emparejados por nombre. Verifica modos RGB/grayscale/panoptic RGB, dimensiones, IDs semánticos, canal de clases panoptic y estructura JSON. No guarda datos ni artefactos en el repositorio.
- Commits de esta adición: `2229cec0dde92c48609673598714b64ce58d34b0` (script) y `4a9c5ce3b4607dc83d17f0924c3f0702288eda45` (workflow). El workflow está configurado para dispararse por push de esos archivos o manualmente, y limita la muestra a cuatro ejemplos.
- **Estado de ejecución:** al consultar inmediatamente después del commit, el conector GitHub no devolvió ejecuciones para el commit (su consulta de runs filtra ejecuciones disparadas por pull request). Por tanto, la ejecución remota de este nuevo preflight queda **pendiente de confirmar**; no se declara PASS ni se inventa cantidad/tamaño descargado. Revisar Actions en GitHub: `validate-urbansyn-sample.yml`.
- **Waymo:** se verificó la página oficial de términos. La propia página exige iniciar sesión y aceptar el acuerdo de licencia para acceder al dataset; el acceso no es anónimo. La licencia es no comercial, restringe uso en producción/operación de vehículos y establece obligaciones de atribución/distribución. No se intentó descargar datos protegidos ni usar credenciales ajenas. Para continuar, el propietario debe iniciar sesión en `https://waymo.com/open/` y aceptar personalmente los términos; después se podrá configurar acceso remoto seguro en el entorno de cómputo. Fuentes: `https://waymo.com/open/terms/`, `https://waymo.com/open/download/`, `https://waymo.com/open/about/`.
- La ficha oficial UrbanSyn y HF confirman que existen las cuatro modalidades y los formatos esperados. UrbanSyn no aporta splits ambientales verificados de día/noche/lluvia/niebla ni clase explícita de carril; sus resultados no cubren por sí solos robustez meteorológica real ni segmentación de carriles. Las perturbaciones sintéticas deben reportarse aparte. Antes de fijar definitivamente la licencia, revisar el texto íntegro de los términos del sitio oficial, porque la página y su redacción resumida no son completamente consistentes.
- No se cambió el dataset principal ni se migraron loaders; no hubo entrenamiento, checkpoints ni métricas. Los datos de prueba solo se descargarán en runner remoto temporal, nunca al teléfono.
- Próximo paso: consultar el resultado real del workflow UrbanSyn; si falla, corregir según logs. En paralelo, el usuario debe aceptar los términos de Waymo desde su cuenta si desea que probemos el acceso autenticado. Mantener PR #3 abierta y en draft.


### Nueva auditoría de acceso y cobertura de datasets alternativos — 2026-11-21

El usuario indicó que no puede acceder a Waymo y pidió probar acceso a Cityscapes, BDD100K, KITTI y alternativas antes de recomendarlas. Se volvió a consultar el registro antes de investigar.

#### Evidencia de acceso obtenida

- **A2D2 (Audi):** documentación oficial y AWS Open Data Registry consultados. Ambos indican que el bucket S3 es público y permite listar/descargar sin cuenta AWS (--no-sign-request); existe un mirror extraído con archivos individuales y verificación por CHECKSUMS.txt. La web oficial confirma 41.277 fotogramas anotados, segmentación semántica y de instancias, cajas 3D y 6 cámaras. No se logró completar desde las herramientas de esta sesión una petición de listado/descarga al endpoint S3: el navegador web no pudo abrir el host S3 y el contenedor de ejecución carece de DNS/red externa. Por tanto, **acceso anónimo respaldado por fuente oficial, pero muestra binaria aún no descargada/decodificada en esta sesión**. Fuentes: https://a2d2-dataset.github.io/ ; https://registry.opendata.aws/aev-a2d2/.

- **UrbanSyn:** la ficha pública de Hugging Face y la página oficial cargan sin login y describen RGB, segmentación semántica, panoptic instances y bbox2D. Los endpoints directos de ss.zip y panoptic.zip del mirror respondieron como application/zip (el lector web no puede procesar ZIP); el enlace RGB expiró por timeout. Esto acredita que los endpoints de etiquetas responden, pero no que se haya descargado/validado el contenido binario. El preflight del repositorio sigue sin ejecución confirmada; el conector disponible no pudo consultar la colección de Actions de este repositorio privado y el entorno de contenedor no tiene conectividad DNS. **No declarar PASS**. UrbanSyn no tiene clase específica de marcas de carril ni splits reales etiquetados por día/noche/lluvia/niebla. Su ficha HF declara CC BY-SA 4.0, mientras el sitio oficial formula la licencia como CC Attribution-Commercial-ShareAlike 4.0; confirmar la licencia aplicable con el proveedor antes de redistribuir o fijarla en el informe. Fuentes: https://huggingface.co/datasets/UrbanSyn/UrbanSyn ; https://www.urbansyn.org/.

- **ADUULM:** la documentación pública de su repositorio confirma 12 clases semánticas (incluye peatón, ciclista, vehículos, señales y semáforos), y una tarea separada de drivable-area con 7 clases de carril; documenta test en condiciones adversas. Sin embargo, el propio README remite a la página de descarga de la Universidad de Ulm y ese enlace devuelve 404 en la comprobación actual. No recomendar como fuente operativa hasta hallar y verificar un mirror autorizado. Fuente: https://github.com/uulm-mrm/aduulm_dataset_tools.

- **ACDC:** documentación oficial confirma 4.006 imágenes etiquetadas repartidas entre niebla, noche, lluvia y nieve, con panoptic semantic labels de 19 clases y benchmark de semantic/object detection/panoptic. La licencia exige aceptación individual, es solo para investigación no comercial y prohíbe redistribuir el dataset o versiones modificadas. El endpoint oficial /download devolvió 404 Not Found en la comprobación actual. Mantener como candidato de cobertura, pero **no como fuente de datos actualmente validada**. Fuentes: https://acdc.vision.ee.ethz.ch/ ; https://acdc.vision.ee.ethz.ch/overview ; https://acdc.vision.ee.ethz.ch/license.

- **SHIFT (SysCV/CVPR 2022):** no confundir con el dataset Shifts de predicción de trayectorias alojado en shifts.ai. SHIFT de SysCV sí es relevante: sintético, panoptic/semantic, cajas 2D/3D, clases de agentes y variaciones de hora, lluvia, niebla y nubosidad; incluye categorías finas de vehículos. Su DevKit público ofrece descargas selectivas por vista, modalidad, split y frecuencia. No obstante, la página/file server oficial han tenido incidencias HTTP 502 documentadas en issue pública de enero de 2026; la web oficial tampoco pudo abrirse desde la herramienta actual. **Acceso real pendiente**, no recomendar todavía como base descargable. Fuentes: https://github.com/SysCV/shift-dev ; https://openaccess.thecvf.com/content/CVPR2022/html/Sun_SHIFT_A_Synthetic_Driving_Dataset_for_Continuous_Multi-Task_Domain_Adaptation_CVPR_2022_paper.html ; https://github.com/SysCV/shift-dev/issues/79.

- **Cityscapes:** se confirmó en términos oficiales que la descarga requiere registro y que solo se autoriza a personas afiliadas a una entidad con interés científico; la aprobación puede tardar días y puede ser rechazada. No apto bajo la restricción actual del usuario. Fuente: https://www.cityscapes-dataset.com/license/.

- **KITTI:** página oficial de descarga exige registro, propósito de uso y email institucional (ej. .edu). No apto bajo la restricción actual. Fuente: https://www.cvlibs.net/datasets/kitti/user_login.php.

- **BDD100K:** documentación oficial confirma que conceptualmente cubre imágenes, detección, carriles, semántica, instancias y atributos weather/scene/timeofday en labels de vídeo. Pero el host oficial dl.cv.ethz.ch devolvió 502 en la comprobación actual y ya existe evidencia previa de 403 para el paquete oficial de etiquetas de instancia; el mirror HF semántico y muestra no oficial de instancias no reemplazan anotaciones oficiales completas. No se puede afirmar acceso completo ni cambiar a BDD100K como fuente principal hasta superar un preflight autorizado de imágenes + labels de instancia + splits.

- **EuroCity Persons:** portal actual indica que el acceso a sus paquetes exige cuenta, email institucional y prueba de afiliación, con revisión manual. Además está centrado en peatones y no cubre el proyecto completo. Fuente: https://eurocity-dataset.tudelft.nl/.

#### Conclusión metodológica y recomendación provisional

- No se encontró ni se verificó todavía un dataset único que simultáneamente sea descargable sin credenciales desde esta sesión y cubra de forma demostrable semántica multiclase, máscaras de instancias, detección, carriles, señales y particiones reales día/noche/lluvia/niebla.
- **A2D2 es el candidato real más viable por acceso público oficialmente documentado** y por su cobertura de segmentación semántica/instancias y objetos viales; su taxonomía semántica incluye marcas de carretera (líneas sólidas/discontinuas, paso peatonal), y tiene categorías de peatones, bicicletas, vehículos y señales. No hay evidencia suficiente aquí de atributos de condición por imagen para estratificar rigurosamente día/noche/lluvia/niebla.
- **UrbanSyn es buen candidato técnico complementario** para desarrollar y comparar DeepLabV3+ vs Mask R-CNN/detector con un esquema coherente, pero es sintético, no tiene carril explícito ni etiquetas reales de clima/hora.
- **SHIFT (SysCV) sería el complemento más alineado para condiciones controladas sintéticas**, pero su servidor de datos no está verificado disponible.
- ACDC sería una buena fuente de evaluación adversa real, pero el endpoint de descarga está devolviendo 404 y su licencia es no comercial.
- No se debe declarar cobertura real de noche/lluvia/niebla a partir de aumentos sintéticos. Si no se recupera acceso a ACDC/SHIFT/BDD100K, documentar que la robustez se prueba mediante corruptions sintéticas y que no equivale a evaluación de campo real.
- No se descargó ningún dataset completo ni una muestra binaria validada de A2D2; no se inició entrenamiento ni se modificó el pipeline. La validación remota UrbanSyn sigue pendiente de consultar Actions.
- Próximo paso recomendado: conseguir una ejecución remota con conectividad S3 para listar A2D2 y recuperar una sola imagen + su máscara semántica/instancia, comprobar checksum y clases; después evaluar si el esquema y licencia permiten adaptar loaders. En paralelo, repetir prueba de disponibilidad de ACDC/SHIFT antes de incorporarlos. No fusionar PR #3.


### Preflight remoto de acceso anónimo A2D2 — 2026-11-22

- El usuario autorizó probar A2D2 con una muestra remota pequeña, sin descargar nada al teléfono ni descargar el dataset completo.
- Se volvió a comprobar la documentación oficial. El sitio de A2D2 y AWS Open Data Registry identifican el bucket extraído recomendado `s3://audi-autonomous-driving-dataset/`, región `eu-central-1`, acceso AWS CLI anónimo sin cuenta y archivos individuales con `CHECKSUMS.txt`. El bucket de archivos tar original es distinto (`aev-autonomous-driving-dataset`) y se evita para este preflight. Fuentes: https://a2d2-dataset.github.io/ y https://registry.opendata.aws/aev-a2d2/.
- Se añadió `scripts/validate_a2d2_s3_sample.py`: usa boto3 con firma UNSIGNED, lista un máximo acotado de prefijos/secuencia y objetos, busca un par RGB + máscara semántica front-center, descarga solo esos dos objetos (máximo 80 MiB cada uno) en directorio temporal, valida decodificación Pillow, dimensiones y hashes SHA-256. No usa tar ni snapshot completo. Genera `a2d2_s3_preflight_report.json`.
- Se añadió `.github/workflows/validate-a2d2-s3-sample.yml`: ejecuta el script en GitHub Actions al modificar el script/workflow o manualmente; sube el informe como artifact durante 14 días. Commits: script `870a6ef9fe3ac3ffd6d50bf0185ade492048f97d`; workflow `8d2b0b4943bcbcd8f5cab0521f189e42964cd097`.
- **Ejecución aún no confirmada:** la herramienta de GitHub disponible solo devuelve runs asociados a pull requests y no devolvió una ejecución para el commit de workflow. No se ha podido consultar la colección general de Actions del repositorio privado ni disparar `workflow_dispatch` con las herramientas disponibles. Por ello no afirmar que S3 respondió ni que la muestra se descargó; el workflow está comprometido y configurado, pendiente de obtener el resultado real de Actions.
- **Alcance de anotaciones:** el preflight actual verifica RGB + máscara semántica; registra claves de archivo que parezcan relacionadas con instancias/label3D como pistas, pero no certifica todavía el formato ni la decodificación de las máscaras de instancias. La documentación y el paper oficial describen anotaciones de instancias para participantes del tráfico; se requiere inspeccionar una muestra concreta/formato antes de afirmar compatibilidad directa con Mask R-CNN. Tampoco se ha confirmado metadata para estratificar día/noche/lluvia/niebla.
- **Precaución técnica:** el estado esperado PASS del script significa únicamente que se logró leer una muestra RGB/semántica con dimensiones coincidentes; no valida el conjunto completo, las instancias, la detección, las condiciones ambientales ni la licencia más allá de la atribución/CC BY-ND 4.0 publicada.
- No se ha descargado dataset completo, no se modificaron loaders ni pipeline de entrenamiento, no se entrenó ningún modelo y no hay métricas/checkpoints nuevos.
- Próximo paso: revisar la ejecución `Validate A2D2 anonymous S3 sample` en GitHub Actions y su artifact/logs; si pasa, extender el preflight a las anotaciones de instancia/detección y verificar checksums contra `CHECKSUMS.txt`. Si falla por estructura/timeout, corregir con evidencia de los logs. Mantener PR #3 abierta y en draft; no fusionar.


### Adopción de estrategia multidataset A2D2 + UrbanSyn + SHIFT — 2026-11-22

El usuario aprobó utilizar la combinación recomendada para cubrir las tareas del Equipo 2. Esta estrategia sustituye BDD100K como dataset principal activo; BDD100K/Cityscapes quedan como referencias heredadas, no como flujo actual.

#### Decisión y distribución de responsabilidades

- **A2D2:** dominio real principal para semántica y, tras validar el formato, instancias/detección. No hay todavía metadata por imagen verificada para separar de forma fiable día/noche/lluvia/niebla.
- **UrbanSyn:** fuente sintética principal para entrenar/comparar semántica (19 clases), panoptic instances de clases dinámicas y cajas 2D. No contiene una clase dedicada a carriles ni escenarios meteorológicos reales.
- **SHIFT (SysCV):** complemento de evaluación de domain shift sintético; el DevKit oficial declara grupos RGB, semseg, detección 2D e instance segmentation 2D. La descarga usa endpoints oficiales seleccionables por vista/split/frecuencia; el servidor debe probarse.
- Se creó `docs/ESTRATEGIA_MULTIDATASET.md` con distribución de tareas, ontología conceptual, protocolos de split, métricas, licencias y puertas obligatorias antes del entrenamiento.
- Se actualizó README y protocolo experimental para dejar clara la nueva estrategia; se marcaron las secciones BDD100K como heredadas/no activas.

#### Auditoría de preflights anteriores

- **A2D2:** workflow run `44965195376` falló en la búsqueda de una ruta `/label/` asumida por el script. Sin embargo, confirmó acceso anónimo al bucket y devolvió cuatro raíces: `camera_lidar/`, `camera_lidar_semantic/`, `camera_lidar_semantic_bboxes/` y `camera_lidar_semantic_instance/`. No se descargó ni validó una anotación. Se corrigió el script para inspeccionar las rutas reales de semántica/instancia y sus sidecars JSON, sin asumir que el JSON sea una máscara.
- **UrbanSyn:** workflow run `44963969661` encontró 7.539 archivos por modalidad, pero cero muestras emparejadas porque el script usaba stems completos distintos (`rgb_0001`, `ss_0001`, `panoptic_0001`, `bbox2d_0001`). Se corrigió el emparejamiento por ID numérico, se añadieron validaciones del canal de clase panoptic y se registró el conflicto de licencia: HF declara CC BY-SA 4.0 y el sitio oficial describe CC BY-NC-SA 4.0. No se había descargado una muestra en esa ejecución.
- **SHIFT:** se añadieron `scripts/validate_shift_access.py` y `.github/workflows/validate-shift-access.yml`. Comprueban con HTTP HEAD, sin descargar archivos de datos, los endpoints oficiales de RGB, semseg e instance labels para una vista/split acotados. El resultado aún no se ha consultado.
- La inspección del DevKit SHIFT confirma que el descargador oficial declara CC BY-NC-SA 4.0 y permite seleccionar vista, grupos, split y frecuencia; el script no debe descargar conjuntos completos durante el preflight.
- La ejecución CI general `44965212000` (push) y el check de PR `44965214601` concluyeron success en el HEAD anterior `56cd28c`. Esto solo valida tests de código existentes, no los datos.

#### Cambios escritos en la rama

- `scripts/validate_urbansyn_sample.py`: emparejamiento por ID numérico; validación de clases dinámicas del canal azul panoptic; licencia marcada como revisión pendiente.
- `scripts/validate_a2d2_s3_sample.py`: inspección de `camera_lidar_semantic/` y `camera_lidar_semantic_instance/`, descargando como máximo una imagen PNG y su JSON sidecar por raíz para inspección estructural.
- `scripts/validate_shift_access.py` y workflow: preflight de endpoints sin descarga.
- `docs/ESTRATEGIA_MULTIDATASET.md`: nuevo plan experimental activo.
- `README.md` y `docs/PROTOCOLO_EXPERIMENTAL.md`: actualizados para reflejar la combinación y marcar BDD100K como legado.
- Commits de esta intervención: `c08092aae4e84ad765fb8b0cc72e042e1d5fd5f0` (UrbanSyn), `ca28be1fbf4bc14cb5f138dd6153f317c045ebee` (A2D2), `607e709749c9119bd7a0691271a446ffcf06956f` (SHIFT script), `39ee28bcacda0bceec3e26502f7cdcb5a040a3d8` (SHIFT workflow), `490159c3019d5c9d0b3e6cca7f9c825d88ce3801` (estrategia).

#### Estado operativo y próximos pasos

- No se ha descargado ningún dataset completo.
- No hay entrenamiento, checkpoints ni métricas experimentales de esta combinación.
- `RUN_TRAINING=False` permanece obligatorio.
- Próximo paso: consultar las ejecuciones nuevas de UrbanSyn/A2D2/SHIFT; corregir según logs; después decodificar las etiquetas y construir el mapeo de clases. Solo con los tres preflights y pruebas de adaptadores aprobados se autoriza preparar el entrenamiento.
- PR #3 debe seguir abierta, en draft y sin fusionar.


### Resultados de validación remota y estado de datos — 2026-11-22

#### A2D2
- Workflow [44971559558](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971559558) y la versión extendida [44971681934](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971681934) terminaron success.
- Se descargó desde S3 anónimo una imagen RGB y su máscara semántica: 1920×1208; dimensiones iguales; RGB PNG 3,817,263 bytes; máscara RGB PNG 71,403 bytes, 21 colores. SHA-256 imagen `1ea14036742fe8b453add67ce6a09b7f306de21d2a0906c90568e1e7b7ec15cc`; máscara `43a7a453fe632228d181f06673fc7c9adfd16f19060f70ef31161138d2c89666`.
- Se descargó `camera_lidar_semantic/class_list.json`: 55 colores/clases. La muestra mapea clases de superficie y participantes, incluyendo `Car 1-4`, `Bicycle 1-4`, `Pedestrian 1-3`, `Truck 1-3` y `Solid line`.
- La ruta explorada de `camera_lidar_semantic_instance` no contenía PNGs en `label/cam_front_center`. A2D2 documenta instance segmentation generada desde etiquetas semánticas, con subclases para participantes; queda pendiente validar conversión de componentes a máscaras individuales.
- Se actualizó el script para inspeccionar el class map y buscar las subclases.

#### UrbanSyn
- Workflow [44971557432](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971557432) success: 7.539 IDs completos; se descargaron dos muestras, RGB/semántica/panoptic/bbox2D, resolución 2048×1024. Semántica en RGB triplicado y canal de clase panoptic verificados.
- Preflight positivo solo para esas dos muestras. Licencia HF CC BY-SA 4.0 frente a página oficial CC BY-NC-SA 4.0: revisar antes de redistribuir/derivar.

#### SHIFT
- Workflow de endpoints oficiales [44971481786](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971481786) falló por DNS/NXDOMAIN del host `dl.cv.ethz.ch`.
- Se encontró espejo HF parcial `KevinConnorLee/SHIFT`; workflow [44971720763](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971720763) success. Tiene 21 archivos, solo `discrete/videos`, sin `continuous/`. `val/front` ocupa 15.7 GB; archivos: img.tar 9.62 GB, semseg.tar 3.56 GB, det_insseg_2d.json 954 MB, seq.csv 19.7 kB.
- `seq.csv` confirma columnas `start_weather_fine` y `start_timeofday_fine`; primeras filas incluyen small rain/night, small fog/night, heavy fog/noon y mid rain/noon.
- El primer preflight solo leyó 16 MiB de cada tar y no pudo extraer un video completo. Se añadió un segundo preflight con HTTP Range y límite de 64 MiB por primer miembro MP4; workflows [44971805203](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971805203) y posterior revisión están pendientes.
- HF marca el mirror como MIT, pero el DevKit original marca CC BY-NC-SA 4.0. No asumir relicenciamiento; revisar términos y no redistribuir.

#### Próximos pasos
1. Revisar el resultado del preflight SHIFT por rango y confirmar video RGB/semseg emparejado.
2. Implementar pruebas de conversión A2D2 RGB-colormap a IDs semánticos y subclases de instancia a máscaras por objeto; verificar connected components.
3. Crear adaptador UrbanSyn panoptic RGB (R/G instance ID, B class ID) a máscaras/targets Mask R-CNN y pruebas con muestras.
4. Crear ontología común solo para intersección de etiquetas equivalentes; documentar clases exclusivas y ignore.
5. Mantener `RUN_TRAINING=False` hasta completar puertas anteriores y revisar licencias.
6. No descargar conjuntos completos; las pruebas se ejecutan remotamente y de forma acotada.
7. PR #3 permanece abierta, draft y sin fusionar.


### Seguimiento final de esta intervención — 2026-11-22

- README actualizado: A2D2/UrbanSyn con preflights semánticos positivos; SHIFT espejo parcial y muestra RGB/semseg pendiente.
- El preflight SHIFT con HTTP Range tuvo dos fallos de código corregibles: (1) el primer workflow no instaló OpenCV; (2) el siguiente identificó el primer miembro TAR como directorio `./`, no como MP4. Se corrigió el script para instalar OpenCV en workflow y saltar directorios TAR.
- Último script SHIFT: commit `5f54e40e116a2b4a516ef829d281e151d625da78`. Workflow asociado [44971898884](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971898884) estaba en ejecución al cerrar esta actualización; no declarar resultado hasta consultarlo.
- El workflow de pruebas de código [44971898853](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44971898853) también estaba en ejecución. Los checks anteriores no sustituyen este resultado final.
- Entrenamiento permanece desactivado. No se han descargado datasets completos ni se han generado checkpoints.


### Validación de video SHIFT y lectura de A2D2 paper — 2026-11-22

- Workflow [44972034973](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972034973) success: se extrajo por HTTP Range el primer video RGB y semseg del espejo SHIFT. Ambos `eba5-a5bd.mp4`, 501 frames, 1280×800; RGB 16,770,040 bytes a 10 FPS y semseg 5,847,998 bytes a 25 FPS. Metadata `seq.csv`: small fog, sunrise/sunset. No usar para métricas hasta resolver desfase FPS/alineación temporal.
- Se actualizó `scripts/validate_shift_hf_mirror.py` para separar muestra decodificada de alineación temporal; commit `9c0e866691572ba1c0a2fcd9e5bec644fb70e61f`. Workflow de nueva versión pendiente al momento de la actualización.
- Paper oficial A2D2 consultado: 41.277 imágenes con semántica e instancia para 38 categorías; instancias derivadas de semántica, diferenciando instancias adyacentes con subclases Car 1–4, etc.; no adyacentes pueden reutilizar subclase. 12.497 frames frontales con cajas 3D. El paper indica captura diurna; sin metadata por imagen para estratificar lluvia/noche.
- A2D2 se utilizará como dominio real diurno, semántica, lane markings y fuente de subclases para reconstruir instancias por componentes conectados. Este último paso requiere pruebas de oclusiones y fragmentación antes de entrenar.
- UrbanSyn: fuente oficial confirma >7.5k imágenes, semántica de 19 IDs, panoptic y bbox2D solo para objetos dinámicos; RGB 2048×1024; panoptic RG=instance ID y B=class ID. No ofrece clase dedicada de carril. Licencia oficial CC BY-NC-SA 4.0 vs metadatos HF CC BY-SA 4.0.


### Cierre de la intervención de adopción multidataset — 2026-11-22

- Se documentó en `docs/ESTRATEGIA_MULTIDATASET.md` y `docs/PROTOCOLO_EXPERIMENTAL.md` la evidencia de las tres fuentes y sus limitaciones.
- Se ajustó el preflight SHIFT para reportar FPS y estado de alineación temporal por separado. Commit del script: `9c0e866691572ba1c0a2fcd9e5bec644fb70e61f`.
- Workflow previo de SHIFT [44972034973](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972034973) success, pero el informe muestra 10 FPS RGB frente a 25 FPS semseg. Mismo miembro de archivo, resolución 1280×800 y 501 frames; el CSV indica small fog y sunrise/sunset. No calcular métricas hasta resolver sincronización.
- Workflow del script con reporte explícito de FPS [44972103974](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972103974) estaba en progreso al cierre.
- Tests Python más recientes [44972130092](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972130092) y [44972127015](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972127015) estaban en progreso; no declarar CI final aprobado.
- Último commit de README antes de este registro: `58710c8b16f10b252473cf688d4bc56f0ee0fe16`.
- PR #3 comprobada: abierta, draft, sin merge; HEAD coincide con la rama.
- **Entrenamiento sigue desactivado**; no se descargó ningún dataset completo ni se generó checkpoint.


### Consulta de preparación para descarga y entrenamiento — 2026-11-22

- Se revisó el registro antes de responder y se volvió a consultar GitHub Actions y PR #3.
- CI Python [44972159537](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972159537) y [44972155622](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972155622) terminaron success en el HEAD previo; esto acredita tests de código existentes, no los adaptadores multidataset (aún pendientes).
- SHIFT preflight [44972103974](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44972103974) terminó success: extrajo por HTTP Range un video RGB y su semseg desde el espejo. Coinciden nombre, 1280×800 y 501 frames; difieren 10 FPS y 25 FPS. Metadata de secuencia: small fog, sunrise/sunset. Estado correcto: PASS_DECODED_SAMPLE_ALIGNMENT_PENDING; no se debe utilizar en métricas hasta comprobar sincronización.
- Estado de las fuentes:
  - A2D2: muestra semántica real aprobada, falta implementar/probar reconstrucción de instancias por subclases/componentes, inspeccionar cobertura y definir split.
  - UrbanSyn: dos muestras RGB/semseg/panoptic/bbox aprobadas, falta adaptador de máscaras/targets, validar más muestras/splits y aclarar discrepancia de licencia oficial/HF.
  - SHIFT: muestra de vídeo RGB/semseg decodificada, falta sincronización temporal; espejo parcial de validación, no dataset de entrenamiento.
- Faltan implementar y probar: adaptadores A2D2 y UrbanSyn; ontología común e ignore map; loaders y splits reproducibles; preflight de cobertura/clases/pares; smoke tests forward/backward de DeepLab y Mask R-CNN con targets reales; estimación de almacenamiento y estrategia de descarga por lotes; revisar licencias y condiciones.
- Para iniciar entrenamiento, primera descarga acotada solo de los subconjuntos train/val que alimentarán UrbanSyn semántica/panoptic y A2D2 semántica. No descargar SHIFT completo; solo un subconjunto pequeño para evaluación después de corregir alineación. Dataset en almacenamiento temporal de Colab, checkpoints/resultados en Drive.
- RUN_TRAINING=False se mantiene. No hay checkpoints, métricas ni entrenamiento.
- PR #3 sigue abierta, draft y sin fusionar.


### Implementación inicial de adaptadores y pruebas de modelos — 2026-11-22

- Se consultó primero este registro y se verificó la rama `urban-models-and-benchmark` y PR #3.
- Se añadió `src/data_adapters.py`:
  - A2D2: `class_list.json` RGB→nombre, mapeo a IDs canónicos, normalización de clases y reconstrucción de instancias con connected components por color/subclase.
  - UrbanSyn: decodificación semántica de máscara de un canal/RGB triplicado; panoptic con ID de instancia R/G y clase B; extracción de máscaras, labels, cajas y áreas.
  - Conversión de los resultados a targets compatibles con Torchvision Mask R-CNN.
- Se añadió `tests/test_multidataset_adapters.py` con pruebas sintéticas de ambos decodificadores y del contrato de targets.
- Se añadió smoke test CPU de DeepLabV3+ ResNet-50 y Mask R-CNN ResNet-50-FPN: forward, pérdidas y backward con datos sintéticos pequeños. Esto no representa entrenamiento con datasets ni métricas de precisión.
- Commits: adaptador `2b0f992d384f8ed8478ae3fc79b6e64329dcfd2f`; pruebas `56120e2e5d6dd5619ac7e47db53e91f54cff0eb5`; corrección regex de subclases A2D2 `74a795fdbb69c244aee5d7447082d23ce7f73536`.
- GitHub Actions Python tests push run `44973434410` y PR run `44973436510` iniciados para validar el HEAD de la rama; ambos estaban en progreso al registrar esta entrada. No declarar PASS hasta consultar conclusión/logs.
- Alcance aún incompleto: los decodificadores están implementados, pero faltan loaders de archivos/manifiestos/splits y pruebas sobre muestras remotas reales A2D2/UrbanSyn; verificar mapeo completo de clases, oclusiones/fragmentación y licencia UrbanSyn. SHIFT sigue fuera de métricas por desalineación FPS.
- `RUN_TRAINING=False`; no se descargaron datasets completos, no se ejecutó entrenamiento real y no hay checkpoints ni métricas experimentales.
- PR #3 se mantiene abierta y en draft, sin fusionar.


### Adaptadores A2D2/UrbanSyn y smoke tests de modelos — 2026-11-22 (continuación)

- Se completó `src/data_adapters.py` con:
  - `load_a2d2_class_list`, `decode_a2d2_semantic`: parseo del mapa RGB de A2D2 y conversión a IDs canónicos con ignore=255.
  - `decode_a2d2_instances`: detección de subclases participantes (Car 1–4, Pedestrian 1–3, Bicycle 1–4, etc.) y separación de componentes conectados; no se trata el color/subclase como ID global.
  - `decode_urbansyn_semantic`: máscaras de IDs de un canal o RGB triplicado y mapeo fuente→canónico explícito.
  - `decode_urbansyn_panoptic`: decodificación de instancia R*256+G y clase B; extrae máscaras, labels, cajas XYXY, área e iscrowd.
  - `to_torchvision_target` y `detection_collate_fn` para targets y batches variables de Mask R-CNN.
  - Loaders basados en manifiesto: `A2D2SemanticDataset`, `A2D2InstanceDataset`, `UrbanSynSemanticDataset`, `UrbanSynInstanceDataset`; soportan resize correcto y normalización adecuada para cada arquitectura.
- Se amplió `tests/test_multidataset_adapters.py`: pruebas de mapeo/ignore A2D2, componentes separados y vacío, semántica UrbanSyn, panoptic, targets Torchvision, loaders con archivos temporales, collate de targets variables y smoke training de DeepLabV3+ y Mask R-CNN con backward.
- Primera ejecución CI en commit `03c801a` reveló dos defectos (regex de subclase A2D2 y área de cero instancias). Ambos se corrigieron y se añadieron regresiones.
- Evidencia CI: push run [44973632150](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44973632150) y PR run [44973635321](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44973635321) terminaron success; el log de run 44973632150 registra **45 passed in 12.37s**, incluida la ejecución de smoke test de ambos modelos y loaders. El workflow también pasó la validación remota BDD100K heredada; eso no valida A2D2/UrbanSyn reales.
- Se añadió concurrencia `cancel-in-progress` al workflow de tests para cancelar ejecuciones duplicadas/superadas. Se añadió prueba específica del collate después de esos 45 tests; el CI del HEAD final `bd0569bca8b2504a68f572a0569ae41fb6de0daf` está en ejecución (push run [44973729238](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44973729238), PR run [44973733099](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44973733099)); no afirmar aún el resultado de esa última prueba.
- La rama HEAD es `bd0569bca8b2504a68f572a0569ae41fb6de0daf`. PR #3 comprobada abierta, draft y sin merge.
- Alcance pendiente antes de entrenamiento de producción: ejecutar adaptadores sobre varias muestras reales remotas A2D2/UrbanSyn; versionar mapeo de las 19 clases UrbanSyn y revisar las 55 clases A2D2; construir manifiestos oficiales train/val sin fuga; inspeccionar fragmentación/oclusiones; resolver discrepancia de licencia UrbanSyn. SHIFT permanece fuera de métricas por alineación temporal 10/25 FPS no resuelta.
- `RUN_TRAINING=False`. No se ha iniciado entrenamiento de producción, no hay checkpoints ni métricas de precisión. Los smoke tests usan datos sintéticos pequeños y prueban únicamente el contrato de modelo/gradientes.


### Validación de adaptadores con muestras reales — 2026-11-22

- Se revisó este registro antes de comenzar. Se ampliaron los workflows remotos existentes para ejecutar los decodificadores de producción sobre muestras reales de los orígenes oficiales; sin descargar conjuntos completos.
- A2D2 workflow [44974096279](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974096279): **success**. Una muestra frontal real de 1920×1208 pasó `decode_a2d2_semantic` y `decode_a2d2_instances`. Se leyó class_list de 55 entradas; IDs canónicos observados 2,3,5,6,7,12 e ignore 255; 66 componentes reconstruidos; labels 3,5,6,7; arrays masks [66,1208,1920] y boxes [66,4]. Esto es una muestra, no validación de todo A2D2 ni de oclusiones.
- UrbanSyn workflow [44974144391](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974144391): ampliado para ejecutar semseg y panoptic adapters en dos muestras remotas completas, incluyendo validación de tamaños y arrays de máscaras/cajas. Estaba en curso al escribir esta entrada; verificar conclusión antes de afirmar PASS.
- Se corrigió el sys.path de scripts de preflight para importar módulos de la raíz. Los fallos iniciales de esos nuevos workflows fueron import errors, no errores de decodificación.
- No se han creado aún manifiestos train/val ni descargado subconjuntos para producción. Faltan validación multi-muestra ampliada, revisión de oclusiones, versionado de la ontología completa y licencia UrbanSyn. SHIFT permanece fuera de métricas por desalineación 10/25 FPS.
- `RUN_TRAINING=False`; no se inicia entrenamiento de producción ni se generan checkpoints/métricas de precisión.
- PR #3 debe permanecer abierta y draft, sin fusionar.


### Cierre de validación con muestras reales — 2026-11-22

- UrbanSyn preflight [44974144391](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974144391) terminó **success**: mirror con 7,539 IDs y 7,539 pares completos en las cuatro modalidades; descargó únicamente dos muestras completas (0001 y 0002). Los decodificadores reales pasaron en ambas; panoptic generó 5 y 17 instancias respectivamente y arrays de máscaras/cajas con dimensiones consistentes. No equivale a validar la ontología canónica completa.
- A2D2 preflight [44974096279](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974096279) terminó **success**: muestra real 1920×1208, class list 55 entradas, decodificación semántica y reconstrucción de 66 componentes por connected components. Se verificaron labels 3,5,6,7; masks [66,1208,1920], boxes [66,4]. Una sola muestra: ampliar a varias secuencias y revisar fragmentación/oclusiones.
- Los workflows descargaron solo muestras acotadas en runners temporales; no se bajaron datasets completos ni se almacenaron en el teléfono.
- El preflight UrbanSyn registra 7,539 IDs completos en su índice remoto. Esto es cobertura del inventario de archivos del mirror, no prueba de calidad de anotaciones de todas las muestras.
- Se corrigió el estado pendiente de UrbanSyn en la documentación de estrategia.
- CI de Python para HEAD anterior al último cambio documental estaba en cola/en progreso (runs [44974186367](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974186367) y [44974181660](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974181660)); revisar el HEAD actual tras el registro.
- Siguiente bloque: ampliar A2D2 a múltiples muestras; verificar y versionar la ontología fuente→canónica de UrbanSyn/A2D2; determinar splits oficiales antes de generar manifiestos train/val; calcular tamaño del subset y preparar descarga remota a Colab/Drive. La discrepancia de licencia UrbanSyn y la sincronización SHIFT (10/25 FPS) siguen abiertas.
- RUN_TRAINING=False; no se inicia entrenamiento ni se crean checkpoints/métricas de precisión.
- PR #3 permanece abierta, draft y sin fusionar.


## 13. Preparación de subconjuntos reproducibles — 2026-11-22

Solicitud del usuario: preparar los subconjuntos reproducibles.

### Implementación guardada en la rama

- Se añadió `scripts/prepare_reproducible_subsets.py`.
- Se añadió `tests/test_reproducible_subsets.py` con pruebas de determinismo, agrupación por secuencia, límite por split y rechazo de IDs duplicados.
- Se actualizó `docs/ESTRATEGIA_MULTIDATASET.md` con el protocolo y comandos.
- El generador no descarga datos: solo consulta índices/metadatos remotos y escribe referencias JSONL.

### Política reproducible

- Semilla predeterminada: 2026.
- Asignación 80/10/10 train/val/test mediante SHA-256 de `seed:group_id`.
- Máximo predeterminado: 1.000 muestras por split; orden de selección estable por hash de ID.
- A2D2: solo pares front-camera RGB + semántica; grupo = secuencia, evitando repartir frames de una secuencia entre splits. Incluye URI, tamaño y ETag de RGB/máscara.
- UrbanSyn: solo IDs con RGB, semseg, panoptic y bbox2D completos; grupo = ID de muestra, con commit SHA de Hugging Face fijado. No se ha confirmado metadata de secuencia para agrupar más arriba.
- SHIFT queda fuera hasta resolver alineación temporal RGB/semseg.

### Limitaciones y estado real

- Los splits generados son experimentales y hash-deterministas, no particiones oficiales.
- El ETag/tamaño de A2D2 ayuda a detectar cambios, pero S3 no se ha fijado a un snapshot inmutable.
- UrbanSyn sigue sujeto a aclaración de licencia; el script no descarga ni redistribuye sus archivos.
- No se han generado manifiestos con el inventario completo todavía: eso requiere ejecutar el script en el entorno remoto con boto3/huggingface_hub y acceso a las fuentes. No se ha descargado ningún dataset completo.
- No se ha entrenado ningún modelo; `RUN_TRAINING=False`.
- PR #3 permanece abierta, draft y sin fusionar.

### Próximos pasos

1. Ejecutar pruebas CI del nuevo generador.
2. Lanzar generación de manifiestos en el entorno remoto (no en el teléfono), guardar JSONL y resúmenes en almacenamiento remoto persistente.
3. Auditar conteos y cobertura por clase, revisar splits y licencias; luego ajustar tamaños de subconjunto según VRAM/espacio disponibles.
4. Resolver SHIFT y licencia UrbanSyn antes de habilitar los experimentos que dependan de ellos.

- Se añadió workflow `.github/workflows/build-reproducible-subsets.yml` para ejecutar el generador remotamente y publicar un artifact de manifiestos por 30 días. Se dispara al cambiar el script/workflow y admite ejecución manual con semilla y límite configurables.
- Primera ejecución automática [44974469162](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974469162) quedó **queued** al registrar; todavía no hay manifiestos reales generados. CI de tests [44974469066](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974469066) también queued.

- Seguimiento al cierre: workflow de generación [44974469162](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974469162) pasó de queued a **in_progress**; la etapa de inventario remoto aún no ha terminado. Los manifiestos no están disponibles todavía. La suite de pruebas del HEAD más reciente [44974488452](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974488452) también sigue en ejecución.


### Comprobación de finalización de manifiestos — 2026-11-22

- Se consultó el estado real de GitHub Actions. El workflow de generación [44974469162](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974469162) terminó, pero su conclusión fue **cancelled**, no success. El job `manifests` fue cancelado durante el paso `Build remote-reference manifests`; el paso de subir artifacts quedó omitido. Por tanto, **no hay manifiestos generados ni artifact disponible que pueda darse por válido**.
- La ejecución de tests del HEAD actual [44974517462](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974517462) terminó **success**. Otra ejecución de tests del mismo HEAD [44974521446](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974521446) también terminó success.
- HEAD de `urban-models-and-benchmark`: `e134e73fe1d3755e9537d0823d1592efaf8519e4`. PR #3 sigue abierta, en draft y sin fusionar.
- Próximo paso: investigar por qué se canceló el job de manifiestos y relanzar una ejecución controlada; después auditar conteos, duplicados, emparejamiento de recursos y ausencia de fuga entre secuencias. No iniciar entrenamiento mientras no existan manifiestos validados.
- `RUN_TRAINING=False`; no hay entrenamiento de producción, checkpoints ni métricas experimentales.


### Investigación y corrección de la cancelación de manifiestos — 2026-11-22

- Se consultó primero este registro y se recuperaron los logs completos del job [44974469162](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44974469162).
- Causa confirmada: el paso `Build remote-reference manifests` estuvo ejecutándose desde 02:05:59Z hasta 03:06:03Z y GitHub reportó `The operation was canceled`; el workflow tenía `timeout-minutes: 60`. Por tanto, el job alcanzó el timeout de una hora. No hay evidencia de error de decodificación ni de fallo de tests en esa ejecución.
- Se optimizó `scripts/prepare_reproducible_subsets.py`: A2D2 ahora indexa los nombres/metadatos de máscaras una vez por secuencia y los empareja en memoria, en lugar de hacer un `head_object` por cada imagen. También pagina la enumeración de secuencias y emite progreso por secuencia.
- Se modificó `.github/workflows/build-reproducible-subsets.yml`: los inventarios A2D2 y UrbanSyn corren como jobs de matriz independientes, cada uno con timeout máximo de 360 minutos y artifact separado.
- Commits guardados en la rama: optimización A2D2 `b47bd63120a7d00c0d2ae355a59e445813c33b19`; workflow paralelo `42f8e7419cd052b4623475edc6f66c40e846bf1f` (HEAD observado al cierre).
- Nueva ejecución del workflow con ambos datasets: [44992977292](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992977292), dos jobs (A2D2 y UrbanSyn) en progreso al actualizar este registro. Ejecución intermedia del commit anterior [44992975111](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992975111) también se inició por el trigger push antes de que quedara aplicado el workflow paralelo; no tomarla como la validación final de la nueva configuración.
- CI Python del HEAD `42f8e7419cd052b4623475edc6f66c40e846bf1f`: runs [44992979167](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992979167) y [44992977459](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992977459) en progreso al cierre. No declarar tests aprobados hasta revisar sus conclusiones.
- PR #3 verificada: abierta, draft, sin fusionar; HEAD actualizado al commit `42f8e7419cd052b4623475edc6f66c40e846bf1f`.
- Aún no hay manifiestos confirmados ni artifacts validados. El siguiente paso es esperar/verificar ambos jobs, revisar artifacts y auditar conteos, duplicados, emparejamiento y fuga entre secuencias. Entrenamiento sigue desactivado; no se descargan datos completos ni se inicia entrenamiento.


### Verificación de generación y auditoría de manifiestos — 2026-11-22

- Se volvió a consultar este registro antes de revisar las ejecuciones.
- Workflow final de manifiestos [44992977292](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992977292): **success**. Ambos jobs terminaron correctamente y subieron artifacts separados:
  - A2D2: artifact [14742059955](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992977292/artifacts/14742059955), 207,323 bytes, SHA-256 del ZIP ca12a915bac4e597d8bf22a9d28a144d505a14cebb070d8459f553b55515dd97.
  - UrbanSyn: artifact [14741878951](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44992977292/artifacts/14741878951), 58,209 bytes, SHA-256 del ZIP 73e23edd6b49669d4c5cca1fc0f129928f24b3eea76812b74f6f10e2a242815b.
- Se descargaron ambos ZIP mediante la integración GitHub y se inspeccionaron los JSONL directamente:
  - A2D2: 1,000 train + 1,000 val + 1,000 test = 3,000 registros. 23 secuencias distribuidas 18 train / 3 val / 2 test. Cero IDs nulos, cero duplicados dentro o entre splits, cero solapamiento de group_id; cada fila incluye URI S3 para RGB y semántica y metadatos de tamaño/ETag. Split experimental por secuencia, no oficial.
  - UrbanSyn: 1,000 train + 751 val + 783 test = 2,534 registros. Cero IDs nulos, cero duplicados dentro o entre splits, cero solapamiento de group_id; registros con RGB, semseg, panoptic y bbox2D y revision HF 8599498aceee9072f1e067a4a4efed7f20b11809. Agrupación por sample ID porque no se verificó metadata de secuencia; no garantiza independencia por secuencia. Split experimental, no oficial.
  - Ambos ZIP contienen tres JSONL y un summary JSON. La auditoría no descargó ni decodificó las 5,534 muestras completas ni calculó distribución de clases.
- CI Python del HEAD: [44993021461](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44993021461) success; compileall, CLIs, validación BDD100K y **49 passed in 9.22s**. El run gemelo [44993016907](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44993016907) también success. Runs anteriores del commit 42f8e cancelados por concurrencia quedan reemplazados por estos checks satisfactorios del HEAD 6dd185b5200865997524b3fdc1b66dc9fd9ab33a.
- PR #3 sigue abierta, draft y sin fusionar; HEAD actual 6dd185b5200865997524b3fdc1b66dc9fd9ab33a.
- Conclusión: la generación de manifiestos sí terminó y los artifacts existen. No equivale a descargar los datasets ni validar el contenido de cada anotación. Antes de entrenar faltan: validar muestra más amplia y distribución por clase; revisar los 23 grupos A2D2 y sus proporciones; verificar independencia temporal/secuencias de UrbanSyn (o documentar limitación); resolver licencia UrbanSyn; descargar subconjunto acotado al almacenamiento remoto y ejecutar smoke tests con targets reales de manifiesto.
- RUN_TRAINING=False: no se ha iniciado entrenamiento de producción, no hay checkpoints ni métricas de precisión. PR #3 no se fusiona.


### Inicio de auditoría ampliada de clases y anotaciones — 2026-11-22

- Se consultó este registro al inicio de la intervención.
- Se añadió `scripts/audit_urban_annotations.py`: selección determinista de muestras de cada split (8 por split y dataset por defecto), descarga remota temporal de RGB/semántica A2D2 y RGB/semseg/panoptic/bbox2D UrbanSyn, histogramas de píxeles por color/clase, conteo de colores desconocidos, decodificación con adaptadores del proyecto, conteo de componentes/instancias, comprobación de dimensiones y acuerdo de clase semseg/panoptic en píxeles dinámicos. El informe distingue IDs fuente de nombres canónicos y conserva explícitamente pendiente la ontología oficial UrbanSyn.
- Se añadieron `tests/test_urban_annotation_audit.py` y `.github/workflows/audit-urban-annotations.yml`. El workflow descarga artifacts existentes por ID inmutable y ejecuta la auditoría en runner remoto; las muestras no se guardan en Git ni se transfieren al dispositivo del usuario.
- Se corrigieron tres defectos del propio workflow/script detectados por las primeras ejecuciones, no por los datos: (1) valores de inputs vacíos en disparo push; (2) directorios anidados al descargar artifacts; (3) falta de inserción de raíz del repositorio en `sys.path`. Primeros runs de auditoría [44994284828](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994284828), [44994341576](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994341576), [44994432572](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994432572), [44994454957](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994454957), [44994487722](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994487722) fallaron por esos defectos de orquestación/importación; no son fallos de calidad de las anotaciones.
- Se corrigió la ruta de importación y el aplanado de artifacts. Ejecución actual de auditoría [44994523923](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994523923): artifacts A2D2 y UrbanSyn descargados correctamente; paso `Audit class distributions and annotation consistency` en progreso al cierre. Aún no hay resultados de distribución/clases ni artifact de informe.
- CI de pruebas en HEADs intermedios se canceló por la concurrencia de pushes sucesivos. Runs de tests para HEADs recientes [44994529833](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994529833) y [44994523885](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994523885) estaban en progreso al cierre; verificar el run correspondiente al HEAD final antes de declarar PASS.
- Limitaciones de alcance: la auditoría muestrea 8 registros por split (24 por dataset), no toda la colección. A2D2 connected components siguen siendo una aproximación de instancias con riesgo de fragmentación por oclusión. UrbanSyn source class IDs se reportan numéricamente; no se les asignan nombres hasta confirmar documentación oficial. La discrepancia de licencia UrbanSyn sigue bloqueando su uso/publicación externa.
- HEAD esperado al cierre de los cambios: `77183b83234e51c4f0c5b4cb4abbc0f74fb1845c`; se añadieron después commits correctivos de workflow y script. Consultar HEAD actual y actualizar este punto tras los resultados. PR #3 debe permanecer abierta, draft y sin fusionar. `RUN_TRAINING=False`; no entrenamiento.

- Addendum de cierre de esta intervención: el HEAD de la rama avanzó a `7b3e602bc90b12c84140a1356cb2d0d29f39aa8d` al guardar este registro. La auditoría [44994523923](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994523923) seguía en el paso de inspección remota de muestras; los dos artifacts se descargaron correctamente. CI del HEAD actual [44994603507](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994603507) y [44994599244](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994599244) en cola al registrar. No declarar aún auditoría ni CI aprobados.


### Resultados de auditoría de clases/anotaciones — 2026-11-22

- Auditoría remota [44994523923](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994523923): **success**. Artifact [14743746648](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994523923/artifacts/14743746648), ZIP 3,389 bytes, SHA-256 `27a1f6680996d2651ae9f87d0e7ba7b947a7bdaab888749ae720e42efdeae929`. Informe descargado e inspeccionado.
- Alcance: 8 muestras deterministas por split x 3 splits x 2 datasets = 48 muestras; no es auditoría exhaustiva de los 5,534 registros.
- A2D2: 24 muestras (8/train, 8/val, 8/test), resolución 1920x1208; mapa oficial 55 entradas; cero colores no reconocidos. Histograma canónico de píxeles: bicycle 118,086; car 1,428,812; lane marking 637,819; person 30,333; sidewalk 1,005,336; traffic sign 705,723; truck 1,015,586. Total de píxeles mapeados a las siete clases 4,941,695 de 55,664,640 (8.88%); el resto se marca ignore por incluir clases fuera de la ontología objetivo, no porque se haya detectado corrupción. 268 componentes de instancia reconstruidos en total. Labels de instancia observados (IDs canónicos) 3,5,6,7. Limitación: connected components puede fragmentar objetos por oclusión/discontinuidad y no sustituye IDs nativos de instancia.
- UrbanSyn: 24 muestras (8 por split), resolución 2048x1024; aparecen todos los IDs semánticos 0..19 y panoptic IDs 0,11..18 en la muestra. Acuerdo medio de clase semseg/panoptic en píxeles dinámicos 0.9999927119 (99.9993%). 578 instancias panoptic decodificadas y 578 registros bbox2D en total; conteos coincidentes en las 24 muestras. Una muestra no tiene objetos dinámicos y correctamente produce 0 instancias y 0 cajas. No se asignan nombres a IDs 0..19: aún falta fuente oficial autoritativa para la ontología.
- La auditoría confirma consistencia interna de las muestras examinadas, no calidad global de todas las anotaciones ni independencia temporal de UrbanSyn. La licencia UrbanSyn sigue con declaraciones contradictorias; mantener revisión pendiente y no redistribuir/publicar datos derivados hasta resolverla.
- CI Python del commit de registro previo [44994630573](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994630573) y duplicado [44994627338](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44994627338): fallaron durante recolección de tests porque el módulo auditor importaba `boto3` en nivel superior, dependencia que no está en el entorno de tests. Compilación y validación de CLIs sí pasaron; no es fallo de datos ni de lógica de adaptadores. Se corrigió en commit `22288a46d10c5ddec6cc36e8cb416b5c860ac0b7` moviendo boto3/botocore y huggingface_hub a imports locales dentro de sus funciones de descarga. Esperar CI nuevo de este HEAD antes de declarar suite verde.
- Próximos pasos: confirmar CI; aumentar muestra especialmente en A2D2 y auditar fragmentación; incorporar clases A2D2 adicionales solo si responden a los requisitos del trabajo; identificar oficialmente ontología UrbanSyn y resolver licencia; luego validar loaders/targets reales antes de entrenamiento. `RUN_TRAINING=False`; PR #3 sigue abierta, draft y sin fusionar.


## 14. CI confirmado, ontología UrbanSyn y ampliación de auditoría — 2026-11-22

- Se consultó primero el registro de continuidad y se verificó PR #3 y las ejecuciones pendientes de CI.
- CI del HEAD previo `64f55277b3f61ebda42c984ba8741151914c4b7d`: workflow [44995209289](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995209289) terminó **success**. Los pasos de instalación de PyTorch CPU/dependencias, compileall, validación de CLIs, suite de tests y validación de muestras semánticas BDD100K pasaron. Runs [44995193658](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995193658) y [44995188685](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995188685) fueron cancelados durante la instalación de PyTorch; no se consideran fallos de código porque el run posterior del HEAD completó todos los pasos.
- Fuente oficial UrbanSyn (sitio del proveedor y README del dataset en Hugging Face) verificada: trainId 0–18 sigue las 19 clases Cityscapes y 19 es `unlabeled`. Nombres: road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle, bicycle, unlabeled. Panoptic aplica a Person/Rider/Car/Truck/Bus/Train/Motorcycle/Bicycle; bbox2D solo a objetos dinámicos, hasta 110 m y mayores de 150 px. UrbanSyn no tiene clase dedicada a lane marking.
- Se actualizó `docs/ESTRATEGIA_MULTIDATASET.md` con tabla de ontología fuente, distinción rider/bicycle y restricciones de bbox/panoptic. Commit: `72de77828cf025a7a5887148b895fda23738d58e`.
- Licencia: la página oficial del proveedor declara CC BY-NC-SA 4.0, mientras que Hugging Face muestra CC BY-SA 4.0. Se mantiene CC BY-NC-SA 4.0 como criterio conservador hasta aclaración escrita. No redistribuir datos ni derivados; la auditoría local y métricas agregadas quedan sujetas a los términos del proveedor.
- Se amplió el workflow `.github/workflows/audit-urban-annotations.yml` de 8 a 12 muestras por split y dataset (36 por dataset, 72 total), con timeout de 180 minutos. El cambio debe disparar una nueva auditoría por push; run esperado en el nuevo HEAD, pendiente de consultar. Commit: `ff1f39d5aedf116ac9b01eaa597ee8a55d2098f3`.
- La ampliación audita A2D2 y UrbanSyn en 12 muestras por split; no es un censo de los manifiestos. El informe anterior de 24 muestras por dataset permanece como evidencia anterior, no debe mezclarse con el resultado nuevo.
- Estado de entrenamiento: `RUN_TRAINING=False`; no se inicia entrenamiento ni se declaran métricas de modelos. PR #3 permanece abierta, draft y sin fusionar.
- Próximo paso: verificar el workflow de auditoría ampliada y su artifact; inspeccionar histogramas/cobertura por split, muestras con componentes fragmentados y consistencia de cajas. Después decidir si se amplía el subconjunto A2D2/ontología canónica y probar los loaders con manifiestos reales. Resolver licencia UrbanSyn con proveedor antes de redistribución.


### Seguimiento inmediato de ejecuciones — 2026-11-22

- Tras guardar la ampliación de auditoría se verificó que el workflow se disparó correctamente: [44995394741](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995394741), commit `ff1f39d5aedf116ac9b01eaa597ee8a55d2098f3`, estado **in_progress**. Checkout/setup-python completados; instalación de dependencias en curso; aún no se descargaron manifiestos ni comenzó la auditoría de 12 muestras/split. No hay artifact ampliado todavía.
- CI del commit `ff1f39d5...`: [44995396960](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995396960), estado **in_progress** (instalación PyTorch CPU). CI para HEAD de registro `02a7afeee305fa6e9f25d1e3a01cc4ff1907f952`: [44995406185](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995406185), también **in_progress**; otra ejecución [44995410143](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995410143) quedó pending. No declarar verde el HEAD actual hasta revisar una ejecución completada sobre él.
- Probe de archivo BDD100K del HEAD de registro [44995406197](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995406197) está **in_progress**.
- PR #3 verificada tras el commit de registro: abierta, draft, merged=false; head `02a7afeee305fa6e9f25d1e3a01cc4ff1907f952`. El campo mergeable temporalmente figura false mientras los checks se ejecutan; no se intentó fusionar.
- El resultado de auditoría ampliada y el estado final de CI quedan pendientes para la siguiente revisión. No entrenamiento ni descarga completa de datasets.


### Resultado de auditoría y corrección de tamaño de muestra — 2026-11-22

- Auditoría [44995394741](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995394741): **success**. Artifact [14742968559](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995394741/artifacts/14742968559), 3,389 bytes, SHA-256 `a0fa6d628c290a3f205f912be31b4e7949ce91aff6c52a48d05b265f88ad393e`. ZIP descargado y JSON inspeccionado localmente.
- Hallazgo importante: el informe indica `samples_per_split=8`, no 12. Causa confirmada en el workflow: aunque el input manual default era 12, el fallback del comando para eventos push seguía siendo `inputs.samples_per_split || '8'`. La ejecución auditó 8 train + 8 val + 8 test por dataset = 24 por dataset y 48 en total; por tanto no debe describirse como auditoría de 72 muestras.
- A2D2 (24 muestras, 1920x1208): 55 entradas de clase; cero píxeles de colores desconocidos. Conteo canónico agregado: bicycle 118,086; car 1,428,812; lane marking 637,819; person 30,333; sidewalk 1,005,336; traffic sign 705,723; truck 1,015,586. Total objetivo 4,941,695/55,664,640 píxeles (8.88%); 50,722,945 (91.12%) ignore por clases ajenas a ontología objetivo. 268 componentes reconstruidos; subclases fuente observadas con IDs canónicos 3,5,6,7. Connected components sigue siendo aproximación y puede fragmentar instancias.
- UrbanSyn (24 muestras, 2048x1024; revision HF `8599498aceee9072f1e067a4a4efed7f20b11809`): aparecen todos los IDs semánticos 0–19 y panoptic 0,11–18. Acuerdo medio por muestra semseg/panoptic en píxeles dinámicos 0.9999927119479173 (99.9993%), mínimo 0.9999370464482751. 578 instancias panoptic y 578 registros bbox2D; conteos coinciden en todas las muestras. La muestra sin objetos dinámicos produjo cero y cero. El informe todavía marca `class_names` no asignados; la taxonomía oficial se documentó por separado en estrategia. Licencia continúa `REVIEW_REQUIRED_CONFLICTING_DECLARATIONS`.
- Corrección aplicada: workflow `.github/workflows/audit-urban-annotations.yml` ahora usa fallback 12 en eventos push, commit `7201be2069333859577905f40678e721e889414b`. Esto dispara nueva auditoría [44995801143](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801143), estado **in_progress** al registrar; debe confirmar 12 muestras por split (72 total) y producir un artifact nuevo. No atribuirle resultados hasta inspeccionarlo.
- CI del HEAD previo `55015ce40dc6413f72912f6db5bcfb7b17ee4455`: [44995428234](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995428234) success. CI del HEAD actual `7201be2069333859577905f40678e721e889414b`: [44995801141](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801141) y [44995805671](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995805671) en progreso al cierre. Esperar una ejecución exitosa sobre HEAD actual.
- PR #3 permanece abierta, draft y merged=false; HEAD `7201be2069333859577905f40678e721e889414b`. No se inició entrenamiento; `RUN_TRAINING=False`.
- Próximo paso: comprobar finalización de [44995801143](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801143), inspeccionar JSON del nuevo artifact y verificar que indique 12 muestras por split para ambos datasets. Luego revisar CI sobre HEAD actual. No iniciar entrenamiento hasta completar validaciones de datos y licencia.


### Verificación final de auditoría ampliada y CI — 2026-11-22

- Se consultó primero este registro y se comprobó la rama, PR #3, ejecución de auditoría y CI.
- Auditoría remota [44995801143](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801143): **success**. Job único completado; artifact [14742929447](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801143/artifacts/14742929447), 4,054 bytes, SHA-256 `f482e7bb83d363bd924b79557f9ddd6380fa6f42fd0cc42d41a0bb3433a675d2`. ZIP descargado e inspeccionado; el JSON confirma `samples_per_split=12`.
- A2D2: 36 muestras (12 train/12 val/12 test) de un manifiesto de 3,000 registros (1,000 por split), todas 1920x1208. Mapa de 55 clases; cero píxeles de colores desconocidos. Píxeles mapeados a las siete clases objetivo: bicycle 122,674; car 2,196,767; lane marking 907,305; person 31,639; sidewalk 1,268,614; traffic sign 751,051; truck 1,188,485. Total 6,466,535 de 83,496,960 píxeles (7.74%); el resto se ignora porque corresponde a clases fuera de la ontología objetivo, no por colores corruptos. Se reconstruyeron 438 componentes (180 train/106 val/152 test) a partir de subclases/connected components; IDs canónicos observados 3,5,6,7. No son IDs nativos y puede haber fragmentación por oclusión.
- UrbanSyn: 36 muestras (12 por split) de manifiesto de 2,534 registros (1,000 train/751 val/783 test), resolución 2048x1024, revisión HF `8599498aceee9072f1e067a4a4efed7f20b11809`. En la muestra aparecen todos los IDs semánticos 0–19 y clases panoptic 0,11–18. Acuerdo medio semseg/panoptic en píxeles dinámicos: 0.99992872195 (99.9929%), mínimo 0.99769889894 y máximo 1.0; 35 muestras tuvieron píxeles dinámicos comparables y una muestra de test no tuvo objetos dinámicos. Se decodificaron 870 instancias y 870 registros bbox2D; conteos coinciden en las 36 muestras. El informe aún no asigna nombres a los IDs fuente, aunque la tabla de taxonomía oficial está documentada en `docs/ESTRATEGIA_MULTIDATASET.md`; armonizar ese campo del auditor queda como mejora documental. Licencia sigue `REVIEW_REQUIRED_CONFLICTING_DECLARATIONS`.
- CI del HEAD de la rama [44995841201](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995841201): **success** en commit `51a1782bc17a3e0e53e586cbe6f7a22dda3f8bf4`. Pasaron instalación de dependencias, compileall, validación de CLIs, **52 tests en 8.96 s** y validación de muestras semánticas BDD100K reales. Los runs [44995801141](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801141) y [44995805671](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995805671) quedaron cancelados por concurrencia y no son fallos de tests; el run posterior exitoso cubre el HEAD actual.
- HEAD verificado: `51a1782bc17a3e0e53e586cbe6f7a22dda3f8bf4`. PR #3 sigue **open, draft, merged=false**; no se fusionó.
- Conclusión: ya está completada la auditoría ampliada prevista de 72 muestras (36 A2D2 + 36 UrbanSyn), con consistencia interna positiva en las muestras analizadas. No es un censo de todas las anotaciones ni demuestra independencia temporal de UrbanSyn. SHIFT sigue sin ser evaluable hasta resolver sincronización RGB/semseg. La licencia UrbanSyn sigue pendiente. No se descargaron datasets completos ni se inició entrenamiento; `RUN_TRAINING=False`, sin checkpoints ni métricas de modelos.
- Próximos pasos: armonizar nombres de clases en el informe automático, resolver la licencia UrbanSyn y la sincronización SHIFT, y ejecutar smoke tests de loaders/targets de A2D2 y UrbanSyn con muestras reales de los manifiestos antes de habilitar entrenamiento.


### Siguiente fase: smoke tests de loaders reales y taxonomía UrbanSyn — 2026-11-22

- Se consultó este registro antes de intervenir y se verificó la PR #3 y el HEAD.
- Se añadió `scripts/smoke_test_real_manifest_loaders.py`: selecciona determinísticamente una muestra de cada split (train/val/test) en A2D2 y UrbanSyn, descarga temporalmente solo RGB/anotaciones necesarias, y ejecuta los cuatro loaders reales (`A2D2SemanticDataset`, `A2D2InstanceDataset`, `UrbanSynSemanticDataset`, `UrbanSynInstanceDataset`). Comprueba dimensiones/tensores, IDs, cajas XYXY, máscaras, labels y DataLoader/collate. Para UrbanSyn lee también bbox2D JSON. Las descargas permanecen en almacenamiento temporal del runner; solo se publica un informe agregado.
- Se añadió `.github/workflows/smoke-test-real-loaders.yml` con disparo manual y por cambios del propio smoke test. El primer run [44996790300](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996790300) falló antes de ejecutar los loaders: el trigger push no recibe `inputs.manifest_run_id` y la acción intentó descargar desde run-id NaN. Se corrigió el fallback al run de manifiestos `44992977292` en commit `3900fdb9248ebfdd202c1b790587847b5a38df62`.
- Nueva ejecución del smoke test [44996854672](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996854672): **in_progress** al actualizar el registro, en instalación de PyTorch CPU/dependencias; todavía no se han descargado manifiestos ni ejecutado los loaders. No declarar PASS hasta inspeccionar el artifact JSON.
- Se actualizó `scripts/audit_urban_annotations.py` para incluir explícitamente el mapa oficial trainId→nombre de UrbanSyn (0–19) en el informe. Commit `89178818549c898600be7ba0d9666712e626d0c0`. Auditoría de verificación [44996793135](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996793135) seguía **in_progress** en descarga/inspección remota al registrar; revisar su artifact para confirmar nombres.
- CI Python del commit de auditoría [44996794893](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996794893) estaba **in_progress**; una ejecución previa fue cancelada por concurrencia de pushes. Revisar una ejecución verde sobre HEAD final antes de habilitar entrenamiento.
- SHIFT sigue bloqueado para métricas: RGB y semseg decodifican 501 frames con igual tamaño, pero OpenCV reportó 10 FPS y 25 FPS. Esto no demuestra alineación temporal. Próximo análisis técnico será extraer timestamps PTS por frame de ambos MP4 y comparar duración/instantes; no asumir correspondencia por índice.
- UrbanSyn se mantiene bajo criterio conservador CC BY-NC-SA 4.0 por discrepancia con el metadata del mirror. El proyecto es académico/no comercial; mantener atribución y no redistribuir imágenes, máscaras ni derivados. No se ha obtenido aclaración escrita del proveedor, por lo que la discrepancia documental queda abierta.
- HEAD esperado después de registrar: commit nuevo de documentación. PR #3 continúa abierta/draft/no fusionada. `RUN_TRAINING=False`; no se inició entrenamiento ni se descargaron datasets completos.

#### Correcciones del smoke test y ejecución vigente — 2026-11-22

- El primer intento de loaders [44996854672](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996854672) ya descargó correctamente ambos artifacts de manifiestos. Falló al importar src; se corrigió añadiendo la raíz del repositorio a sys.path (commit 21fff53988d5e55ce60832bbd8d57c3aa0d94655). En ese run también se detectó que el input opcional image_size queda vacío en push; se corrigió el fallback a 512 (commit 6f6b2f0206a67248f7ba9655696fc9ddc96a182c).
- El segundo intento [44996927934](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996927934) llegó a ejecutar el loader de instancias A2D2 y detectó que el workflow no instalaba OpenCV (cv2), dependencia requerida por connected components. Se añadió opencv-python-headless al entorno en commit a34218498afafc82305b734a0175bdbf9cac67b9.
- Run [44996924880](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996924880) corresponde al commit anterior a los fallbacks y falló con --size ""; no es una prueba de los loaders.
- Nuevo run [44997010957](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997010957) del commit a34218498afafc82305b734a0175bdbf9cac67b9: in_progress en instalación de dependencias al último chequeo. Aún no hay resultado de loaders ni artifact.
- La auditoría con nombres oficiales UrbanSyn [44996793135](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996793135) continúa in_progress en el paso de descarga/inspección; aún no hay artifact final. No declarar el mapa aplicado al informe hasta inspeccionar ese artifact.
- CI del commit anterior [44996929342](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996929342) se canceló por pushes sucesivos. CI del HEAD a34218498afafc82305b734a0175bdbf9cac67b9 [44997017593](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997017593) está in_progress al cierre. Revisar ejecución final del HEAD.
- HEAD de rama verificado al iniciar este addendum: a34218498afafc82305b734a0175bdbf9cac67b9. PR #3 sigue abierta, draft y sin fusionar. RUN_TRAINING=False.

#### Resultado de smoke test con loaders reales — 2026-11-22

- Ejecución [44997010957](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997010957): **success**. Se descargaron los dos artifacts de manifiestos y se ejecutaron los cuatro loaders sobre una muestra real por split (3 A2D2 + 3 UrbanSyn). Artifact agregado [14744226123](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997010957/artifacts/14744226123), descargado e inspeccionado; ZIP 631 bytes, SHA-256 f452849025c556d1aacc660dee56c0c621eeab190159764dba933ed22cee9afe.
- A2D2: las tres imágenes se cargaron a tensores 3x512x512 y sus máscaras semánticas a 512x512. Las muestras train/val/test presentaron IDs canónicos esperados e ignore 255. El loader de instancias produjo 0, 5 y 2 instancias respectivamente. La muestra train no tiene subclases de participantes, por lo que target vacío (0 cajas, máscaras 0x512x512) se acepta correctamente; val/test generaron cajas y máscaras consistentes. Esto confirma que el loader soporta targets vacíos, pero también muestra por qué la cobertura por split debe medirse antes de entrenar instancias.
- UrbanSyn: los tres splits produjeron tensores semánticos 512x512 y targets de instancias con 10/22/14 objetos. Conteos de bbox2D JSON: 10/22/14 respectivamente; coinciden exactamente con las instancias decodificadas. Shapes de cajas y máscaras coherentes (N x 4 y N x 512 x 512); etiquetas canónicas válidas.
- Conclusión acotada: **PASS estructural de los cuatro loaders con muestras reales de manifiesto** y de DataLoader/collate; no es evaluación de calidad de etiquetas ni suficiente para aprobar distribución/cobertura global de clases. Para A2D2 instance training se debe filtrar o ponderar frames sin participantes y estudiar desequilibrio de clases.
- Correcciones del workflow documentadas arriba: sys.path, fallback de tamaño 512 y dependencia OpenCV. Los intentos anteriores fallidos fueron problemas del propio workflow, no de los datos.
- CI del HEAD documental todavía en ejecución [44997090889](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997090889); revisar antes de cerrar esta fase. Auditoría con nombres de clase UrbanSyn [44996793135](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996793135) también seguía in_progress en la última consulta.

### Cierre de verificaciones adicionales — 2026-11-22

- La auditoría de nombres oficiales UrbanSyn [44996793135](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996793135) terminó success. Artifact [14743879270](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44996793135/artifacts/14743879270), descargado e inspeccionado: 12 muestras por split (36 UrbanSyn), el JSON incluye los 20 nombres de clase verificados (road, sidewalk, building, wall, fence, pole, traffic light, traffic sign, vegetation, terrain, sky, person, rider, car, truck, bus, train, motorcycle, bicycle, unlabeled). El acuerdo semseg/panoptic sigue en 0.99992872195.
- Smoke test real de los cuatro loaders [44997010957](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997010957) success; artifact [14744226123](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997010957/artifacts/14744226123) inspeccionado. Resultado: A2D2 0/5/2 instancias en train/val/test; UrbanSyn 10/22/14 instancias y exactamente 10/22/14 cajas bbox2D. Todos los tensores semantic 512x512 y targets de instancia tienen shapes coherentes. La muestra A2D2 train sin participantes produce correctamente target vacío; no equivale a fallo del loader, pero alerta de cobertura desigual.
- SHIFT: se añadió análisis ffprobe de PTS reales. El artifact de diagnóstico [14744456783](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997244326/artifacts/14744456783) mostró 501 PTS en ambos videos, pero RGB dura 50.1 s a 10 fps y semseg 20.04 s a 25 fps; primer PTS 0 en ambos y último PTS 50.0 vs 20.0. La diferencia absoluta por índice de frame tiene mediana 15 s, p95 28.5 s y máximo 30 s. Solo 20 s de timeline se superponen (40% del RGB); 201 frames RGB del solapamiento tienen vecino semseg cercano (p95 0.02 s). Por tanto no hay alineación temporal demostrada para el video completo. Puede investigarse un subconjunto de 20 s, pero requiere comprobar visualmente los pares; SHIFT permanece excluido de métricas.
- Se corrigió el criterio del comparador PTS para exigir cobertura temporal de al menos 95% de ambos streams, no solo del stream más corto. Código commit 3e0d62734fc2dab4f160d55e0bb1a148903366dd. Run actualizado [44997339932](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997339932) está in_progress en la inspección; confirmar el artifact final.
- CI Python del HEAD 3e0d62734fc2dab4f160d55e0bb1a148903366dd [44997339867](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997339867) está in_progress. Los runs previos se cancelaron por pushes sucesivos; no declarar suite verde para el HEAD hasta que termine.
- HEAD al actualizar este apartado: 3e0d62734fc2dab4f160d55e0bb1a148903366dd. PR #3 abierta, draft y sin fusionar. RUN_TRAINING=False. No datasets completos descargados, no entrenamiento, checkpoints ni métricas de modelos.
- Bloqueos restantes: discrepancia licencia UrbanSyn sin aclaración escrita del proveedor; A2D2 necesita medir cobertura de instancias por split/clase a escala del manifiesto; SHIFT requiere inspección visual de los pares dentro del solapamiento o queda descartado. Próximo paso tras CI: ampliar smoke de A2D2 a más muestras deterministas (para cuantificar frames vacíos/clases) y revisar correspondencia temporal visual SHIFT; después decidir si SHIFT se descarta.

#### Resultado final de sincronización SHIFT y CI de código — 2026-11-22

- La ejecución actualizada de SHIFT [44997339932](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997339932) terminó success. Artifact [14744556799](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997339932/artifacts/14744556799), descargado e inspeccionado. Confirma 501 frames en ambos archivos, RGB 50.1 s/10 fps y semseg 20.04 s/25 fps; solapamiento solo 20 s, equivalente al 40% del RGB y 100% de semseg. Desfase PTS por índice: mediana 15 s, p95 28.5 s, máximo 30 s. Estado definitivo: NOT_TEMPORALLY_ALIGNED_BY_PTS. SHIFT queda excluido del benchmark completo; no se debe corregir FPS a mano ni emparejar por índice. Podría estudiarse solo la ventana común de 20 s con verificación visual frame-a-frame, pero no es requisito para continuar con A2D2/UrbanSyn.
- CI Python del commit de código 3e0d62734fc2dab4f160d55e0bb1a148903366dd terminó success en run [44997343731](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997343731). El HEAD actual avanzó después solo por documentación; CI para HEAD documental c0375a9c98bb435a3d53a9e21f29327846352526 [44997468590](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997468590) estaba in_progress y [44997464409](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44997464409) pendiente al cierre. Reconfirmar el run final sobre HEAD documental.
- La PR #3 sigue abierta, draft, merged=false. No se fusionó ni se habilitó entrenamiento.

#### Cobertura de instancias A2D2 en la auditoría ampliada

- Se reanalizó el artifact de 36 muestras A2D2 (12 por split) [14742929447](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44995801143/artifacts/14742929447). Componentes por split: train 180, val 106, test 152. Frames sin componentes: train 0/12, val 1/12, test 0/12. Componentes por etiqueta canónica: train car 11/truck 9/bicycle 2/person 1; val car 10/truck 10; test car 11/bicycle 5/person 5/truck 3.
- Esta muestra determinista indica cobertura de participantes en los tres splits, pero no demuestra cobertura suficiente de clases raras: no se observaron bus/motorcycle/rider y persona/bicicleta tienen menos componentes. Los conteos son componentes reconstruidos desde subclases y no instancias nativas. Se requiere ponderación/estratificación por clase o ampliar muestra antes de entrenar Mask R-CNN con A2D2.- El smoke test independiente de una muestra por split seleccionó un frame train sin participantes (target vacío) aunque el muestreo de 12 frames del audit train no tuvo frames vacíos; esto confirma variación entre muestras, no contradicción del loader.


#### Ampliación de auditoría de cobertura A2D2 — 2026-11-22

- Se amplió `scripts/audit_urban_annotations.py`: el tamaño de muestra por defecto pasó a 50 por split (train/val/test), límite ya admitido por el CLI; la selección sigue siendo determinista y se realiza dentro de cada manifiesto existente. Total previsto: 150 pares RGB/máscara A2D2 y 150 muestras UrbanSyn en el mismo informe.
- El informe ahora añade `per_split_instance_coverage` para A2D2: número de frames muestreados, frames con/sin instancias reconstruidas, porcentaje con instancias, número de frames donde aparece cada clase y componentes por clase. Se mantienen conteos de píxeles y controles de dimensiones/decodificación.
- Workflow `.github/workflows/audit-urban-annotations.yml`: valor predeterminado de `samples_per_split` actualizado de 12 a 50. Los dos cambios se guardaron en commits `b19123a0a84c228632e02f32a56ffe9f3b450467` (script) y `7ae8b44d7fbb68d20ecd993467ec3f1ca936d13a` (workflow). El push de estos archivos activa automáticamente la auditoría; aún no se declara resultado hasta que finalice y se inspeccione el artifact.
- CI de Python del HEAD anterior `1c49b56a5d58d1d419ca864b9db1bed4f91562d2`: runs push `44997639027` y PR `44997642985` terminaron `success`; el probe BDD100K `44997639029` también terminó `success`. HEAD sigue avanzando con la ampliación de auditoría.
- PR #3 permanece abierta, draft y sin fusionar. No se inició entrenamiento ni se habilitó `RUN_TRAINING`.
- Próximo paso: inspeccionar CI y la nueva auditoría de 50 muestras por split; revisar el artifact JSON y determinar si la cobertura de bus, motocicleta, ciclista y peatón es suficiente o si conviene filtrar/ponderar A2D2.


#### Resultados de auditoría ampliada — 150 muestras por dataset — 2026-11-22

- Auditoría completa [44998059307](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44998059307), **success**, sobre commit `7ae8b44d7fbb68d20ecd993467ec3f1ca936d13a`. Artifact [14745482226](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44998059307/artifacts/14745482226), descargado e inspeccionado (JSON 181,886 bytes; SHA-256 del artifact declarado por GitHub: `505a4f7494d8784a76f28bbd4dc256d2b19c8e024b88e117817d1f846c5d6ffc`). Se inspeccionaron 50 muestras por split y dataset: A2D2 150/150 y UrbanSyn 150/150.
- A2D2: manifiestos de 1,000 filas por split. En la muestra, train 50/50 frames con componentes (100%); val 44/50 (88%, seis vacíos); test 50/50 (100%). Total 144/150 (96%) con alguna instancia reconstruida. Componentes por clase: train car 569, truck 111, bicycle 55, person 49; val car 337, truck 225, sin bicycle/person; test car 476, truck 63, bicycle 42, person 46. Totales 1,382 car, 399 truck, 97 bicycle y 95 person. Frecuencia de aparición por frames: car 137/150, truck 93/150, bicycle 28/150, person 25/150. No se observaron bus, motorcycle ni rider en estas 150 muestras.
- A2D2 no tuvo colores desconocidos. La cobertura de píxeles semánticos canónicos fue: car 9,734,113; truck 3,207,728; lane marking 4,163,747; sidewalk 3,581,788; traffic sign 2,144,756; bicycle 195,694; person 95,013. El resto de píxeles de clases fuente no mapeadas a la ontología canónica se conserva como ignore; no es corrupción de máscara. La muestra confirma que A2D2 tiene participantes, pero el subconjunto reconstruido está muy sesgado hacia car/truck y no cubre las clases requeridas bus/motorcycle/rider en la muestra.
- UrbanSyn: 150 muestras, 50 por split. Acuerdo medio entre clase semseg y canal de clase panoptic en píxeles dinámicos: `0.9999771023` (~99.9977%). Los 150 JSON bbox se pudieron interpretar; los conteos de bbox coinciden exactamente con instancias panoptic decodificadas en las 150 muestras. Distribución semseg observada incluye clases estáticas y dinámicas; el panoptic muestreado contiene clases dinámicas 11–18. Esto es una validación de consistencia de anotaciones, no evaluación del modelo.
- Interpretación: A2D2 puede servir para semántica (incluidas marcas viales) y para experimento limitado de instancias de car/truck/person/bicycle, pero no debe presentarse como cobertura equilibrada de todos los objetos urbanos. Para el benchmark multiclase de instancias, UrbanSyn aporta mejor cobertura nominal de clases dinámicas; su licencia sigue bajo revisión conservadora CC BY-NC-SA 4.0 por discrepancia documental.
- Decisión: no entrenar aún un único detector multiclase usando A2D2 como fuente suficiente. Mantener A2D2 para semántica y como complemento/ablation de instancias; usar UrbanSyn como fuente principal para instancias, sujeto a las restricciones de licencia. Si se necesita cubrir clases raras con datos reales, evaluar un dataset adicional compatible y accesible o declarar explícitamente que A2D2 no cubre esas clases en la muestra. La auditoría es aleatoria determinista por hash, no estratificada; 150 muestras no demuestran ausencia global de clases raras.
- CI del HEAD documental `9c875184e7ab023523b569bef9845645055d309d`: Python tests push [44998091612](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44998091612) y PR [44998087534](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44998087534) **success**; probe BDD100K [44998087513](https://github.com/Leohf04/Procesamiento-de-Im-genes-/actions/runs/44998087513) **success**. Las ejecuciones intermedias canceladas pertenecen a commits supersedidos.
- HEAD al cierre de esta revisión: `9c875184e7ab023523b569bef9845645055d309d`. PR #3 sigue abierta, draft, no fusionada. `RUN_TRAINING=False`; no se ha entrenado ni descargado ningún dataset completo.


#### Ontología versionada y preparación del plan balanceado — 2026-11-22

- Se consultó este registro al inicio. HEAD previo 73084d90e3fd6b556fbd4e9f6a16c76dad0139b7; PR #3 estaba abierta, draft y sin fusionar; CI de Python en ese HEAD estaba verde (push 45000605679, PR 45000608902).
- Se confirmó que ya existía scripts/prepare_reproducible_subsets.py, que produce manifiestos experimentales remotos con split determinista por grupo (A2D2 por secuencia; UrbanSyn por ID de muestra), pero no balanceaba clases.
- Se añadió configs/urban_ontology_v1.json y src/urban_ontology.py. Ontología urban-v1: semántica UrbanSyn 0–18 preservada, unlabeled 19 → ignore 255, lane marking semantic ID 19; instancias 1–8 = person/rider/car/truck/bus/train/motorcycle/bicycle, background 0. rider y bicycle quedan separados; lane marking no es instancia. A2D2 se mapea por nombre normalizado y clases no incluidas quedan en ignore. Se rechazan fuentes de dataset desconocidas.
- Se añadió scripts/build_balanced_training_plan.py. Consume manifiestos y archivos de índice per-image ({dataset}_{split}.annotations.jsonl) con semantic_pixels e instance_counts; falla si faltan filas, hay duplicados, estado no válido o conteos negativos. Selecciona train con un algoritmo greedy multilabel determinista; mantiene validation/test completos, sin downsampling ni reordenamiento. Emite manifiestos separados por dataset/tarea y un informe de cobertura. UrbanSyn se marca como fuente primaria de instancias y A2D2 como complemento/ablation; no se concatenan dominios.
- Se añadieron pruebas tests/test_urban_ontology_and_balance.py para IDs/mapeos, ignore/unlabeled, distinción rider/bicycle, determinismo, selección de clases raras, fallos de índices incompletos y preservación de validation/test completos.
- Se añadió docs/PLAN_BALANCEO_Y_ONTOLOGIA.md y una actualización en docs/ESTRATEGIA_MULTIDATASET.md.
- Límite importante: el artifact de auditoría 150+150 contiene estadísticas agregadas por split, no estadísticas por imagen. Por tanto, el código del planificador y la ontología están implementados, pero todavía no se ha generado el índice per-image ni un plan balanceado real. No afirmar que el balanceo sobre datasets reales está terminado. Próximo paso: construir un indexador remoto que decodifique las anotaciones y emita esos seis índices (A2D2/UrbanSyn × train/val/test), ejecutar el planificador y auditar la cobertura resultante.
- La ontología nueva no cambia retroactivamente los IDs legacy por defecto de src/data_adapters.py; los nuevos experimentos deben pasar explícitamente los mapas versionados y probarlos antes de entrenar.
- RUN_TRAINING=False; no se descargaron datasets completos, no se entrenó y no se generaron checkpoints ni métricas de modelos. Se mantiene la licencia conservadora UrbanSyn CC BY-NC-SA 4.0, atribución y no redistribución.
- Commits de implementación: 5001f421 (config), 87f20fae (loader), 80f1907e (planner), 0a05f901 (tests), 579aa308 (doc); correcciones posteriores 9d823957, aabf0e7f, 8827e768, b1b14ef y 6184489d.
- HEAD antes de esta actualización del registro: 6184489dd3a796eee71748a1e6d669b0bf2689fd. PR #3 verificada abierta, draft, merged=false y apuntando al HEAD. CI de Python push/PR para ese SHA estaba pendiente/queued (45001424794, 45001429018); los runs intermedios cancelados pertenecen a commits supersedidos. Confirmar el resultado final después del commit de este registro.


#### Correcciones de CI y validación final de ontología/planificador — 2026-11-22

- La primera suite de CI para el código nuevo (`45001494752`, SHA `a3677be7`) detectó dos fallos en pruebas nuevas: los IDs fuente UrbanSyn llegaban como strings y una fixture JSONL escribía el literal \\n. Se corrigió `src/urban_ontology.py` para exponer claves UrbanSyn como enteros y se corrigió la escritura de fixtures.
- CI final de código en SHA `c5a8fd8773183bd98499422ad7cb2526e30c41ae`: Python tests push `45001691687` **success** y PR `45001696004` **success**. Se verificaron pasos: instalación de dependencias, compileall, CLIs, `pytest -q` y validación real de muestras semánticas BDD100K; todos terminaron success.
- La suite incluye ahora las pruebas nuevas de ontología, planificador, integridad del índice y preservación de validation/test completos. Los runs fallidos anteriores corresponden a la primera versión y quedaron corregidos en el SHA posterior.
- Estado del código: ontología y planificador listos a nivel de implementación y tests sintéticos; el plan balanceado real sigue bloqueado por falta de índices de anotaciones per-image para ambos datasets. La auditoría 150+150 no contiene esos datos individuales.
- HEAD antes de este addendum: `c5a8fd8773183bd98499422ad7cb2526e30c41ae`. PR #3 abierta, draft, merged=false. `RUN_TRAINING=False`; sin datasets completos descargados ni entrenamiento.


#### Indexador remoto per-image y ejecución de prueba — 2026-11-22

- Se implementó `scripts/index_remote_annotations.py`. Lee únicamente las anotaciones (sin fotografías RGB): A2D2 semantic RGB masks desde S3 anónimo y UrbanSyn semseg+panoptic desde la revisión exacta del manifiesto. Aplica `urban-v1` y genera una fila JSONL por sample_id con `semantic_pixels` e `instance_counts`; cualquier error de descarga/decodificación/forma hace fallar el job, no se convierte en muestra vacía.
- Se añadieron `tests/test_remote_annotation_index.py`, `.github/workflows/index-remote-annotations.yml` y `docs/INDEXACION_REMOTA_ANOTACIONES.md`. El workflow tiene `workflow_dispatch` y smoke automático al cambiar los scripts relacionados; límite por defecto 100 muestras por split/dataset para la prueba inicial. Construye manifiestos y, si el indexado termina, invoca `build_balanced_training_plan.py` y sube artifacts sin datos de imagen/máscara.
- Se amplió `normalize_class_name` para clases estáticas A2D2 (building, wall, fence, pole, vegetation, terrain, sky) y el patrón de instancias A2D2 para reconocer bus/person/rider. Esto corrige clases que se perderían en el conteo per-image.
- Primera ejecución automática `45002523488` falló al pasar inputs: el workflow contenía barras invertidas literales antes de las expresiones `${{ inputs.* }}`. Se corrigieron las expresiones; no se generó artifact en ese intento.
- Segunda ejecución `45002573760` generó correctamente manifiestos de 100 por split (A2D2 300 y UrbanSyn 300, UrbanSyn revision `8599498aceee9072f1e067a4a4efed7f20b11809`) pero falló al importar `src` desde el script. Se corrigió añadiendo la raíz del repo a `sys.path`.
- Tercera ejecución del indexador `45002662737` sobre commit `a724ecaa5ff422ad331e9f4b58b01f28f2dd7e82`: generación de manifiestos **success**; indexación per-image en curso al actualizar este registro. No declarar aún índices ni balanceo real completados; revisar el job/artifact cuando finalice.
- CI Python de ese SHA detectó una expectativa errónea en una prueba sintética: las regiones person/bicycle eran de 4 px, inferiores al umbral intencional de 8 px de componentes A2D2. Se amplió la fixture a 9 px y se corrigieron los conteos esperados en commit `700454d6d17cab49b6c634d43743da2d2eb94343`. CI push `45002804361` y PR `45002798404` quedaron en curso/pendientes al cierre; verificar resultados sobre el HEAD final.
- CI anterior PR `45002668197` terminó failure únicamente por esa expectativa de área mínima: 64 passed, 1 failed. Compileall y CLIs pasaron. No hay evidencia de entrenamiento ni de descarga de imágenes RGB.
- HEAD al redactar este addendum: `700454d6d17cab49b6c634d43743da2d2eb94343`. PR #3 permanece abierta, draft y sin fusionar. `RUN_TRAINING=False`.


#### Estado al cierre de la intervención — 2026-11-22

- Se corrigió la fixture A2D2 para respetar el umbral real de 8 px de componentes; el commit de prueba es `700454d6`. El run PR anterior `45002668197` falló solo en esa expectativa (64 passed, 1 failed), no en compileall ni CLIs.
- La actualización de este registro y de `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md` generó HEAD `8ef74fabe3859eb798ec9bb9d60cb05a02277f2d`; PR #3 continúa abierta, draft, merged=false y apunta al HEAD.
- CI de Python para el SHA actual push `45002871645` está en curso; la ejecución PR del SHA intermedio se canceló por el push documental siguiente. Verificar el run del HEAD después de esta actualización.
- Workflow de indexación remoto `45002662737` sigue en curso sobre SHA `a724ecaa5ff422ad331e9f4b58b01f28f2dd7e82`: manifiestos de 100 muestras por split/dataset generados correctamente; el paso de indexación per-image está en curso. Aún no hay artifact final ni balanceo real validado. El run anterior `45002573760` falló por import path; esa corrección ya está en el SHA del run actual.
- No entrenamiento, no checkpoint ni descarga de fotografías RGB. El indexador descarga solo máscaras/anotaciones en el runner temporal. `RUN_TRAINING=False`.

#### Inspección del primer artifact per-image y ampliación a 1.000 muestras — 2026-11-22

- Se consultó este registro y se verificaron HEAD, PR #3 y Actions antes de continuar. HEAD inicial de esta intervención: `150ba7f8d0c6e8ac2ed001a22c4e5f1cbcbe02fd`; PR #3 abierta, draft, merged=false.
- El workflow `45002662737` terminó **success** (job `index-and-plan`, todos los pasos success). Artifact `14747027823`, ZIP de 163.067 bytes, SHA-256 `3d1e6342b4ecf20426b6125c0439f894fa5089db3203751a560c8c74d5e08240`; descargado e inspeccionado. Contiene 23 archivos: seis índices JSONL, seis manifiestos de tarea/dataset/split, plan JSON y resúmenes.
- Integridad del artifact: 100 filas por split para cada dataset (600 filas de índice en total), 100 IDs únicos por archivo, cero IDs nulos o duplicados. Conteos JSONL y resúmenes coinciden.
- UrbanSyn semántica: 19/19 clases semánticas observadas en cada split de 100. Instancias: las ocho clases observadas en train/val/test. Conteos de objetos por clase train: bicycle 86, bus 21, car 599, motorcycle 64, person 1.231, rider 142, train 6, truck 41; val: 119/31/568/73/1.330/141/8/31; test: 89/37/513/52/1.314/127/7/37, respectivamente.
- A2D2 semántica: ocho clases observadas en train y test (car, truck, bicycle, person, sidewalk, sky, traffic sign, lane marking); seis en val (car, truck, sidewalk, sky, traffic sign, lane marking). Instancias: train car 1.133, truck 194, bicycle 98, person 109; val car 686 y truck 486; test car 968, truck 130, bicycle 90, person 68. No aparecen bus, train, motorcycle ni rider en las muestras de instancias A2D2. Val tampoco presenta bicycle/person en las 100 muestras indexadas. Esto refuerza el uso de A2D2 como fuente semántica y ablation complementaria limitada para instancias, no como detector multiclase equilibrado.
- Observación importante del plan piloto: al indexar solo 100 filas y permitir hasta 100 muestras, el planificador conserva las 100 de cada split; en train solo reordena con prioridad multilabel, no realiza downsampling ni balancea por sí solo las frecuencias. No interpretar el nombre balanced como distribución equilibrada. Debe considerarse sampler/pesos de clase en el pipeline de entrenamiento.
- Se detectó que `uncovered_classes` solo comparaba clases presentes en el índice y no reportaba clases esperadas por la ontología que estaban ausentes. Se corrigió `scripts/build_balanced_training_plan.py` para reportar `unavailable_classes` y `uncovered_classes` contra el conjunto esperado por dataset/tarea; se añadió prueba para clases esperadas ausentes.
- Se elevó el límite predeterminado del workflow de indexación de 100 a 1.000 muestras por split/dataset, y se actualizó `docs/INDEXACION_REMOTA_ANOTACIONES.md`. Los cambios quedaron en commits sucesivos; HEAD documental actual: `7b369c0b3be27aebd30c689443b4127c3558e747`.
- Ejecuciones disparadas por los cambios: smoke de 100 filas `45005695816` (SHA `8aea5a0e`) y flujo ampliado de 1.000 filas `45005700564` (SHA `c08ea9a3`); ambos habían completado manifiestos y estaban indexando anotaciones al cierre. CI Python del HEAD `7b369c0b`, run `45005705417`, estaba en curso. Consultar resultados y artifact antes de declarar cobertura ampliada.
- La suite de CI del HEAD anterior `150ba7f8` y el probe BDD100K terminaron success (`45002932881`, `45002927531`). Los runs cancelados pertenecen a SHAs intermedios supersedidos.
- No se inició entrenamiento, no hay checkpoints ni métricas de modelo. `RUN_TRAINING=False`. La indexación descarga anotaciones/máscaras al runner temporal, no fotografías RGB completas. Licencia UrbanSyn sigue bajo criterio conservador CC BY-NC-SA 4.0.
- Próximo paso: inspeccionar el artifact del run 1.000 y comprobar la cobertura por clase y split con los nuevos campos; revisar CI del HEAD. Después, definir pesos/sampler de entrenamiento y validar loaders con los manifiestos completos antes de habilitar cualquier entrenamiento.

- **Cierre de esta actualización del registro:** el addendum anterior quedó guardado en commit `590d7bc096c99fbfb4a7032929ebcf1df80761ab`. En la consulta posterior, el workflow ampliado de 1.000 muestras `45005700564` seguía indexando y el smoke de 100 muestras `45005695816` también seguía activo; no se encontró aún artifact nuevo. CI del HEAD del registro estaba pendiente en runs `45005835685` (push) y `45005831167` (PR). El probe BDD100K del HEAD `590d7bc0` terminó success (`45005831271`). La PR #3 continúa abierta, draft y sin fusionar. No habilitar entrenamiento hasta inspeccionar el artifact de 1.000 muestras y resolver la estrategia de muestreo/pesos.

#### Siguiente objetivo: estrategia de pesos y muestreo consciente de clases — 2026-11-22

- Se volvió a consultar el registro y auditar HEAD/PR/Actions antes de trabajar. HEAD de partida `529222b544c09a4ade9336aa2e5557ec87b104fe`; PR #3 abierta, draft, merged=false. CI Python push y PR de ese HEAD: success (`45005890158`, `45005885890`); probe BDD100K success (`45005885769`).
- El workflow ampliado `45005700564` (SHA `c08ea9a3`) aún no había publicado artifact: job `index-and-plan` seguía en el paso `Index per-image annotations`; el run de 100 muestras `45005695816` también seguía activo. No existe todavía un artifact de 1.000 muestras que pueda auditarse. Se mantiene pendiente de finalización remota.
- Se implementó `src/class_balancing.py`:
  - `semantic_class_weights`: pesos de CrossEntropyLoss calculados desde píxeles de train con frecuencia inversa de raíz cuadrada, normalización media uno, cero para clases ausentes y validación de conteos.
  - `instance_sample_weights`: peso por imagen como promedio de rareza de las clases de instancia presentes, evitando ponderar solo por número de objetos.
  - `make_instance_sampler`: WeightedRandomSampler reproducible con semilla y replacement.
- Se añadieron pruebas para normalización/ausencia de clases, preferencia por clase rara y reproducibilidad del sampler; se documentó que los pesos se calculan solo con train y que A2D2/UrbanSyn permanecen separados.
- Los helpers aún no están conectados a los trainers antiguos (Cityscapes/BDD100K); falta validar el artifact ampliado y rutas locales para integrar los loaders UrbanSyn/A2D2 sin alterar el flujo legacy. No se deben calcular pesos usando validation/test ni afirmar que el balanceo de datos reales está finalizado.
- Commits de esta tarea: `4398bb64` (helper), `beba56bd` (tests), `76d4cf9a` (documentación). HEAD al cierre de estos cambios: `76d4cf9aeb4c5274933e137b258a8826aebe0b71`.
- Próximo paso: comprobar CI del nuevo HEAD; volver a consultar run `45005700564` y artifact; si la indexación termina, auditar 1.000 muestras por split, clases ausentes y manifiestos. Después conectar sampler/pesos al loader multidataset, con prueba de integración sintética. `RUN_TRAINING=False`.


#### Comprobaciones de continuidad — 2026-11-22

- Se volvió a leer este registro antes de consultar el estado remoto.
- HEAD confirmado en `urban-models-and-benchmark`: `c8ea2a7cc6acb7fa39c0e645609c392fd90998c8`.
- PR #3: `open`, `draft=true`, `merged=false`; su head SHA coincide exactamente con el HEAD de la rama. Se mantiene sin fusionar.
- CI Python sobre el HEAD actual terminó correctamente en ambos eventos: push `45006574610` y pull_request `45006579199`. En ambos jobs finalizaron success instalación CPU PyTorch/dependencias, compileall, validación de CLIs, `pytest -q` y validación de muestras semánticas BDD100K. El probe BDD100K del mismo SHA `45006574562` también terminó success.
- Los runs de CI cancelados corresponden a commits intermedios supersedidos; no representan fallos del HEAD actual.
- Revisión del indexador ampliado: run `45005700564`, SHA `c08ea9a363098880e577f9104cc4fd3f32c72efa`, sigue `in_progress`. El job `index-and-plan` completó setup, checkout, Python, dependencias y manifiestos reproducibles; el paso `Index per-image annotations` continúa en curso. Los pasos de construcción del plan y publicación del artifact siguen pendientes. La consulta de artifacts devolvió una lista vacía; por tanto, no hay artifact de 1.000 filas disponible para inspección.
- El smoke de 100 filas `45005695816` también continúa `in_progress`, en el mismo paso de indexación; todavía sin artifact.
- No se declara terminada la indexación per-image ampliada, ni el plan balanceado real, ni la integración de sampler/pesos en loaders. La validación de código/CI está verde, pero no sustituye esas comprobaciones de datos.
- No se inició entrenamiento; `RUN_TRAINING=False` se mantiene. No hay checkpoints ni métricas experimentales nuevas.
- Próximo paso: volver a consultar ambos workflows; al finalizar el run 1.000, descargar y auditar el artifact (integridad de filas/IDs, manifiestos, clases presentes/ausentes y cobertura por split). Después integrar sampler/pesos a los loaders multidataset con prueba sintética y smoke sin entrenamiento.


#### Nueva comprobación de indexación remota — 2026-11-22

- Se consultó primero el registro de continuidad y después se auditaron rama, PR #3 y GitHub Actions.
- HEAD al iniciar esta comprobación: `7c43d142d85bf7338c1f3ce9ebce7782a94a15ad`; PR #3 `open`, `draft=true`, `merged=false`, head SHA coincidente.
- CI Python del HEAD actual: push `45007088775` y pull_request `45007082842` terminaron `success`; probe BDD100K `45007082868` también `success`.
- El workflow ampliado `45005700564` sigue `in_progress`; job `index-and-plan`. Setup, checkout, Python, dependencias y preparación de manifiestos completados; `Index per-image annotations` sigue `in_progress`; build de planes y upload pendientes. Artifacts: lista vacía.
- El smoke `45005695816` de 100 muestras también sigue `in_progress` en `Index per-image annotations`, sin artifacts.
- Conclusión: indexación no terminada; no es posible auditar la salida de 1.000 muestras, clases ausentes/cobertura ni plan real. No se han inferido resultados a partir de manifiestos solamente.
- No se modificó código ni se inició entrenamiento. `RUN_TRAINING=False` se mantiene.
- Próximo paso: reconsultar estos dos workflows; cuando finalice el de 1.000 muestras, descargar y auditar el artifact antes de integrar sampler/pesos.


#### Revisión posterior de indexación — 2026-11-22

- Se volvió a consultar el registro antes de auditar HEAD, PR #3 y Actions.
- HEAD actual al iniciar: `852ac3d11f4fe57345d78cb5c44ae9fe8bc93006`; PR #3 continúa `open`, `draft=true`, `merged=false`, y su head SHA coincide con la rama.
- CI Python del HEAD actual: push `45007764725` y pull_request `45007768141` terminaron `success`; probe BDD100K `45007764701` terminó `success`.
- Indexación ampliada `45005700564` (SHA `c08ea9a363098880e577f9104cc4fd3f32c72efa`) sigue `in_progress`: manifiestos generados; paso `Index per-image annotations` aún en curso; plan y upload pendientes; sin artifacts. No hay base para auditar las 1.000 muestras todavía.
- Smoke de 100 muestras `45005695816` terminó `failure`. Su indexación per-image sí completó las 600 filas (100 por split × A2D2/UrbanSyn) y generó estadísticas de cobertura en el log, pero el paso `Build class-aware training manifests` falló con `ModuleNotFoundError: No module named 'src'` al importar `src.urban_ontology` desde `scripts/build_balanced_training_plan.py`. El upload quedó skipped, por lo que no existe artifact inspeccionable. Las estadísticas del log son diagnósticas y no constituyen un plan balanceado publicado.
- El run de 100 filas es un SHA previo y no demuestra que el error persista en el run de 1.000 filas; comprobar el resultado de este último. No modificar el código a partir de una suposición antes de revisar el SHA y logs del run actual.
- No se inició entrenamiento; `RUN_TRAINING=False`. No se generaron checkpoints ni métricas de modelos.
- Próximo paso: reconsultar run `45005700564`; si termina, descargar artifact y auditar integridad/cobertura/clases ausentes/plan. Si falla en el mismo import, corregir path de import en el planificador y repetir la indexación.


#### Comprobación posterior de indexación ampliada — 2026-11-22

- Se leyó el registro y se volvió a auditar la rama, PR #3 y Actions.
- HEAD actual al inicio: `416eee08bae9edfebcfffc4fad34caacd455a22d`. PR #3 continúa abierta, draft, sin fusionar y con head SHA coincidente. Los CI Python push/PR sobre este HEAD terminaron success (`45014065989`, `45014069463`); probe BDD100K `45014065984` también success.
- El workflow de indexación ampliada `45005700564`, ejecutado sobre el SHA antiguo `c08ea9a363098880e577f9104cc4fd3f32c72efa`, continúa `in_progress` en la consulta. Job `index-and-plan`: setup, checkout, Python, dependencias y manifiestos completados; `Index per-image annotations` sigue activo; build plan y upload pendientes. No tiene artifacts. No se puede auditar el resultado de 1.000 muestras.
- El smoke `45005695816` terminó failure. Sus pasos de indexación per-image completaron correctamente, pero el planificador falló al importar `src.urban_ontology` desde `scripts/build_balanced_training_plan.py`: `ModuleNotFoundError: No module named 'src'`. El upload se omitió y no existe artifact. Esto confirma el fallo de integración en el SHA de ese run; no se presupone que el run de 1.000 tenga el mismo resultado, porque corre sobre otro SHA anterior y aún sigue indexando.
- El log del smoke contiene estadísticas diagnósticas de 100 muestras por split, pero no se considera una auditoría publicable ni un plan final debido al fallo y ausencia de artifact.
- No se modificó código en esta intervención. No se inició entrenamiento; `RUN_TRAINING=False`; no hay checkpoints ni métricas de modelo.
- Próximo paso: revisar de nuevo el run de 1.000. Si finaliza, descargar artifact y auditarlo; si falla al construir el plan, corregir el import path en el SHA vigente y relanzar el workflow. La corrección debe probarse antes de aceptar la indexación ampliada.


#### Comprobación de indexación solicitada — 2026-11-22

- Se leyó el registro de continuidad y se verificó la rama, PR #3 y Actions.
- HEAD observado: `85ec33db4788fa86c0f366d88109552ad268b989`. PR #3 permanece abierta, draft y sin fusionar; su head SHA coincide con la rama.
- El workflow ampliado `45005700564` (SHA de ejecución `c08ea9a363098880e577f9104cc4fd3f32c72efa`) **no ha terminado**: estado `in_progress`. Job `index-and-plan`; pasos de setup, checkout, Python, dependencias y manifiestos completados; `Index per-image annotations` continúa en curso; construcción del plan y publicación de artifact siguen pendientes.
- Consulta de artifacts del run 1.000: lista vacía. No se puede auditar todavía la integridad de las 1.000 filas, la cobertura/clases ausentes ni los manifiestos finales.
- El workflow piloto de 100 filas `45005695816` terminó `failure`; no es sustituto del run ampliado ni proporciona artifact final.
- No se ha iniciado entrenamiento; `RUN_TRAINING=False`.
- Próximo paso: reconsultar el run `45005700564` cuando el usuario vuelva. Solo si termina y publica artifact, descargarlo y auditar filas, IDs, manifiestos, cobertura por clase/split y campos `unavailable_classes`/`uncovered_classes`.


#### Resultado definitivo de la indexación ampliada — 2026-11-22

- Se volvió a consultar este registro antes de verificar rama, PR y Actions.
- HEAD de la rama al iniciar: `eff585ef5023ee66f16845aeb0a8e7b0f70e4ba2`; PR #3 continúa abierta, draft, sin fusionar y con head SHA coincidente.
- El run ampliado `45005700564` terminó, pero el workflow global concluyó **failure**. Es importante distinguir: el paso `Index per-image annotations` terminó **success**; el paso siguiente `Build class-aware training manifests` falló y el upload fue omitido. No se publicó artifact.
- El log confirma que se procesaron todos los índices solicitados: A2D2 train/val/test 1000/1000 cada uno; UrbanSyn train 1000/1000, val 751/751 y test 783/783. Total 5.534 filas anotadas (A2D2 3.000 + UrbanSyn 2.534). Esto acredita finalización del indexador per-image, pero no valida integridad de los JSONL mediante artifact descargable ni produce manifiestos balanceados.
- Error reproducible en el paso del planificador: `ModuleNotFoundError: No module named 'src'` al importar `src.urban_ontology` desde `scripts/build_balanced_training_plan.py`. El mismo fallo aparece en el smoke `45005695816`; ambos runs terminan failure y ambos carecen de artifacts.
- El log sí emitió resumen de cobertura. A2D2 semantic frame coverage train/val/test: bicycle 225/3/292; car 882/936/880; lane marking 955/990/846; person 267/17/274; sidewalk 648/191/718; sky 994/1000/997; traffic sign 803/623/836; truck 647/852/534. A2D2 instance object counts train/val/test: bicycle 1263/5/1270; car 10383/6454/9299; person 1341/31/786; truck 1880/4440/1395. Las clases de instancia esperadas no observadas en estos índices incluyen bus, motorcycle, rider y train; no asumir cobertura A2D2 de esas clases.
- UrbanSyn presentó las 19 clases semánticas esperadas en train/val/test. Instancias: ocho clases observadas en los tres splits; conteos de objetos (train/val/test): bicycle 941/730/729; bus 307/222/239; car 5707/4313/4566; motorcycle 578/489/474; person 12865/10125/9773; rider 1230/1030/988; train 60/48/57; truck 367/242/292.
- Estos números son estadísticas de ejecución impresas en logs, no una auditoría independiente de archivos JSONL ni un plan balanceado. No afirmar que el balanceo esté terminado. Los splits de UrbanSyn son experimentales por sample ID, no garantizan independencia por secuencia.
- Próxima acción técnica necesaria: corregir el path de importación del planificador (insertar explícitamente la raíz del repositorio en `sys.path` o convertir la ejecución en módulo), añadir prueba que reproduzca la invocación exacta del workflow y relanzar indexación/plan. Mantener entrenamiento desactivado hasta publicar e inspeccionar artifact completo.
- CI Python actual del HEAD `eff585ef` y probe BDD100K terminaron success (runs `45020490550`, `45020486506`, `45020486542`). `RUN_TRAINING=False`; no hay checkpoints ni métricas de modelos.

#### Corrección del import del planificador y relanzamiento — 2026-11-22

- Se consultó primero el registro vigente y se auditaron HEAD, PR #3 y Actions. HEAD inicial: `4f43c0a3e136880b4e5cc111614b8fd75b49aee4`; PR #3 abierta, draft, no fusionada.
- Se corrigió `scripts/build_balanced_training_plan.py`: añade la raíz del repositorio a `sys.path` antes de importar `src.urban_ontology`. Esto soporta la invocación exacta del workflow (`python scripts/build_balanced_training_plan.py`) sin depender de variables de entorno ni de ejecución como módulo.
- Se añadió `tests/test_balanced_training_plan_cli.py`, que ejecuta el script en un subproceso desde la raíz del repositorio con `--help` y comprueba que el import y la CLI terminan correctamente.
- Commits: corrección `2a9bcd05e9e39014ad7117a1b2e415774159bae8`; prueba `246a656d2e878f21ecaeabfc511f2b8f8413f647`.
- El push de la corrección disparó automáticamente el workflow ampliado de indexación `45038801547` sobre SHA `2a9bcd05`; en la última consulta estaba `in_progress`. Esto vuelve a ejecutar preparación de manifiestos, indexación remota y construcción del plan. No se debe declarar éxito ni artifact hasta consultar el resultado final.
- CI Python del SHA final `246a656d`: runs push `45038810303` y pull_request `45038805388`, ambos en cola al cierre. CI del commit de corrección `2a9bcd05` también tenía run `45038804394` en curso; el run duplicado `45038801549` fue cancelado al supersederse.
- HEAD final observado: `246a656d2e878f21ecaeabfc511f2b8f8413f647`; PR #3 permanece abierta, draft, merged=false y apunta a este HEAD.
- No se inició entrenamiento ni se habilitó `RUN_TRAINING`; continúa `False`. No hay checkpoints ni métricas experimentales nuevas.
- Próximo paso: verificar CI del HEAD final y workflow `45038801547`; si termina correctamente, descargar e inspeccionar íntegramente el artifact (índices JSONL, manifiestos, plan, IDs y cobertura/clases ausentes). Si falla, revisar el nuevo log y corregir antes de avanzar.

#### Integración de balanceo en loaders y estado de cierre de fase — 2026-11-22

- Se consultó el registro antes de auditar rama, PR y Actions. La rama sigue siendo `urban-models-and-benchmark`; PR #3 permanece `open`, `draft=true`, `merged=false`.
- La corrección del import del planificador está incorporada en la rama. La prueba CLI dedicada también está añadida.
- Se integraron las utilidades de balanceo en `src/urban_training.py` mediante `build_urban_train_loader`:
  - tarea semántica: agrega conteos de píxeles exclusivamente de filas train y devuelve pesos para `CrossEntropyLoss`; el muestreo de imágenes se mantiene uniforme;
  - tarea de instancias: crea `WeightedRandomSampler` reproducible y aplica `detection_collate_fn`;
  - valida longitud del índice vs dataset, estado de anotación y rechaza explícitamente filas declaradas como val/test.
- Se añadió `tests/test_urban_training_loader.py` para probar pesos semánticos, sampler/collate de instancias y rechazo de estadísticas de evaluación/desalineadas. Se documentó la interfaz en `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md`.
- Commits de integración: `9919b366` (helper inicial), `51a669fa` (tests), `c74c0f5b` (limpieza de semilla), `39114682` (fixture de instancias), `39a748a4` (documentación). HEAD de la rama al último commit registrado en GitHub: `39a748a42481f068497d3d9bf9ad17a2e8ed5ad1`.
- CI Python del HEAD previo `39114682` está en curso en runs `45040642573` (push) y `45040637665` (PR); ambos estaban instalando PyTorch CPU al cierre. El run del HEAD documental `39a748a4`, `45040654800`, estaba pendiente. No se declara todavía que las nuevas pruebas hayan pasado.
- Workflow de indexación ampliada `45038801547` (SHA `2a9bcd05e9e39014ad7117a1b2e415774159bae8`) continúa `in_progress`. Ya completó preparación de manifiestos; el indexador per-image sigue ejecutándose. El planificador y upload permanecen pendientes; no hay artifact. El endpoint de logs no estuvo disponible (404) mientras el job continúa activo.
- La corrección de import ya fue incorporada en el SHA del workflow activo, pero el resultado real del planificador solo podrá confirmarse cuando la indexación termine. No reiniciar una segunda indexación pesada en paralelo sin necesidad.
- **No se cierra aún la fase de datos/balanceo**: falta que el run publique artifact, descargarlo y auditar seis índices JSONL, seis manifiestos de tarea, plan JSON, conteos, IDs, clases ausentes/no cubiertas y splits. También falta CI verde del HEAD actual.
- El helper de loaders no está conectado a un entrenamiento de producción ni a rutas locales reales. Su prueba es sintética; falta validación con los IDs y rutas reales de los manifiestos después de descargar el artifact y materializar datos autorizados. A2D2 y UrbanSyn deben seguir separados.
- No se inició entrenamiento, no hay checkpoints ni métricas de modelos; `RUN_TRAINING=False`.
- Próxima acción: esperar/consultar los runs de CI y el workflow `45038801547`. Si el workflow termina success, descargar y auditar el artifact. Si el planificador falla, inspeccionar el log final y corregir. No habilitar entrenamiento ni declarar fase cerrada antes de completar esa auditoría.


#### Resultado y auditoría del workflow ampliado de indexación — 2026-11-22

- Se reconsultó este registro antes de comprobar la rama, PR #3 y GitHub Actions. HEAD actual de `urban-models-and-benchmark`: `e3b74c844faff1093218674b777436c15477525c`. PR #3 sigue `open`, `draft=true`, `merged=false`, con el mismo HEAD.
- El workflow ampliado `45038801547`, ejecutado sobre el commit `2a9bcd05e9e39014ad7117a1b2e415774159bae8`, terminó **success**. Los pasos de preparación de manifiestos, indexación per-image, construcción del planificador y publicación del artifact finalizaron correctamente. El fallo anterior de importación del planificador quedó resuelto en esta ejecución.
- Artifact publicado: `14770171764`, `urban-per-image-index-and-balanced-plan-45038801547`, 1.350.995 bytes, SHA-256 declarado por GitHub `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`. Descargado e inspeccionado localmente. Contiene seis índices JSONL, doce manifiestos por tarea/split, el plan JSON y resúmenes de anotaciones/manifiestos.
- Integridad auditada de los seis índices y doce manifiestos: A2D2 1.000/1.000/1.000 (3.000 filas); UrbanSyn 1.000/751/783 (2.534 filas); total 5.534 muestras. Cero IDs nulos o duplicados por split; los conjuntos de `sample_id` de cada índice coinciden exactamente con los de sus manifiestos semántico y de instancias; cero `annotation_status` distintos de `ok`; todos los registros contienen `semantic_pixels` e `instance_counts`.
- No hay solapamiento de `group_id` entre train/val/test. En A2D2 se confirma partición por secuencia: 18 grupos train, 3 val y 2 test. En UrbanSyn hay 1.000/751/783 grupos, uno por sample ID; esto evita repetir el mismo ID entre splits, pero **no demuestra independencia temporal por secuencia** porque no hay metadata de secuencia verificada.
- Cobertura semántica observada en todos los splits: A2D2, 8 clases (`bicycle`, `car`, `lane marking`, `person`, `sidewalk`, `sky`, `traffic sign`, `truck`); UrbanSyn, las 19 clases de su taxonomía. Cobertura de instancias: A2D2, 4 clases (`bicycle`, `car`, `person`, `truck`); UrbanSyn, las 8 clases dinámicas esperadas. Para A2D2 las clases de instancia `bus`, `motorcycle`, `rider` y `train` están ausentes/no cubiertas en los tres splits; no entrenar ni reportar estas clases como soportadas por A2D2.
- Limitación importante del nombre “balanced”: el plan se generó, pero **no hace downsampling ni impone un cap por clase** (`per_class_cap=null`). Los doce manifiestos conservan todos los elementos de cada split (100%); por tanto no son conjuntos con distribución equilibrada. En A2D2 val la cobertura es especialmente débil para `bicycle` (3/1.000 frames) y `person` (17/1.000), con 5 y 31 instancias respectivamente. El plan informa correctamente clases no disponibles/no cubiertas. Los pesos semánticos y el sampler de instancias implementados en `src/urban_training.py` son una herramienta distinta y aún no equivalen a validar balanceo efectivo durante entrenamiento.
- Los manifiestos semántico y de instancias contienen los mismos conjuntos de `sample_id`, pero su **orden no es idéntico en train** para ambos datasets (sí coincide en val/test). El loader helper exige que las filas de anotación estén en el mismo orden que el dataset, pero actualmente no valida identidad por `sample_id`. Antes de usarlo con datos reales hay que construir dataset e índice desde el mismo manifiesto/orden o añadir una comprobación explícita de IDs; no asumir que dos manifiestos con los mismos IDs están alineados posicionalmente.
- CI Python del HEAD actual `e3b74c84` terminó success en los runs `45040701149` (pull request) y `45040695540` (push). El probe BDD100K `45040695536` también terminó success.
- Estado global: la **indexación remota y generación del plan sí finalizaron**, y el artifact superó las comprobaciones de integridad indicadas. La fase de balanceo/entrada a entrenamiento no debe declararse completamente cerrada: falta resolver el alineamiento por `sample_id` del loader, decidir si se necesita un subconjunto realmente balanceado o aceptar el split completo con ponderación/sampler, y validar loaders con rutas locales autorizadas. `RUN_TRAINING=False`; no hay entrenamiento de producción, checkpoints ni métricas de modelo.
- Próximo paso recomendado: reforzar `build_urban_train_loader` para verificar IDs y orden, definir el protocolo de balanceo real por dataset/tarea y probar los loaders contra una materialización pequeña de los manifiestos sin mezclar A2D2 y UrbanSyn. Mantener PR #3 abierta y draft.


#### Corrección de alineamiento por sample_id y balanceo efectivo — 2026-11-22

- Se consultó el registro antes de iniciar y se re-auditó rama, PR #3 y Actions. HEAD observado al iniciar esta intervención: `74e51111848eedcfbb79cfb30c8d6f1284c73d8e`. PR #3 seguía abierta, draft y sin fusionar, con ese HEAD. Se detectaron dos runs de CI Python y el probe BDD100K fallidos sobre ese SHA; la descarga de logs de los jobs devolvió 404, por lo que la causa detallada no pudo confirmarse en esta sesión.
- Se verificó el resultado de indexación ampliada `45038801547`: job completo con success; artifact `14770171764` presente y no expirado. La auditoría registrada anteriormente confirma 5.534 muestras, integridad de IDs/manifiestos y cobertura por dataset/tarea. Se mantiene la limitación: los manifiestos de train semántico e instancias no tienen necesariamente el mismo orden.
- En `src/urban_training.py`, `build_urban_train_loader` ahora exige que el dataset exponga `records` con `sample_id`, y valida identidad y orden exactos contra el índice de anotaciones. Rechaza IDs vacíos, duplicados y desalineamientos. Esto evita depender únicamente de que ambas listas tengan igual longitud.
- En `tests/test_urban_training_loader.py` se añadieron casos para orden distinto con el mismo conjunto de IDs y para IDs duplicados; las fixtures ahora exponen registros identificables.
- En `scripts/build_balanced_training_plan.py`, el límite por clase ahora excluye cualquier muestra que excedería el límite de al menos una clase presente. Si no quedan candidatos válidos, la selección train termina antes de alcanzar el máximo global. El resumen informa el límite y las muestras no seleccionadas. El default de la API/CLI se fija en 200; 0 desactiva el límite.
- En `.github/workflows/index-remote-annotations.yml` se añadió el input manual `per_class_cap` (default 200) y se pasa al planificador. Validation/test permanecen completos y en orden original; el límite afecta solo train.
- Se añadieron pruebas en `tests/test_urban_ontology_and_balance.py` para comprobar que el límite por clase se respeta y puede reducir realmente el conjunto de entrenamiento.
- Commits de esta intervención: `6826b039` loader; `9a1ff54e` tests de loader; `9060ca40` planificador; `9cbf78ee` tests del planificador; `aaf54668` workflow. Se actualizaron también `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md`.
- Advertencia metodológica: el cap 200 es un parámetro inicial de experimento, no prueba de distribución perfectamente equilibrada. Deben revisarse las distribuciones y el tamaño final de cada subconjunto al inspeccionar el siguiente artifact; no usar val/test para calcular pesos ni seleccionar muestras.
- Pendiente al cierre: añadir/confirmar CI verde del HEAD final; revisar el run de indexación provocado por el cambio de planificador/workflow y auditar su nuevo artifact; validar loaders con una pequeña materialización local de manifests. No se inicia entrenamiento y `RUN_TRAINING=False`.
- Se mantiene PR #3 abierta, en draft y sin fusionar.


#### Revisión de CI y ejecución remota tras la integración — 2026-11-22

- HEAD final de esta intervención: `b4c71ca119dc7ae9a063ed4643ca0a2eaa791d9a`. La rama y PR #3 apuntan al mismo SHA; PR #3 sigue abierta, draft y sin fusionar.
- El workflow de indexación provocado por el cambio de planificador (`45066893040`, SHA `aaf54668`) terminó failure antes de iniciar el job en un runner: la API de GitHub informa `runner_id=0`, `runner_name` vacío y `steps=[]`. No se generó artifact. Esto no demuestra un error del indexador ni del planificador; tampoco permite validar el nuevo cap. La ejecución previa de indexación `45038801547` y su artifact `14770171764` permanecen válidos para la configuración anterior sin cap.
- CI Python del HEAD final (`45066964661`) también terminó failure en 1 segundo con `runner_id=0`, `runner_name` vacío y `steps=[]`; los intentos anteriores de CI de esta secuencia presentan el mismo patrón. El probe BDD100K (`45066964670`) también falla sin runner asignado. Los endpoints de logs devuelven 404 y la API no expone pasos ni salida de tests. Se registra como bloqueo de infraestructura/ejecución de GitHub Actions, no como pruebas aprobadas ni como fallo de código confirmado.
- Por tanto, las nuevas pruebas de alineamiento y cap están añadidas pero **no ejecutadas con éxito** en CI. Se requiere reintentar cuando GitHub Actions asigne runners y revisar el primer error real si aparece.
- El artifact del workflow de indexación con cap 200 no existe todavía. No se ha inspeccionado una nueva selección train ni se puede informar su tamaño/distribución. No repetir indexación completa hasta resolver la asignación de runners o ejecutar el planificador sobre los índices ya almacenados de forma controlada.
- La documentación de balanceo y este registro se actualizaron en la rama. No se inició entrenamiento, `RUN_TRAINING=False`; no hay checkpoints ni métricas experimentales nuevas.


- **Comprobación final de CI tras actualizar el registro:** los runs `45067044843` (Python tests) y `45067044841` (probe BDD100K), disparados sobre el HEAD `1980184c`, también terminaron failure en 1–2 segundos con `runner_id=0`, `runner_name` vacío y `steps=[]`. Se confirma que GitHub Actions no asignó runner; no se ejecutó pytest ni el probe. Se conserva el bloqueo y no se interpretan como fallos de las pruebas del código.


#### Reintento controlado de GitHub Actions — 2026-11-22

- A petición del usuario se reintentaron únicamente los jobs fallidos sobre el HEAD `eafe85ff9348615fa730f5dd3b95536ae488811c`: Python tests (push, job original `137345519621`), Python tests (pull_request, `137345536073`) y BDD100K probe (`137345519206`). La API aceptó los tres reintentos (`success=true`).
- Los reintentos generaron attempt 2 de los runs `45067078270`, `45067083863` y `45067078237`. Al consultar sus jobs, los dos jobs de Python volvieron a terminar `failure` con `runner_id=0`, `runner_name` vacío y `steps=[]`. El probe BDD100K también terminó `failure` con `runner_id=0`, sin runner y sin pasos. Por tanto, pytest, instalación de dependencias y probe no llegaron a ejecutarse; no hay fallo de código confirmado ni pruebas aprobadas.
- El reintento demuestra que el bloqueo persiste incluso al volver a ejecutar los jobs existentes. La conexión GitHub permite solicitar re-run, pero no administrar/inspeccionar los runners de organización/repositorio desde las APIs disponibles en esta sesión. Se requiere que el propietario revise en GitHub Actions la disponibilidad/estado de runners y límites/colas de ejecución, o que soporte GitHub investigue la asignación. No se cambió la configuración de runners ni se tocaron secretos/permisos.
- Se mantiene el HEAD `eafe85ff9348615fa730f5dd3b95536ae488811c`, PR #3 abierta y draft sin fusionar. `RUN_TRAINING=False`. No se lanzó otra indexación remota completa ni se generó artifact nuevo.
- Próximo paso: resolver en GitHub la asignación de runners y después volver a ejecutar los jobs de CI; solo cuando haya ejecución real (runner asignado y steps presentes) evaluar logs y resultados. Tras CI verde, ejecutar el planificador sobre los índices existentes con `per_class_cap=200`, auditar tamaño/distribución y validar loaders con una pequeña materialización.


#### Diagnóstico de configuración de GitHub Actions a partir de capturas — 2026-11-23

- El usuario mostró `Settings → Actions → Runners`: GitHub indica “There are no runners configured”. Esto solo confirma que no hay runners **autohospedados** registrados; no es requisito para los workflows actuales, que usan `runs-on: ubuntu-latest` y esperan runners alojados por GitHub.
- En `Settings → Actions → General`, la opción seleccionada es **Allow all actions and reusable workflows**. Por tanto, la política de acciones no está deshabilitando los workflows.
- En la misma captura, `GITHUB_TOKEN` está limitado a **Read repository contents and packages permissions**. Es una política de permisos del token, no una explicación suficiente del fallo de asignación de runner. Puede impedir pasos que necesiten escribir en el repositorio mediante `GITHUB_TOKEN`, pero no impide por sí sola que GitHub asigne un runner y ejecute pytest.
- La opción para ejecutar workflows de pull requests procedentes de forks está desmarcada; no es relevante para la PR #3 del mismo repositorio.
- Las capturas no muestran el estado de cuota/facturación ni el motivo de rechazo/provisión de los runners alojados por GitHub. Por tanto, la causa exacta sigue sin confirmarse. No crear un runner autohospedado como solución automática.
- Se revisaron los jobs de los runs `45166026316` y `45166019193`: ambos figuran como `failure`, sin pasos disponibles en la respuesta del conector; no hay evidencia de que pytest haya llegado a ejecutarse. El run `45166026316` es el run de Python tests observado sobre el SHA de continuidad `cb7b5708a90ed663241ef48d06fbcc8a7b6e892b`.
- Próxima comprobación manual: en GitHub, revisar **Billing and licensing → Usage** (minutos de GitHub Actions incluidos/consumidos y límites de gasto) y la sección **Actions → General → Runner images** si aparece disponible; comprobar también avisos de cuenta/organización. No cambiar permisos del token ni habilitar workflows de forks sin una necesidad concreta.
- Se mantiene PR #3 abierta y en draft, sin fusionar. No se lanzó entrenamiento; `RUN_TRAINING=False`.


#### Revisión de uso medido de GitHub — 2026-11-23

- El usuario compartió la pantalla de cuenta Billing and licensing → Usage, periodo Nov 1–30, 2026. En el gráfico se aprecia un uso bruto acumulado cercano a USD 12; el desglose visible muestra 21-nov: gross USD 4.28 / billed USD 0; 22-nov: gross USD 7.72 / billed USD 0; 23-nov: gross <USD 0.01 / billed USD 0.
- La captura corresponde a uso medido agregado de la cuenta; no identifica el producto/servicio que originó cada importe. El importe facturado visible es USD 0. No permite concluir que se hayan agotado minutos gratuitos de GitHub Actions, que exista una deuda ni que el uso medido sea exclusivamente Actions. Hace falta desglosar las filas/detalle de uso o filtrar por producto GitHub Actions y revisar minutos incluidos/consumidos, si esa vista está disponible.
- Se volvió a leer este registro antes de auditar. La búsqueda de PRs sigue mostrando la PR #3; no se ha realizado ninguna acción de cierre o merge. La rama urban-models-and-benchmark sigue localizada. La API del conector no devolvió el SHA del HEAD en esta consulta, por lo que no se afirma un SHA nuevo; el último commit documental conocido es c2d75debc26c52efef11f18faf556b4973104a5b.
- CI Python asociado a ese commit: run 45167228310, terminó failure; el job pytest aparece sin pasos/logs disponibles mediante el conector. No se puede confirmar que pytest se ejecutara ni identificar causa a partir de este resultado. No atribuirlo al uso medido de Billing.
- Conclusión: el uso bruto facturado en la captura no explica por sí solo la falta de runner. Próximo paso de diagnóstico: expandir las filas del desglose y/o filtrar Usage por producto/servicio GitHub Actions, revisar el detalle de minutos y cualquier límite de gasto/alerta; alternativamente abrir Billing → Overview para comprobar si hay restricciones de cuenta. No modificar permisos de workflows ni habilitar gasto sin necesidad y autorización.
- Se mantiene la política del proyecto: PR #3 debe permanecer abierta y draft, sin fusionar; RUN_TRAINING=False; no se ha iniciado entrenamiento ni se ha generado artifact nuevo.


#### Desglose detallado de consumo de Actions — 2026-11-23

- Nueva captura de Billing → Usage, con filas expandidas: 21-nov-2026 SKU `Actions Linux`, 713 min × USD 0.006 = USD 4.28 gross / USD 0 billed; 22-nov-2026 `Actions Linux`, 1,287 min × USD 0.006 = USD 7.72 gross / USD 0 billed. Total: 2,000 minutos Linux y USD 12.00 gross, USD 0 billed. Además, `Actions storage` 0.02 GB-hr el 22 y 23 nov, gross <USD 0.01, billed USD 0.
- La coincidencia con el límite de referencia de GitHub Free es muy fuerte. La documentación oficial actualizada de GitHub explica que GitHub Free incluye USD 12 de compute usage al mes (equivalente aproximadamente a 2,000 min de runner Linux estándar a USD 0.006/min); las cantidades incluidas se consumen primero y se reinician al inicio del ciclo de facturación. La documentación también indica que el uso adicional puede bloquearse cuando se agota el incluido y no hay método de pago válido. Fuente: https://docs.github.com/en/billing/concepts/product-billing/github-actions
- La captura prueba consumo de USD 12 brutos de Actions Linux, no muestra directamente el plan, el saldo incluido restante, el método de pago ni el estado del presupuesto. Por eso la hipótesis principal es que se agotó el crédito mensual incluido, pero debe confirmarse en Billing → Overview y Budgets and alerts; no afirmar como hecho que el gasto adicional está bloqueado hasta ver ese estado.
- El precio y las unidades explican por qué el importe facturado es cero: el gross usage es el valor calculado del uso; el importe billed visible sigue en cero, compatible con el uso cubierto por la asignación incluida. No hay indicación en la captura de cargos cobrados.
- El patrón anterior de runs con `runner_id=0`, sin runner y sin steps es compatible con rechazo/provisión bloqueada antes de iniciar el job, pero el conector no aporta la anotación exacta de facturación. No atribuirlo definitivamente sin revisar el estado de presupuesto/uso.
- Siguiente paso: abrir Billing and licensing → Budgets and alerts y Billing → Overview. Verificar si el presupuesto de GitHub Actions está en USD 0 con `Stop usage when budget limit is reached`, si el estado dice `Usage blocked`, el plan y la fecha de reinicio del ciclo. No añadir método de pago ni elevar presupuesto sin consentimiento explícito. Alternativa sin cargos: esperar al reinicio del ciclo; para CI inmediato habría que valorar runner autohospedado en un equipo/servidor controlado, que requiere instalación y disponibilidad continua.
- PR #3 se mantiene abierta y draft, sin fusionar. `RUN_TRAINING=False`; no se ha iniciado entrenamiento ni indexación nueva.


#### Inspección de presupuestos y alertas — 2026-11-23

- Captura de Billing → Budgets and alerts: aparecen cinco presupuestos a nivel de cuenta (Packages, Actions, Codespaces, All AI Credit SKUs, Git LFS). Cada uno muestra USD 0.00 / USD 0.00 spent, barra al 100% y advertencia. Para Actions el límite configurado visible es USD 0.00.
- La vista de lista no expone el detalle de configuración del presupuesto, en particular si está activada la opción `Stop usage when budget limit is reached`, ni el estado explícito `Usage blocked`. Por tanto, no se puede afirmar aún que el presupuesto cero esté bloqueando Actions. Es una hipótesis plausible que debe verificarse abriendo la fila `Leohf04 · Actions`.
- Pasos solicitados al usuario: abrir la fila `Leohf04 · Actions` y compartir la pantalla de detalle donde aparezcan monto, periodo, alertas y acción al alcanzar el límite. No cambiar el presupuesto ni permitir gasto adicional hasta revisar esa configuración y contar con autorización.
- Auditoría de continuidad: PR #3 sigue listada como abierta; no se ha solicitado cierre ni merge. CI en commit documental previo `66c10689b749590e70aee1cccee44619da4e7fc7`: run `45171580626` Python tests terminó failure; job `pytest` no expone steps/logs en la respuesta del conector. No hay evidencia de ejecución real de pytest ni explicación del fallo.
- No se dispone en esta llamada de SHA HEAD actual devuelto por API de rama; se conserva como último commit documental confirmado `66c10689b749590e70aee1cccee44619da4e7fc7` hasta la confirmación del commit que actualice este registro.
- PR #3 debe permanecer abierta y draft, sin fusionar. `RUN_TRAINING=False`. No se ha lanzado entrenamiento ni indexación nueva.

#### Revisión prioritaria de asignación de runners y CI — 2026-11-23

- Se volvió a consultar primero este registro y se auditó rama, PR #3, workflows y ejecuciones recientes.
- HEAD de `urban-models-and-benchmark`: `224abda6e60d9b18858553177cf69e37e25f933f`. PR #3 apunta a ese HEAD y permanece `open`, `draft=true`, `merged=false`; base `fix/evaluacion-y-pipeline`.
- Primera comprobación solicitada: workflow **Python tests**. Los runs `45171863834` (evento `push`) y `45171874210` (evento `pull_request`) terminaron `failure` en aproximadamente 2 segundos. Los jobs `137683141177` y `137683176478` reportan `runner_id=0`, `runner_name=""`, labels `ubuntu-latest` y `steps=[]`. No se ejecutaron checkout, setup-python, instalación, compileall ni pytest. Por tanto no hay resultado de pruebas de código.
- El probe BDD100K `45171863822` presenta el mismo patrón: `failure`, runner 0 y lista de pasos vacía. No se considera un error del probe ni se repite ahora.
- Se inspeccionó `.github/workflows/tests.yml`: solicita `ubuntu-latest`, timeout 30 min y declara concurrencia `python-tests-${{ github.ref }}` con `cancel-in-progress: true`. Push y pull_request generan grupos distintos por sus refs; la política cancela una ejecución previa del mismo ref, pero no explica que los jobs actuales terminen sin runner. Hay dos ejecuciones duplicadas por los eventos push y pull_request, pero no se cambió el workflow porque no corrige la ausencia de runner.
- Se inspeccionó `.github/workflows/index-remote-annotations.yml`: también solicita `ubuntu-latest`; no se ejecutó ni se despachó indexación nueva. No se repitió descarga de anotaciones.
- La auditoría de los eventos confirma ejecuciones recientes para el mismo HEAD por `push` y `pull_request`; no se observó ningún run Python con steps ejecutados en este HEAD.
- Sobre facturación: el usuario compartió un desglose anterior de 2.000 minutos `Actions Linux` (USD 12 gross, USD 0 billed) y una lista de presupuestos donde Actions figura con límite USD 0. El detalle de la regla `Stop usage when budget limit is reached`, saldo incluido restante, estado `Usage blocked` y fecha exacta de reinicio no está disponible en las capturas/API revisadas. La cuota/presupuesto sigue siendo una hipótesis prioritaria, no una causa confirmada.
- Diagnóstico actual: bloqueo antes de asignar runner confirmado; causa raíz (presupuesto/uso incluido u otra restricción de cuenta/servicio) aún no identificada. La configuración de Actions permite todos los workflows y el token read-only no explica por sí solo que no se asigne runner.
- No se modificó código ni se lanzó re-run adicional para evitar consumir más uso sin evidencia de que se pueda provisionar un runner. No se generó artifact nuevo.
- Próximo paso: comprobar en el detalle del presupuesto Actions si está activado `Stop usage when budget limit is reached` y consultar Billing Overview para el estado de uso y reinicio. Si el uso está bloqueado, no habilitar gasto sin autorización; esperar reinicio del ciclo o evaluar runner autohospedado controlado. Una vez resuelta la asignación, ejecutar primero Python tests y confirmar runner asignado + steps + salida de pytest; después planificar con los índices existentes y auditar distribución/diversidad.
- Se mantiene PR #3 abierta y draft, sin fusionar. `RUN_TRAINING=False`. No entrenamiento ni indexación nueva.

#### Alternativa gratuita a GitHub Actions — Colab Free — 2026-11-23

- El usuario pregunta si se puede continuar gratuitamente fuera de GitHub Actions tras alcanzar su límite. Decisión recomendada: trasladar ejecución de pruebas y tareas de preparación/análisis a Google Colab Free, manteniendo GitHub como repositorio y control de versiones.
- Se auditó de nuevo la rama: HEAD previo a este registro `41ec53a6eeafe2e123197c2cc770759fb61941ee`. PR #3 sigue `open`, `draft=true`, `merged=false`.
- Los runs más recientes sobre ese HEAD terminaron: Python push `45193367119`, Python PR `45193382124`, BDD100K probe `45193367281`. Los tres jobs reportan `runner_id=0`, nombre vacío y `steps=[]`; GitHub Actions continúa sin ejecutar comandos.
- Se confirmó que el notebook existente `notebooks/colab_free_urban_training.ipynb` ya prepara Colab, montaje de Drive, clonación del repo privado en la rama, instalación de dependencias adicionales sin reinstalar PyTorch/Torchvision, diagnóstico de GPU y pruebas BDD100K sintéticas/muestra. Usa `GITHUB_TOKEN` como Colab Secret (Fine-grained, Contents read-only) o entrada oculta con getpass; no exponer token en celdas ni chats.
- Rutas del notebook: repo `/content/Procesamiento-de-Im-genes-`, datos temporales `/content/datasets`, resultados persistentes en Drive `/content/drive/MyDrive/ProcesamientoImagenes/resultados/{checkpoints,metricas,graficas,informes,logs}`.
- Plan de migración: (1) abrir notebook desde GitHub/Colab; (2) clonar HEAD actual y verificar SHA; (3) ejecutar primero pruebas Python de manera selectiva y luego `pytest -q` (incluyendo adaptadores multidataset, alineación sample_id y planificador); (4) no iniciar entrenamiento; (5) recuperar/reutilizar el artifact existente de indexación `14770171764` y ejecutar únicamente el planificador con `per_class_cap=200`, si los JSONL/manifiestos están disponibles, sin volver a descargar anotaciones; (6) auditar retención, clases, tamaño y diversidad antes de aceptar el plan. La disponibilidad y descarga del artifact debe verificarse en el entorno; no se afirma que ya esté descargado.
- Colab Free no garantiza GPU, sesiones ilimitadas ni continuidad; las pruebas y el planificador deben ejecutarse como tareas acotadas y guardar logs/resultados en Drive. Para estas tareas CPU puede bastar; GPU no es requisito para pytest ni para el planificador.
- Kaggle Notebooks es alternativa secundaria gratuita, pero no es la primera elección porque el notebook Colab ya existe y tiene configurada la autenticación privada y persistencia en Drive.
- No se cambió el código, no se lanzó entrenamiento, no se volvió a descargar ni indexar datasets y no se autorizó gasto. `RUN_TRAINING=False). PR #3 sigue abierta y draft.

#### Preparación operativa de Google Colab Free — 2026-11-23

- A petición del usuario se preparó el notebook existente para continuar la validación fuera de GitHub Actions, sin iniciar entrenamiento.
- Auditoría inicial: HEAD `60070adaf9c7dd14cea34665989f60accdb0edf4`; PR #3 abierta, draft y sin merge. Los runs sobre HEAD `60070ada` (Python push `45193569865`, Python PR `45193585043`, BDD probe `45193569796`) acabaron en failure con `runner_id=0`, `runner_name=""`, `steps=[]`; no se ejecutaron tests.
- Se confirmó por GitHub API que el artifact `14770171764` del run `45038801547` sigue disponible/no expirado al momento de esta consulta, tamaño 1,350,995 bytes, expiración indicada 2026-12-22. Contiene índices JSONL, plan/manifiestos enriquecidos. Workflow subió `artifacts/annotation_index/`, `artifacts/balanced/` y resúmenes de manifests; no subió los manifiestos base completos.
- Se actualizó `notebooks/colab_free_urban_training.ipynb` para incluir: pruebas dirigidas `test_multidataset_adapters.py`, `test_urban_training_loader.py`, `test_balanced_training_plan_cli.py`, `test_remote_annotation_index.py`; suite completa `pytest -q` condicionada a éxito de las dirigidas; descarga autenticada del artifact existente por REST API (requiere token fine-grained `Contents: read` y `Actions: read`); extracción ZIP con comprobación contra path traversal; reconstrucción de manifiestos base desde los JSONL semánticos enriquecidos existentes; ejecución local del planificador con `per_class_cap=200`; persistencia del informe y evidencia de entorno en Drive.
- La reconstrucción es viable porque el artifact contiene los JSONL enriquecidos `{dataset}_semantic_{split}.jsonl` que retienen los campos del manifiesto base y los seis índices `{dataset}_{split}.annotations.jsonl`. La celda comprueba presencia de todos antes de ejecutar. No indexa ni descarga datos fuente.
- Se verificó que el notebook modificado es JSON válido (34 celdas) y se guardó en commit `0f1cb95bffca2c5dca252afc0ef200b364022435`.
- Se auditó después del commit: HEAD de rama `0f1cb95bffca2c5dca252afc0ef200b364022435`; PR #3 sigue abierta y draft, sin fusionar. Se generó run Python `45193854666` queued sobre este commit al cierre; no hay resultado de ejecución local en Colab.
- Limitación operativa: no existe herramienta para abrir/ejecutar una sesión Colab en nombre del usuario ni para autorizar Google Drive/Colab desde esta conversación. El notebook queda preparado y enlazado; el usuario debe abrirlo en Colab, conceder Drive y guardar el secreto/token requerido. No pedir token en el chat. El PAT debe tener acceso mínimo a este repositorio y permisos de solo lectura Contents + Actions.
- Orden de ejecución: montar Drive, clonar rama, instalar dependencias/diagnosticar PyTorch-Torchvision, correr tests dirigidos; si pasan, suite completa; recuperar artifact y generar plan cap200; revisar retención por clase y diversidad antes de aceptar. Si una prueba falla, detener y conservar logs. CPU basta para tests/planificador; GPU no es requisito. Colab Free no garantiza disponibilidad ni sesiones persistentes.
- No se ejecutó notebook desde aquí, por tanto no se afirma que tests pasen ni que plan cap200 haya sido generado. No se inició entrenamiento, no se descargaron datasets/anotaciones fuente, no se autorizó gasto. `RUN_TRAINING=False`.
- Se mantiene PR #3 abierta, draft y sin fusionar.


#### Diagnóstico de suite completa en Google Colab — 2026-11-23

- El usuario informó que las cuatro pruebas dirigidas de la celda 5.3 terminaron con código 0, pero la suite completa de la celda 5.4 terminó con código 1 y lanzó el RuntimeError de parada previsto.
- La evidencia compartida contiene únicamente el código de salida y el traceback del RuntimeError; no incluye la salida previa de pytest (resumen de fallos, nombres de tests ni excepciones originales). Por tanto, la causa raíz todavía no está identificada y no se atribuye el fallo a dependencias, CUDA ni a un módulo concreto.
- Se consultó el registro antes de intervenir y se revisó el PR #3, que continúa listado en el repositorio. Se consultó CI asociado al commit documental a4b6daf1e409fe14369ddfc5a40906792ebd2a62: run Python tests 45193916788 terminó failure; el job pytest 137759177336 no devuelve steps/logs en el conector. Esta ejecución de Actions no aporta evidencia diagnóstica del fallo local de Colab.
- No se lanzó ningún rerun de Actions, no se modificó código y no se inició entrenamiento ni se ejecutó el plan cap200. Se mantiene RUN_TRAINING=False; PR #3 no debe fusionarse.
- Próximo paso: obtener la salida real de pytest en Colab con stdout y stderr combinados, conservarla en Google Drive y compartir el resumen de fallos. Hasta entonces, detener el flujo antes de las celdas 5.5–5.7 y no considerar aprobada la suite completa.


#### Corrección del balanceador tras suite Colab — 2026-11-23

- El usuario compartió la salida diagnóstica completa de pytest en Colab: `1 failed, 75 passed in 26.93s`. La única prueba fallida fue `test_greedy_balancer_enforces_per_class_cap_and_can_reduce_training_set` (tests/test_urban_ontology_and_balance.py:184): se esperaba seleccionar 2 muestras, pero el algoritmo seleccionó solo `mixed`.
- Causa identificada en `scripts/build_balanced_training_plan.py`: el score sumaba las ganancias marginales de todas las clases de una muestra. Con `per_class_cap=1`, una muestra mixta `car+person` obtenía una puntuación agregada alta y ocupaba simultáneamente los dos cupos, impidiendo seleccionar una muestra individual de cada clase.
- Corrección aplicada en commit `bd52609f472bb4b0ea0632695d713297ccd76cbc`: cuando el cap está activo, el objetivo ahora promedia las ganancias marginales por clase, para evitar que una muestra multilabel consuma desproporcionadamente varios cupos en una sola selección. Sin cap se conserva el score agregado anterior. Se mantiene selección determinista por semilla y desempate SHA-256.
- La corrección se ha guardado en la rama `urban-models-and-benchmark`. Todavía no se ha ejecutado pytest después del cambio; requiere actualizar el clon de Colab con `git pull --ff-only` y repetir primero la prueba fallida y después la suite completa. No declarar resuelto hasta obtener ambas salidas satisfactorias.
- No se ejecutó el plan cap200 ni se descargó el artifact en esta intervención. No se inició entrenamiento; `RUN_TRAINING=False`. PR #3 permanece abierta, draft y sin fusionar.
- Próximo paso: en Colab actualizar el repositorio a `bd52609f472bb4b0ea0632695d713297ccd76cbc`, ejecutar `pytest -q tests/test_urban_ontology_and_balance.py::test_greedy_balancer_enforces_per_class_cap_and_can_reduce_training_set`, luego `pytest -q`. Si ambas pasan, continuar con la recuperación del artifact existente y auditar el plan antes de aceptarlo.


## 2026-11-23 — Notebook autónomo de pruebas completas en Colab

- El usuario pidió un flujo de pruebas completo que solo requiera abrir Colab y ejecutar las celdas.
- Se creó [`notebooks/colab_validacion_completa.ipynb`](../blob/urban-models-and-benchmark/notebooks/colab_validacion_completa.ipynb), separado del notebook de entrenamiento para no mezclar validación con preparación de datasets o experimentos.
- El notebook monta Google Drive para persistir evidencia, clona/actualiza la rama privada `urban-models-and-benchmark` mediante Fine-grained PAT de solo lectura (`Contents: Read-only`, secreto Colab `GITHUB_TOKEN` o entrada oculta), instala dependencias de pruebas sin reinstalar PyTorch/Torchvision y ejecuta en orden: (1) la prueba dirigida del balanceador que falló en la sesión anterior y (2) la suite completa `pytest -q`, aun si la prueba dirigida falla.
- Guarda logs separados y resumen JSON en `MyDrive/ProcesamientoImagenes/validacion_colab`. No descarga datasets, no usa GPU deliberadamente y no inicia entrenamiento.
- Se corrigieron los escapes de nueva línea en el código del notebook y se verificó que el JSON del notebook se puede analizar. La ejecución real en Colab queda pendiente; no se afirma que las pruebas pasen.
- No se alteró el notebook de entrenamiento existente. PR #3 debe seguir abierta, draft y sin fusionar; `RUN_TRAINING=False`.
- Próximo paso: el usuario abre el notebook nuevo y selecciona **Entorno de ejecución → Ejecutar todas**. Revisar el resumen y logs antes de continuar con artifact/plan de balanceo.


#### Validación completa satisfactoria en Google Colab Free — 2026-11-23

- El usuario ejecutó correctamente el notebook `notebooks/colab_validacion_completa.ipynb` en Colab Free, rama `urban-models-and-benchmark`, HEAD `4733ca5e0d0bad1039be429e790579c55a05d520`.
- La prueba dirigida `tests/test_urban_ontology_and_balance.py::test_greedy_balancer_enforces_per_class_cap_and_can_reduce_training_set` pasó: **1 passed in 0.10s**, código de salida 0.
- La suite completa `pytest -q` pasó: **76 passed in 39.73s**, código de salida 0. Queda confirmada en Colab la corrección del balanceador que antes fallaba.
- El resumen de ejecución confirma `passed=true`, `training_started=false` y `datasets_downloaded=false`. Logs persistidos en Google Drive: `MyDrive/ProcesamientoImagenes/validacion_colab/prueba_balanceador_20261123_154909.log` y `suite_completa_20261123_154909.log`; resumen JSON `resumen_pruebas_20261123_154909.json`.
- Auditoría GitHub posterior: HEAD sigue en `4733ca5e0d0bad1039be429e790579c55a05d520`; PR #3 permanece `open`, `draft=true`, `merged=false`. Los workflows de Actions recientes siguen terminando en failure (runs Python `45198525405` y `45198512640`, probe BDD `45198512490`); la respuesta disponible del conector no incluye pasos ni información suficiente para diagnosticar la causa. Esto no invalida la ejecución independiente y satisfactoria en Colab.
- No se inició entrenamiento, no se descargaron datasets y no se generó todavía un plan nuevo con cap 200.
- Próximo paso autorizado por el flujo de trabajo: recuperar en Colab el artifact de indexación existente `14770171764` (run `45038801547`), reconstruir manifiestos a partir de los JSONL enriquecidos y ejecutar el planificador con `per_class_cap=200`; después inspeccionar retención/tamaño por split, cobertura de clases, clases no disponibles/no cubiertas, muestras excluidas y diversidad antes de considerar válido el plan. La recuperación requiere un PAT con `Actions: Read-only` además de `Contents: Read-only`; no pedir el token en el chat. No volver a indexar ni descargar datasets fuente.
- Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.


#### Artifact recuperado y auditoría cap 200 — 2026-11-23

- Se consultó primero el registro y se auditó HEAD/PR/Actions. HEAD inicial `63b8f35c39f9c66fab808e5dd3c60a8a9cb3d633`; PR #3 sigue abierta, draft y sin merge. Los Actions recientes continúan fallando sin información de steps/runner suficiente para diagnosticar; no se lanzaron nuevos reruns.
- Artifact `14770171764` del run `45038801547` se encontró vigente hasta 2026-12-22, 1.350.995 bytes. Se descargó e inspeccionó el ZIP; SHA-256 verificado: `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`.
- Hallazgo de estructura: el artifact no contiene manifiestos base en una carpeta independiente. Sí contiene manifiestos semánticos e instancias enriquecidos en `balanced/`; el plan previo tenía `per_class_cap=null`, por lo que conservaba todas las filas. Se reconstruyeron los manifiestos retirando `semantic_pixels`/`instance_counts`, recuperando el orden determinista original con SHA-256(seed:sample_id), y contrastando las estadísticas con los seis índices. Verificación: 6/6 splits, 5.534 filas, IDs únicos, sets de IDs idénticos entre tareas y estadísticas/metadatos coincidentes.
- Se reprodujo localmente la función determinista `greedy_balanced_select` del script actual, con semilla 2026, promedio de ganancias bajo cap y desempate SHA-256, para generar el plan cap 200. Este cálculo local no descarga RGB/máscaras ni reindexa datos. El notebook `notebooks/colab_generar_plan_cap200.ipynb` quedó añadido para volver a ejecutar el CLI real en Colab, verificar el SHA-256 del artifact, reconstruir manifiestos y guardar los resultados en Drive.
- Resultados train cap 200: A2D2 semántica 206/1000 (20,6 %); A2D2 instancias 257/1000 (25,7 %); UrbanSyn semántica 200/1000 (20,0 %); UrbanSyn instancias 209/1000 (20,9 %). Cap respetado; val/test completos. A2D2: 12 clases semánticas y 4 de instancias no disponibles; UrbanSyn cubre 19/19 clases semánticas y 8/8 de instancias. A2D2 conserva 15/18 secuencias en semántica y 17/18 en instancias.
- Sensibilidad: cap 300 retiene 30–36 %, cap 400 40–46 %, cap 500 50–56 %, cap 700 70–76 %. Cap 200 se considera demasiado agresivo para train principal y queda solo como ablación. Recomendación: baseline train completo, aplicar pesos semánticos/sampler de instancias ya implementados por dataset y train-only; considerar cap 500/700 solo como ablación, sin aceptarlos automáticamente.
- Paquete local de auditoría generado: `urban_cap200_plan_audit_20261123.zip` (plan JSON, seis manifiestos/tareas/splits, validación reconstrucción y comparación caps; sin imágenes/máscaras). La evidencia se comparte en esta conversación. Informe en `docs/INFORME_AUDITORIA_BALANCEO_CAP200.md`.
- No se inició entrenamiento; `RUN_TRAINING=False`. No se modificaron datasets ni se subieron imágenes/máscaras al repo. Mantener PR #3 abierta, draft y sin fusionar.
- Próximo paso: ejecutar el notebook Colab nuevo para confirmar mediante el CLI del repositorio y guardar la evidencia en Drive; después decidir el protocolo baseline completo vs ablaciones cap 500/700. No iniciar entrenamiento hasta decisión explícita.


#### Cierre de auditoría local y notebook reproducible — 2026-11-23

- Se verificó que la recuperación del manifiesto debe restaurar el orden original de `prepare_reproducible_subsets.py` ordenando por `sha256("2026:"+sample_id)`; el notebook incluye esta reconstrucción y valida que val/test conserven identidad y orden exactos.
- Se validó además que los JSONL semánticos y de instancias contienen los mismos IDs y metadatos fuente por ID, aunque el orden de train difiere por selección de tarea. La reconstrucción usa el manifiesto semántico ordenado por hash y cruza las estadísticas por sample_id.
- Paquete de auditoría actualizado: `urban_cap200_plan_audit_20261123.zip`, SHA-256 `88f8dbc26b48837f4adbb64c808a2df1b9b3a7dfb3f3b9eb91137b9c9ed729bf`. Incluye plan, seis manifiestos de train/val/test por tarea, comprobaciones y comparación de caps; no contiene imágenes ni máscaras.
- Notebook `notebooks/colab_generar_plan_cap200.ipynb` quedó reforzado para: verificar digest del artifact, reconstruir seis manifiestos, correr el CLI real del repositorio, comprobar cap<=200, IDs train subset y val/test idénticos en orden, y comparar caps 300/400/500/700/1000. Requiere PAT con Contents: Read-only y Actions: Read-only. Su ejecución real en Colab sigue pendiente; la auditoría local previa reprodujo la función de selección actual con semilla y desempate exactos.
- HEAD auditado antes de esta actualización: `c3934ee824078fc573920a1666f107b6716a6b88`; PR #3 `open/draft/unmerged`. Mantener PR así y `RUN_TRAINING=False`.


#### Corrección de error 403 al descargar artifact desde Colab — 2026-11-23

- El usuario reportó `HTTPError: 403 Client Error: Forbidden` en el GET `/repos/{owner}/{repo}/actions/artifacts/14770171764`, en la celda de descarga. Esto sucede antes de comprobar expiración, digest o extraer ZIP; por tanto, no indica corrupción del artifact. La causa más probable es que el PAT usado en Colab no tiene permiso `Actions: Read-only` sobre este repositorio privado, o que el token no está limitado al repositorio correcto. No se puede afirmar la causa definitiva sin respuesta de diagnóstico del token.
- Se corrigió `notebooks/colab_generar_plan_cap200.ipynb` (commit `8b36bacade367de7a064330e2cb7cd02d4f1944b`): la celda ahora valida por separado autenticación (`GET /user`), acceso al repo (`GET /repos/{repo}`) y acceso al artifact. Ante 403 muestra un error accionable con el encabezado `X-Accepted-GitHub-Permissions` y explica configurar Fine-grained PAT con Resource owner correcto, seleccionar solo este repositorio, `Actions: Read-only` y `Contents: Read-only`; guardar/reemplazar el secreto Colab `GITHUB_TOKEN`. No imprime el token.
- La celda mantiene validación de artifact/run y SHA-256 antes de extraer. El usuario debe reemplazar el secreto por el PAT correcto y volver a ejecutar la celda 3. No necesita regenerar artifact, reindexar ni descargar datasets.
- Estado de Actions auditado: últimos runs continúan con fallos; no se lanzaron reruns. PR #3 sigue abierta, draft y sin merge. No se ha iniciado entrenamiento; `RUN_TRAINING=False`.


#### Corrección de SyntaxError en la reconstrucción de manifiestos del notebook cap200 — 2026-11-23

- El usuario reportó un SyntaxError: unexpected character after line continuation character al ejecutar la sección 4 del notebook notebooks/colab_generar_plan_cap200.ipynb, en la línea que ordena el manifiesto base por SHA-256.
- Causa confirmada al inspeccionar el código publicado: la f-string contenía comillas escapadas literalmente (f\\"2026:...\\":) en lugar de comillas Python normales. No era un error del PAT, del artifact ni de los datos.
- Corrección aplicada directamente en la celda de reconstrucción: base.sort(key=lambda row: hashlib.sha256(f"2026:{row['sample_id']}".encode('utf-8')).hexdigest()).
- Notebook corregido y guardado en la rama urban-models-and-benchmark, commit bf61bd84630256f7cb73fde099f87eb5f26dc3b1. La sección 4 ya no contiene los escapes defectuosos.
- Auditoría al iniciar esta intervención: HEAD 7e1c8dc52374302dd18529a56ac6f4d9b35b6356; PR #3 open/draft/unmerged. Los seis Actions más recientes seguían en failure; el job más reciente consultado (45213945386) figura como completado con failure. No se lanzaron reruns. La corrección del notebook no implica que Actions se hayan recuperado.
- Próximo paso: volver a abrir/recargar el notebook actualizado desde Colab y ejecutar nuevamente la sección 4 (celda de código posterior al encabezado “4. Reconstruir…”). Si Colab conserva una copia antigua, recargar el notebook desde GitHub. Si el runtime perdió las variables ART, extract u otras variables previas, ejecutar las celdas desde el inicio en orden.
- No se ha ejecutado todavía la celda corregida en Colab ni el CLI cap200; la validación real queda pendiente. No se inició entrenamiento; RUN_TRAINING=False. Mantener PR #3 abierta, draft y sin fusionar.


#### Ejecución completada del notebook cap200 en Colab — 2026-11-23

- El usuario confirmó que el notebook `notebooks/colab_generar_plan_cap200.ipynb` llegó al último bloque y compartió la salida: ZIP `/content/drive/MyDrive/ProcesamientoImagenes/balanceo_cap200/plan_balanceado_cap200.zip` (1.081.313 bytes) y resumen `/content/drive/MyDrive/ProcesamientoImagenes/balanceo_cap200/audit_summary.json`.
- El bloque final imprimió explícitamente `RUN_TRAINING sigue False; no se inició entrenamiento.` Esto confirma que no se lanzó entrenamiento y que el empaquetado/copia a Drive terminó. La salida por sí sola todavía no permite validar los conteos de selección, cap, cobertura de clases, sensibilidad ni preservación de val/test; falta revisar el contenido de `audit_summary.json`.
- Próximo paso: solicitar al usuario que abra `audit_summary.json` desde Google Drive y comparta su contenido completo (o descargue/adjunte el JSON/ZIP). No pedir el PAT ni datasets. Tras revisar, contrastar resultados reales del CLI con la auditoría local anterior y emitir dictamen sobre cap200 y alternativas.
- Auditoría GitHub al registrar: HEAD de `urban-models-and-benchmark` `489df6aca8dd38b224339af226978b0e64a1a885`; PR #3 sigue `open`, `draft=true`, `merged=false`. Los seis Actions más recientes consultados continúan en `failure`; no se lanzaron reruns. La ejecución de Colab es evidencia independiente y no cambia ese estado de CI.
- No iniciar entrenamiento hasta revisar el JSON y decidir el protocolo. Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.


#### Auditoría cap200 confirmada por ejecución real del CLI en Colab — 2026-11-23

- El usuario compartió el contenido completo de `audit_summary.json` del notebook `notebooks/colab_generar_plan_cap200.ipynb`. El resumen identifica el HEAD ejecutado como `7e1c8dc52374302dd18529a56ac6f4d9b35b6356`, commit existente en el repositorio.
- El artifact `14770171764` y su SHA-256 `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5` coinciden con la auditoría previa.
- Confirmada la ejecución del CLI real para `per_class_cap=200`: A2D2 semántica 206/1000 (20,6 %), A2D2 instancias 257/1000 (25,7 %), UrbanSyn semántica 200/1000 (20,0 %) y UrbanSyn instancias 209/1000 (20,9 %). Los resultados coinciden con la reproducción local.
- Val/test permanecen completos: A2D2 1000/1000 por split/tarea; UrbanSyn val 751/751 y test 783/783 por tarea. No se aplicó cap a estos splits.
- Cobertura: A2D2 tiene 12 clases semánticas y 4 clases de instancias no disponibles en el índice; UrbanSyn cubre 19/19 clases semánticas y 8/8 clases de instancias. Elevar el cap no corrige las clases ausentes en A2D2.
- Sensibilidad confirmada por el notebook: cap 300 retiene 30–35,7 %; cap 400 retiene 40–45,7 %; cap 500 retiene 50–55,7 %; cap 700 retiene 70–75,7 % según dataset/tarea. Cap 1000 conserva 93,9–100 %. La tabla detallada está en `docs/INFORME_AUDITORIA_BALANCEO_CAP200.md`.
- Importante: `per_class_cap` limita el número de muestras que contienen cada clase, no el total de imágenes seleccionadas; por eso los totales de A2D2 pueden ser mayores que 200 sin violar el cap individual por clase.
- Dictamen: cap200 no se aprueba como train principal; queda como ablación. Baseline recomendado: train completo por dataset, pesos semánticos calculados solo con train y sampler ponderado para instancias. Caps 500/700 pueden compararse como ablaciones, no adoptarse sin evaluación.
- El resumen confirma `training_started=false` y `datasets_downloaded=false`. No se inició entrenamiento ni se descargaron datasets.
- Se actualizó el informe técnico en commit `74085f6aa45a2006117934a2851e6cd717465e13`.
- Auditoría GitHub de esta intervención: HEAD de `urban-models-and-benchmark` `a5526715dd4524513425dd82ff25b3128afbfd83`; el HEAD registrado por el notebook (`7e1c8dc...`) es un commit anterior válido. PR #3 sigue `open`, `draft=true`, `merged=false`. Los seis Actions más recientes consultados (runs `45221858110`, `45221842622`, `45221842530`, `45219425817`, `45219409383`, `45219409350`) terminan en failure. No se lanzaron reruns.
- Próximo paso: fijar el protocolo baseline completo vs ablaciones y revisar el cargador de datos para confirmar que los pesos/sampler se aplican independientemente por dataset y solo con estadísticas de train. No iniciar entrenamiento hasta validarlo y recibir decisión expresa.
- Mantener `RUN_TRAINING=False`, PR #3 abierta, draft y sin fusionar.

#### Integración de loaders de entrenamiento independientes por dataset — 2026-11-23

- Se revisaron `src/urban_training.py`, `src/class_balancing.py`, `src/urban_ontology.py`, `configs/urban_ontology_v1.json`, `tests/test_urban_training_loader.py` y el protocolo documentado. El loader original ya calculaba estadísticas únicamente con las filas que recibía y rechazaba filas marcadas como val/test; sin embargo, la separación por dominio dependía de que el llamador invocara el helper por separado y no existía un orquestador explícito para evitar concatenaciones accidentales.
- Se añadió `build_urban_train_loaders(dataset_specs, ...)` en `src/urban_training.py`. Cada dominio requiere su propio objeto Dataset, sus propias filas de anotaciones y su propio `class_to_id`; la función llama internamente al loader unitario para cada dominio y devuelve loaders separados. Nunca suma píxeles ni frecuencias de A2D2 con UrbanSyn.
- Se añadieron validaciones: no reutilizar el mismo objeto Dataset para dos dominios; detectar etiquetas de dataset ajenas en manifiestos/filas cuando están disponibles; exigir que las filas sean una secuencia y que `class_to_id` sea un mapping. Se mantienen las comprobaciones unitarias de `sample_id` único/no vacío, orden exacto, longitud, split train cuando está declarado y `annotation_status=ok`.
- Se añadieron tres pruebas a `tests/test_urban_training_loader.py`: pesos semánticos opuestos por dominio deben ser diferentes; samplers de instancias deben usar frecuencias locales; y se rechazan filas etiquetadas con otro dominio o la reutilización del mismo Dataset. El archivo ahora contiene 8 pruebas para este loader.
- Se confirmó en la ontología que semántica usa IDs 0–19 (lane marking ID 19; ignore 255) e instancias usa IDs 1–8 (background 0). Por tanto, el llamador debe usar `semantic_name_to_id(ontology)` para semántica y `instance_name_to_id(ontology)` para instancias, suministrados por separado en cada especificación de dominio.
- Se actualizó `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md` con el contrato de la nueva API, un ejemplo y la limitación de que las filas deben venir del archivo `{dataset}_train.annotations.jsonl`; los índices actuales separan splits por archivo y no necesariamente incluyen el campo `split` en cada fila.
- Commits de implementación/pruebas/documentación: `29002ffdd38d43687ead225ca8201964306cfa5d`, `a7f4c5d8b2b87aba5d32dc16ce32b2dd5723474e`, `a25520f0565993c56e9472d7d82faf5130557516`, `5a590f80781ba4519155667d9607f769e401330e`.
- No se han materializado datasets ni iniciado entrenamiento. `RUN_TRAINING=False).
- CI: el workflow Python tests para el HEAD nuevo está en cola al momento de esta anotación; los intentos anteriores siguen fallando con `runner_id=0`, `runner_name=""` y `steps=[]`, por lo que no se puede certificar la ejecución de las pruebas en GitHub Actions. La suite deberá ejecutarse en Colab con el notebook de validación actualizado, que ya incluye `tests/test_urban_training_loader.py` en las pruebas dirigidas.
- Estado al inicio: HEAD `5b0365220717005dc33359cc989a8cb562bed35f`; PR #3 `open/draft/unmerged). Mantener PR #3 así y no fusionar. Próximo paso: ejecutar pruebas dirigidas y suite completa en Colab con el nuevo HEAD; si pasan, revisar la materialización/rutas de los manifiestos locales antes de habilitar cualquier entrenamiento.

- **Actualización de CI tras el commit de registro:** los runs Python `45222675506` y BDD probe `45222675580` terminaron en failure inmediato; ambos jobs reportan `runner_id=0`, `runner_name=""` y `steps=[]`. Es un fallo de asignación/arranque de runner, no un resultado de pytest. No se lanzaron reruns. La ejecución de las 8 pruebas del loader queda pendiente de Colab.



#### Suite completa validada en Google Colab para el loader multidataset — 2026-11-23

- El usuario ejecutó en Google Colab Free el notebook de validación completa sobre la rama `urban-models-and-benchmark`, HEAD exacto `c6b1c29b757b88a289e3583693001510d642c904`.
- La prueba dirigida del balanceador terminó con **1 passed in 0.02s**, código de salida 0. La suite completa terminó con **79 passed in 30.39s**, código de salida 0. El resumen aportado por Colab confirma `passed=true`.
- Evidencia persistida por el usuario en Drive: `MyDrive/ProcesamientoImagenes/validacion_colab/prueba_balanceador_20261123_170118.log` y `suite_completa_20261123_170118.log`. Resumen JSON con timestamp `2026-11-23T17:01:56.264497+00:00`, `git_head=c6b1c29b757b88a289e3583693001510d642c904`, `focused_test_exit_code=0`, `full_suite_exit_code=0`, `training_started=false`, `datasets_downloaded=false`.
- Esta ejecución valida en Colab los cambios recientes de `build_urban_train_loaders`, los pesos semánticos y samplers independientes por dominio y el resto de la suite. Es validación automatizada de código; no constituye entrenamiento ni evaluación de modelos con datos reales.
- Auditoría GitHub al recibir el resultado: HEAD de la rama sigue siendo `c6b1c29b757b88a289e3583693001510d642c904`. PR #3 continúa `open`, `draft=true`, `merged=false`.
- CI de GitHub Actions para ese mismo HEAD continúa fallando antes de ejecutar pasos: Python run `45222727246`, job `pytest`, y BDD probe run `45222714429`, job `probe`; ambos devuelven `runner_id=0`, `runner_name=""` y `steps=[]`. Esto indica que Actions no asignó runner y no es un resultado de pytest. La validación exitosa de Colab es independiente y sí ejecutó las 79 pruebas. No se lanzaron nuevos reruns.
- No se descargaron datasets ni se inició entrenamiento. Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.
- Próximo paso: avanzar a la revisión de integración de manifiestos/rutas y configuración de ejecución por dataset antes de habilitar entrenamiento. Primero resolver la infraestructura de ejecución/persistencia remota; no activar entrenamiento automáticamente a partir del éxito de pytest.


#### Preparación del smoke test de integración real de loaders multidataset — 2026-11-23

- Se revisaron los manifiestos remotos, el índice de anotaciones, los adaptadores, la ontología, el helper build_urban_train_loaders y el notebook cap200. El contrato de loaders exige que Dataset.records y annotation_rows conserven la misma secuencia de sample_id; el índice remoto entrega archivos separados por dataset/split y las filas no siempre incluyen split/dataset, por lo que el smoke test añade esas etiquetas únicamente a la fila train seleccionada.
- Hallazgo corregido: scripts/smoke_test_real_manifest_loaders.py usaba mapas UrbanSyn manuales incompatibles con la ontología urban-v1 (IDs semánticos desplazados) y mapas A2D2 heredados. Se cambió para obtener semantic/instance mappings desde src.urban_ontology y añadir sample_id/dataset a records.
- Se añadió scripts/smoke_test_urban_training_integration.py. Selecciona determinísticamente una fila train por dataset que tenga estadísticas semánticas y de instancias; descarga solo RGB y las máscaras necesarias de esas dos muestras a almacenamiento temporal; construye A2D2/UrbanSyn semantic e instance datasets con mapas de la ontología; ejecuta build_urban_train_loaders separadamente para semántica e instancias; comprueba shapes, pesos semánticos, WeightedRandomSampler, labels, boxes y masks. No ejecuta un modelo, no calcula métricas de calidad, no descarga datasets completos y no entrena.
- Se añadió la sección 9 al notebook notebooks/colab_generar_plan_cap200.ipynb. Reutiliza MANIFEST_DIR e INDEX_DIR creados/verificados por las secciones anteriores y guarda el informe en MyDrive/ProcesamientoImagenes/balanceo_cap200/urban_loader_integration.json. Se validó que el notebook sigue siendo JSON válido (nbformat 4, 18 celdas).
- Se amplió docs/PLAN_BALANCEO_Y_ONTOLOGIA.md con el protocolo, alcance y comando reproducible. Commits de esta intervención: script nuevo `48b13dd64404effec6bbc15f6e3d476673b1032d`; corrección de selección de muestras `c6c2ab662ea452676b8192cb32b1dd216b7694f2` y manejo del mensaje de error `9ec9dabab8a3295d6a4a7ea76601b99fe0986de4`; smoke test anterior corregido `3ab208f6432d656e777c6aa8ffc483475b149ba6`; notebook actualizado `31eac2590057d8723a9729bc0a6584390915ff0f`; documentación `e31042f840ce40940291adab618313edd019ed3d`.
- No se ha ejecutado aún el smoke test con datos reales. La validación automatizada sintética de 79 pruebas del HEAD previo sigue siendo evidencia de código, no sustituye esta nueva prueba. El usuario debe ejecutar las secciones 1–7 y después la nueva sección 9 del notebook; se requiere acceso remoto a A2D2 S3 y UrbanSyn HF para dos muestras. Si la sección 9 falla, no iniciar entrenamiento y compartir la traza/informe.
- Auditoría tras los cambios: HEAD de la rama `e31042f840ce40940291adab618313edd019ed3d`; PR #3 continúa `open`, `draft=true`, `merged=false`. Los runs Python `45224475611` y `45224459568` fallan antes de los steps con `runner_id=0`, `runner_name=""`, `steps=[]`; no se consideran resultados de pytest. No se lanzaron reruns.
- No se ha descargado el dataset completo ni iniciado entrenamiento. Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.
- Próximo paso: ejecutar la nueva sección 9 en Colab y revisar el JSON resultante. Solo si pasa, avanzar a un smoke test de forward del modelo con esas muestras; no habilitar entrenamiento todavía.

- **Auditoría final después de guardar este registro:** el commit que contiene la documentación de esta intervención es `f923a191dce01408cb9ae698e12a4e6e75983685`, y la rama/PR #3 apuntan a ese mismo HEAD. PR #3 permanece `open`, `draft=true`, `merged=false`. El run Python más reciente `45224570271` también terminó antes de ejecutar steps (`runner_id=0`, `runner_name=""`, `steps=[]`); no es un resultado de pytest. No se lanzaron reruns.


## Incidencia del smoke test real y mejora de diagnóstico — 2026-11-23

El usuario ejecutó la sección 9 desde Colab y recibió `subprocess.CalledProcessError` con código de salida 1. El traceback compartido solo identifica el fallo del proceso hijo; no contiene stdout/stderr del script, por lo que **la causa raíz sigue sin determinarse**. El `audit_summary.json` aportado corresponde a la auditoría cap200 y no diagnostica el smoke test.

Se inspeccionaron el script `scripts/smoke_test_urban_training_integration.py`, los adaptadores de `src/data_adapters.py` y el helper `src/urban_training.py`. La ruta de A2D2 sí usa el campo `instance` esperado por `A2D2InstanceDataset`; no se encontró evidencia suficiente para atribuir el fallo a una línea concreta. No se debe adivinar la causa.

Se modificó la celda 9 del notebook para ejecutar el script con salida sin búfer, capturar y mostrar stdout/stderr completos incluso cuando el proceso falle, y persistir ambos logs en Drive:
- `MyDrive/ProcesamientoImagenes/balanceo_cap200/urban_loader_integration.stdout.log`
- `MyDrive/ProcesamientoImagenes/balanceo_cap200/urban_loader_integration.stderr.log`
En la siguiente ejecución, el traceback completo debe aparecer en la salida de la celda; si vuelve a fallar, compartir ambos logs o pegar el contenido de stderr. No se alteró el script de integración ni se declaró PASS. La integración con muestras reales continúa pendiente.

Se revisó PR #3: sigue abierta; el estado draft/no fusionada se mantiene como requisito. En Actions, el run Python `45224667061` terminó en failure, pero la consulta de jobs no expuso pasos/logs (steps=null), así que no permite inferir si falló por código o por runner. No se lanzó ningún rerun.

No se descargaron datasets completos ni se inició entrenamiento; `RUN_TRAINING=False` permanece obligatorio.

#### Diagnóstico de fallo del smoke test real y mejora de captura de errores — 2026-11-23

- El usuario ejecutó la sección 9 del notebook sobre el HEAD indicado por el informe cap200 (4be648758067ea1514ca15eacede618617b33d07). La celda terminó con CalledProcessError, código de salida 1. La salida compartida solo incluye el traceback de Python exterior; no contiene stdout/stderr del script, por lo que no permite identificar aún si falló la lectura de manifiestos, descarga S3/Hugging Face, decodificación de etiquetas o construcción/validación de loaders.
- El audit_summary.json aportado corresponde a la auditoría cap200, no al smoke test de integración. Confirma training_started=false y datasets_downloaded=false; no prueba que el smoke test haya pasado.
- Se revisó scripts/smoke_test_urban_training_integration.py y la celda 9. El notebook ejecutaba subprocess.run(..., check=True) sin capturar ni mostrar stderr, ocultando el mensaje útil del proceso hijo en el output compartido. No se modificó aún la lógica del smoke test ni se atribuyó una causa no demostrada.
- Se actualizó la sección 9 de notebooks/colab_generar_plan_cap200.ipynb: ahora elimina un informe anterior para evitar falsos positivos, captura e imprime stdout/stderr, y presenta el código de salida real. Si el proceso falla, levanta un error claro después de imprimir el diagnóstico. La prueba sigue acotada a una muestra por dataset y no inicia entrenamiento.
- Commit de notebook: faf3e8188b51da61c1043bc2f9400e47124437a3.
- Próximo paso: actualizar el notebook desde la rama urban-models-and-benchmark, ejecutar de nuevo las secciones requeridas 1–7 si la sesión/rutas ya no existen y luego la sección 9. Compartir la sección ERROR REAL (stderr) completa y cualquier salida previa del script. Con ese mensaje se corregirá la causa raíz, no por conjetura.
- La auditoría cap200 sigue concluyendo que cap200 no debe ser el train principal: A2D2 conserva 206/1000 semántica y 257/1000 instancias; UrbanSyn 200/1000 y 209/1000, respectivamente. A2D2 mantiene 12 clases semánticas y 4 de instancias no disponibles en el índice; UrbanSyn cubre 19/19 y 8/8. Val/test se conservaron completos. No se inició entrenamiento ni se descargaron datasets completos.
- No se ejecutaron reruns de Actions. La consulta de workflow runs asociada al commit más reciente no devolvió ejecuciones PR; no se usa eso como evidencia de éxito o fallo de CI. El registro anterior mantiene PR #3 abierta, draft y sin fusionar; no se realizó ninguna acción de merge ni cambio de estado. Mantener RUN_TRAINING=False.

#### Dependencia faltante en Colab: boto3 — 2026-11-23

- El usuario ejecutó la sección 9 y el stderr identificó la causa inmediata: ModuleNotFoundError: No module named 'boto3' al importar en scripts/smoke_test_urban_training_integration.py. No es un fallo de loaders ni de anotaciones; el proceso se detuvo antes de leer muestras o acceder a A2D2/UrbanSyn.
- Se actualizó la sección 9 de notebooks/colab_generar_plan_cap200.ipynb para detectar dependencias ausentes e instalar solo las faltantes (`boto3` y/o `huggingface_hub`) con el mismo intérprete Python de Colab antes de lanzar el script. boto3 instala sus dependencias botocore automáticamente. La ejecución del script usa `-u` para que la salida sea inmediata; la captura stdout/stderr y validación del JSON se conservan.
- Commit del notebook: a696604de73a08e2ef25220a1733d72f4432f244.
- La sección 9 debe reintentarse desde la rama urban-models-and-benchmark. Si pip falla, compartir su error; si la prueba avanza y aparece otro traceback, compartir el nuevo stderr. No editar ni instalar paquetes manualmente en el teléfono; todo se ejecuta dentro del entorno Colab.
- Este error no demuestra que el smoke test haya pasado ni que haya fallado la integración de datos: no llegó a ejecutarse más allá de imports. No se inició entrenamiento ni se descargaron datasets completos; RUN_TRAINING=False.
- Se consultó el estado de Actions para el commit anterior y se encontró un run Python con failure; esta comprobación no se usa como resultado del smoke test local de Colab. No se lanzaron reruns. Mantener PR #3 abierta, draft y sin fusionar.


#### Corrección de importación del paquete src en el smoke test de Colab — 2026-11-23

- El usuario volvió a ejecutar la sección 9 después de la instalación automática de dependencias. `boto3` se instaló y el proceso avanzó hasta importar `src.data_adapters`, donde falló con `ModuleNotFoundError: No module named 'src'`.
- Causa raíz confirmada por el modo de lanzamiento: la celda ejecutaba el archivo por ruta (`python scripts/smoke_test_urban_training_integration.py`). En ese modo, Python pone `scripts/` como primera ruta de módulos y no garantiza que la raíz del repositorio esté en `sys.path`, aunque `cwd=WORKDIR`.
- Corrección aplicada a la sección 9: ejecutar el mismo script como módulo (`python -m scripts.smoke_test_urban_training_integration`) desde `WORKDIR`. Esto hace que la raíz del repositorio esté en la ruta de importación y permite resolver `src` sin modificar el código de los adaptadores ni instalar un paquete ficticio. Se mantienen captura de stdout/stderr, dependencias automáticas, borrado de informe previo y validación explícita de `status=PASS` / `training_started=false`.
- Commit del notebook: `ff7af24be7e843b3c2a4baa7f9491c4421f7835d`.
- El smoke test todavía no ha pasado: el nuevo comando debe ejecutarse en Colab y cualquier error posterior se diagnosticará con su stderr real. La prueba sigue limitada a una muestra por dataset; no descarga datasets completos, no hace forward de modelos y no entrena.
- Auditoría antes del cambio: HEAD previo `58a83f6bb6f2b64fc67478d41f77c2a0872f2418`; PR #3 confirmada `open`, `draft=true`, `merged=false`. Actions run `45231711166` (Python tests) falló en 2 segundos antes de ejecutar steps, con `runner_id=0`, `runner_name=""`, `steps=[]`; no es un resultado de pytest. No se lanzaron reruns.
- No se descargaron datasets completos ni se inició entrenamiento. Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.


#### Smoke test real de loaders aprobado y siguiente validación de forward — 2026-11-23

- El usuario ejecutó la sección 9 del notebook en Colab y compartió el informe completo. Resultado explícito: `status=PASS`, `RESULT: REAL MULTIDATASET TRAIN-LOADER INTEGRATION PASSED`, `training_started=false`, `full_dataset_downloaded=false`.
- Muestras train usadas:
  - A2D2: `20181108_091945/20181108091945_camera_frontcenter_000006064.png`; manifiesto train de 1.000 filas; `annotation_status=ok`.
  - UrbanSyn: `4696`; manifiesto train de 1.000 filas; `annotation_status=ok`.
- Semántica, ambos datasets: imagen `[1,3,512,512]`, máscara `[1,512,512]`, 20 pesos de clase. IDs observados A2D2 `[10,13,14,19,255]`; UrbanSyn `[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,18,255]`.
- Instancias: A2D2 5 objetos, cajas `[5,4]`, máscaras `[5,512,512]`, labels observadas `[3,4]`; UrbanSyn 20 objetos, cajas `[20,4]`, máscaras `[20,512,512]`, labels `[1,2,3,4]`. El informe confirma uso de los loaders y sampler de instancias en la prueba.
- La advertencia HF Hub fue por solicitudes no autenticadas y límites de tasa potencialmente menores; no invalidó la descarga ni el resultado. El script usó muestras remotas temporales y eliminó el directorio temporal al terminar.
- Alcance: queda validada la integración real de manifiestos, una muestra por dataset, decodificadores, tensores, targets y balanceo/sampler. No se validó todavía ningún forward de modelo, precisión, calidad predictiva ni entrenamiento.

##### Implementación de forward pass real, sin entrenamiento

- Se amplió `scripts/smoke_test_urban_training_integration.py` con opción `--model-forward`: reutiliza los loaders y las mismas muestras deterministas, ejecuta DeepLabV3+ con 20 logits semánticos y Mask R-CNN con 9 salidas de clase (background + 8 clases de instancia), en modo `eval()` y `torch.inference_mode()`.
- Ambos modelos se inicializan sin pesos preentrenados ni checkpoints. Se validan dimensiones y valores finitos de logits/cajas/máscaras. No se llama a `train()`, backward, optimizer, ni escritura de checkpoint; las predicciones no son métricas de calidad y no deben interpretarse como modelo entrenado.
- Se añadió sección 10 a `notebooks/colab_generar_plan_cap200.ipynb`, que vuelve a descargar solo una muestra por dataset y guarda `urban_model_forward_real_samples.json` en Drive. No se descargan datasets completos.
- Commits: script `413b4580aaa274b9d7a574e0b4e11b71bbd5ba88`; notebook `58bb19d1a36e76270600a2ec41a48cc340a2fc5b`.
- La ejecución de sección 10 en Colab queda pendiente. Si falla, compartir stdout/stderr completo; si pasa, inspeccionar el JSON antes de proponer entrenamiento.

##### Auditoría tras los cambios

- HEAD rama: `58bb19d1a36e76270600a2ec41a48cc340a2fc5b`.
- PR #3: `open`, `draft=true`, `merged=false`.
- Actions run más reciente observado: `45234787373`, evento pull_request, status `queued` al consultar. No se lanzó rerun. No se considera CI aprobado.
- La intervención no descargó datasets completos ni inició entrenamiento. Mantener `RUN_TRAINING=False` y PR #3 abierta, draft y sin fusionar.

#### Forward pass de modelos aprobado con muestras reales — 2026-11-23

- El usuario ejecutó la sección 10 de `notebooks/colab_generar_plan_cap200.ipynb` y compartió el JSON completo. Resultado: `status=PASS`, `model_forward.status=PASS`, `training_started=false`, `full_dataset_downloaded=false`.
- Muestras utilizadas: A2D2 `20181108_091945/20181108091945_camera_frontcenter_000006064.png` y UrbanSyn `4696`, una por dataset, ambas del manifiesto train de 1.000 filas y `annotation_status=ok`.
- DeepLabV3+ ejecutó forward para ambos dominios: entrada `[1,3,512,512]`, logits `[1,20,512,512]`, predicción `[1,512,512]`, todos los logits finitos.
- Mask R-CNN ejecutó forward para ambos dominios: entradas `[3,512,512]`; A2D2 tenía 5 instancias GT y UrbanSyn 20. Cada muestra produjo 100 cajas `[100,4]` y máscaras `[100,1,512,512]`; predicciones finitas.
- Ejecución en CPU. Los dos modelos se inicializaron con pesos aleatorios, sin pesos preentrenados ni checkpoints; el modo de prueba no ejecutó backward, optimizador, entrenamiento ni guardado de checkpoints. Por ello el PASS confirma compatibilidad de tensores/modelos y el forward de inferencia, pero **no** calidad de predicciones, capacidad de aprendizaje, estabilidad de loss ni métricas de segmentación/detección.
- Advertencia de Hugging Face: peticiones anónimas con límites de tasa potencialmente menores; no afectó el resultado PASS.
- Informe guardado por el usuario en Drive: `MyDrive/ProcesamientoImagenes/balanceo_cap200/urban_model_forward_real_samples.json`.
- Se consultó el registro antes de la auditoría remota. PR #3 aparece abierta en la búsqueda de GitHub; se conserva el requisito de mantenerla draft y sin merge. La búsqueda de workflows asociada al SHA conocido `e54150d8b72d9a88f67cbf188efc1d9e0547c69b` muestra el run Python `45234862819` completado con failure; su job `pytest` no expone steps/logs (`steps=null`). Los runs `45234853382` y `45234853305` también aparecen failure sin pasos consultables. No se puede determinar con estos metadatos si el fallo es de runner, código u otra causa; **no equivale a un resultado de pytest**. No se lanzaron reruns.
- No se inició entrenamiento ni se descargó el dataset completo. Mantener `RUN_TRAINING=False`.
- Dictamen: quedan aprobados los smoke tests reales de loaders/balanceador y el forward de DeepLabV3+/Mask R-CNN sobre una muestra real de cada dataset. Antes de un experimento de aprendizaje hacen falta una prueba controlada de loss/backward/optimizer y un protocolo de entrenamiento/evaluación por dominio; usar muestras train, mantener val/test intactos y registrar seeds, tiempos, memoria, losses y checkpoints. Esta siguiente prueba requiere autorización expresa del usuario y no debe confundirse con entrenamiento de producción.

#### Preparación de prueba controlada de aprendizaje autorizada — 2026-11-23

- El usuario autorizó expresamente ejecutar una prueba mínima de aprendizaje después de aprobar loaders reales y forward pass. El alcance autorizado es exclusivamente cuatro actualizaciones aisladas: DeepLabV3+ en A2D2, DeepLabV3+ en UrbanSyn, Mask R-CNN en A2D2 y Mask R-CNN en UrbanSyn. No equivale a entrenamiento de producción.
- Se amplió `scripts/smoke_test_urban_training_integration.py` con `--learning-step` y `--learning-rate`. Cada combinación instancia un modelo nuevo, con inicialización aleatoria y sin pesos preentrenados/checkpoints; calcula loss real, ejecuta backward, valida gradientes finitos/no nulos, ejecuta un único SGD y comprueba que los parámetros cambian y permanecen finitos. DeepLabV3+ usa CrossEntropy con pesos semánticos train-only e ignore_index 255; Mask R-CNN utiliza sus losses nativas con cajas/máscaras reales.
- La prueba registra pérdidas, componentes de loss de Mask R-CNN, tensores con gradiente, tiempo por paso, memoria máxima CUDA (si hay GPU) y RSS máximo del proceso. No guarda checkpoints ni ejecuta épocas. Los dominios y modelos son independientes.
- Se añadió sección 11 al notebook `notebooks/colab_generar_plan_cap200.ipynb`: ejecuta el script como módulo con cuatro pasos, tamaño 256×256 para limitar memoria y learning rate 1e-4; persiste JSON y logs stdout/stderr en `MyDrive/ProcesamientoImagenes/balanceo_cap200/`. El informe distingue `training_started=true` (hubo cuatro actualizaciones reales) de `full_training_started=false`; el flujo de entrenamiento general `RUN_TRAINING=False` no se modifica.
- Se documentó el contrato y las limitaciones en `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md`. Commits: script inicial `100af2745fa447a6f95f8b1b2563d2fc3472d657`; sección notebook `62074d2a3d44a4a1d2a013a29e0420871af407b1`; documentación `c03b1cc55de87a680c5421c5c24de1c50a659dcf`; instrumentación de tiempo/memoria `d3fb469dc5e1429ca9404618e2e1e4aa46289997`; verificación de parámetros tras SGD `0b40e8927c5eda73539fd7fe7ed6d13b4c3db7e3`.
- **Ejecución real pendiente:** todavía no se ha ejecutado la sección 11 en Colab; no declarar PASS ni afirmar que las cuatro actualizaciones se completaron. El usuario debe abrir/recargar el notebook desde la rama y ejecutar la sección 11 tras reconstruir variables/rutas mediante secciones 1–7 si es necesario. El tamaño 256 se eligió para limitar memoria; si falla, revisar stdout/stderr antes de cambiar la configuración. No repetir pasos exitosos a menos que se autorice.
- Auditoría al finalizar implementación: HEAD rama y head PR #3 `0b40e8927c5eda73539fd7fe7ed6d13b4c3db7e3`. PR #3 continúa `open`, `draft=true`, `merged=false`. Actions para commits recientes siguen fallando antes de pasos (job `pytest`, `steps=[]`); el run `45238059817` del commit `c03b1cc...` aparece `queued` al consultar. No se puede atribuir causa raíz ni interpretar los fallos como resultados de pytest; no se lanzaron reruns.
- No se descargó el dataset completo ni se inició entrenamiento de producción. La única ejecución de aprendizaje autorizada es la sección 11, acotada a cuatro pasos. PR #3 debe permanecer draft y sin fusionar.


#### Prueba controlada de aprendizaje con datos reales aprobada — 2026-11-23

- El usuario ejecutó la sección 11 de `notebooks/colab_generar_plan_cap200.ipynb` y compartió el JSON completo y los resultados finales. Estado: `status=PASS`, `controlled_learning.status=PASS`, `optimizer_steps_expected=4`, `optimizer_steps_completed=4`; mensajes de salida: `REAL MULTIDATASET TRAIN-LOADER INTEGRATION PASSED` y `CONTROLLED REAL-DATA LEARNING STEPS PASSED (4 optimizer updates)`.
- Muestras train: A2D2 `20181108_091945/20181108091945_camera_frontcenter_000006064.png` (manifiesto 1.000 filas, annotation_status=ok) y UrbanSyn `4696` (manifiesto 1.000 filas, annotation_status=ok). Una muestra por dominio; entradas 256×256.
- DeepLabV3+ A2D2: loss 2.9230999947; 186/186 tensores de gradiente finitos y no nulos; SGD lr=1e-4; `parameter_updated=true`, `finite_parameters_after_step=true`; 3.599 s.
- DeepLabV3+ UrbanSyn: loss 3.0971031189; 186/186 tensores de gradiente finitos y no nulos; SGD lr=1e-4; parámetros actualizados y finitos; 3.195 s.
- Mask R-CNN A2D2: 5 instancias GT; loss total 9.4461917877 (classifier 2.2215030193, box_reg 0.0083871614, mask 5.3099250793, objectness 0.7233833671, rpn_box_reg 1.1829936504); 201/201 tensores de gradiente finitos y no nulos; SGD lr=1e-4; parámetros actualizados y finitos; 5.647 s.
- Mask R-CNN UrbanSyn: 20 instancias GT; loss total 7.1227083206 (classifier 2.2164609432, box_reg 0.1582923532, mask 3.1125996113, objectness 0.7150309086, rpn_box_reg 0.9203243256); 201/201 tensores de gradiente finitos y no nulos; SGD lr=1e-4; parámetros actualizados y finitos; 7.323 s.
- Ejecución en CPU; RSS máximo del proceso 1.042,71 MB; memoria CUDA no aplica. Los cuatro modelos se inicializaron aleatoriamente, sin pesos preentrenados ni checkpoints. No se guardó checkpoint. `training_started=true` refleja correctamente las cuatro actualizaciones controladas; `full_training_started=false` y `full_dataset_downloaded=false`. El forward separado figura `NOT_REQUESTED` en esta ejecución.
- Advertencia de Hugging Face Hub: petición anónima; solo afecta límites de tasa potenciales y no invalida el PASS. El usuario guardó JSON y logs en Drive: `MyDrive/ProcesamientoImagenes/balanceo_cap200/urban_controlled_learning_step.json`, `urban_controlled_learning_step.stdout.log` y `urban_controlled_learning_step.stderr.log`.
- Interpretación: queda validado el ciclo loss → backward → gradientes → una actualización SGD para las cuatro combinaciones sobre las muestras reales indicadas. Esto **no** demuestra convergencia, estabilidad en múltiples iteraciones, generalización, calidad predictiva ni métricas de validación/test. No es entrenamiento de producción. Mantener `RUN_TRAINING=False` hasta diseñar y aprobar un protocolo completo por dominio.
- Auditoría GitHub posterior a la ejecución: HEAD de `urban-models-and-benchmark` sigue en `178bb756bc3a9dbe452b801988906159718903c3`; PR #3 sigue `open`, `draft=true`, `merged=false`, con ese mismo head SHA. Los runs más recientes para ese SHA son 45238126396 (Python tests), 45238112490 (Python tests) y 45238112448 (BDD100K probe); todos concluyeron failure con `runner_id=0`, `runner_name=""` y `steps=[]`. Por tanto no ejecutaron pytest/probe y no constituyen evidencia de fallo del código. No se lanzaron reruns.
- Próximo paso: diseñar, revisar y aprobar el protocolo de entrenamiento experimental completo (iteraciones/épocas, separación por dominio, validación intacta, métricas, checkpoints, límites de tiempo/memoria y reanudación) antes de ejecutarlo. PR #3 permanece draft y sin fusionar.


#### Protocolo experimental multidataset documentado — 2026-11-23

- A petición del usuario se diseñó y añadió `docs/PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md` (versión `urban-exp-v1`). Commits de documentación: protocolo `321b3689fafd731727144ba70f677b0e6e46ac6b`; enlace desde estrategia multidataset `d043b702534136b7d73daec246627a45e8e681d6`; enlace desde plan de balanceo/ontología `175dd6d467f71465c674c7e87ea26c76c05b03df`.
- Matriz propuesta de cuatro experimentos independientes: DeepLabV3+ semántica en A2D2 y UrbanSyn; Mask R-CNN instancias en UrbanSyn (baseline principal) y A2D2 (complementario/ablación por instancias reconstruidas con componentes conectados y cobertura limitada). No mezclar dominios ni estados de optimizer/sampler/estadísticas.
- Train baseline usa todas las filas train válidas (A2D2 1.000; UrbanSyn 1.000); cap200 solo ablación. Val/test permanecen completos (A2D2 1.000/1.000; UrbanSyn 751/783). Pesos semánticos y sampler de instancias se calculan solo con anotaciones train del dominio actual. Ontología `urban-v1`, semántica 20 logits/ignore 255 e instancias 8 clases.
- El protocolo define hiperparámetros iniciales conservadores para T4, piloto de 10 batches como puerta previa, máximo 20 épocas con validación por época, early stopping, métricas semánticas IoU/mIoU y métricas COCO Mask/Box AP, selección de checkpoint por validación, test una sola vez al final, checkpoints atómicos y reanudación con estado de optimizer/scheduler/RNG, logging, semillas, criterios de parada y límites de memoria/tiempo.
- Las cifras de configuración son propuestas por validar, no benchmarks ni garantía de que el runtime tenga recursos. Se exige primero implementar runner/evaluadores/checkpoint restore, validar sobre HEAD exacto y probar materialización completa lógica. La autorización anterior cubrió únicamente cuatro pasos SGD aislados; **no autoriza el piloto de 10 batches ni el entrenamiento completo**.
- Estado explícito del protocolo: propuesta documentada, no autorizada para ejecución. `RUN_TRAINING=False`, no hay épocas ni checkpoints entrenados. Se requiere autorización específica para el piloto y, tras revisar sus resultados, autorización separada para entrenamiento completo.
- Auditoría previa a los cambios de documentación: HEAD era `5ea81a34b99bf9b4a8432cd62bd2fb3335dac15d`; PR #3 `open`, `draft=true`, `merged=false`. Actions recientes de ese SHA (runs 45239753324, 45239745544, 45239745521) fallaron con jobs sin pasos consultables; no se interpretan como pytest ejecutado.


##### Auditoría posterior a la documentación del protocolo — 2026-11-23

- HEAD final de `urban-models-and-benchmark` y head de PR #3: `db262f9bb971c89aacc42a542c1c8c5c15e82adf`.
- PR #3 continúa `open`, `draft=true`, `merged=false`.
- Actions para el HEAD final: runs 45240089901 (pytest) y 45240089856 (probe) aparecen queued al consultar. Runs previos del mismo cambio documental 45240076012 y 45240051463 terminaron failure con `runner_id=0`, `runner_name=""`, `steps=[]`; no se ejecutó pytest/probe. No se lanzaron reruns.
- No se cambió `RUN_TRAINING`, no se implementó ni ejecutó el runner experimental, no se iniciaron épocas ni se generaron checkpoints. El protocolo sigue siendo propuesta pendiente de revisión y autorización.


#### Diseño del protocolo de entrenamiento experimental multidominio — 2026-11-23

- A petición del usuario se diseñó y añadió `docs/PROTOCOLO_ENTRENAMIENTO_MULTIDOMINIO.md`. Es una especificación de ejecución por fases, no un entrenamiento ni un runner implementado.
- Matriz: cuatro experimentos independientes (DeepLabV3+ semántica A2D2; DeepLabV3+ semántica UrbanSyn; Mask R-CNN instancias UrbanSyn; Mask R-CNN instancias A2D2 exploratorio). No se concatenan dominios ni estadísticas. A2D2 queda restringido por clases ausentes y por instancias reconstruidas con componentes conectados; UrbanSyn es la fuente primaria para las ocho clases de instancia. SHIFT continúa excluido por desalineación PTS.
- El protocolo bloquea test hasta la evaluación final, usa train para pesos/sampler, validation para selección/early stopping y conserva separación por secuencia A2D2 y por sample ID UrbanSyn (sin afirmar independencia temporal no verificada). Cap200 no es baseline; se propone train completo y caps solo como ablaciones.
- Se especificó preflight obligatorio (CI sobre SHA exacto o suite Colab si Actions no asigna runner, integridad/hash de manifests/índices, loaders train/val, cobertura por clase, licencias, GPU/almacenamiento persistente, prueba de checkpoint/reanudación y configuración inmutable).
- Piloto propuesto, no ejecutado: seed 2026, máximo 5 épocas, validación por época, early stopping paciencia 2, job máximo 90 min, batch ajustado por prueba de memoria, objetivo 512×512 (reducir solo con evidencia), AMP solo si validado. Los learning rates y pesos iniciales deben fijarse en config después de inspeccionar arquitectura/entorno; el LR 1e-4 del smoke test no se extrapola.
- Se definieron métricas: semántica mIoU macro sobre clases con soporte + IoU/soporte por clase; instancias Box AP y Mask AP COCOeval solo si el evaluador queda validado (si no, reportar únicamente métricas internas correctamente nombradas); benchmark de latencia separado. Checkpoints last/best atómicos con optimizer/scheduler/scaler/RNG, hashes, logs y reanudación.
- Confirmatorio futuro: tres seeds 2026/2027/2028 tras revisar el piloto y aprobar presupuesto; evaluación test una vez por seed. No se autoriza automáticamente al terminar el piloto.
- Actualizado enlace desde `docs/PLAN_BALANCEO_Y_ONTOLOGIA.md`. Commits de documentación: protocolo `e5011b27e7185fe76c1c1df88b7de5432c2c169d`; enlace en plan `051bd6ac5b23c4aec3c39410128c0a9abcb9c1bf`.
- No se modificó código de entrenamiento ni notebook, no se inició entrenamiento, no se descargaron datasets completos, no se creó infraestructura de pago y `RUN_TRAINING=False` permanece. Antes de ejecutar hay que implementar/revisar runner reproducible, validar Mask AP, comprobar entorno GPU/almacenamiento y recibir autorización expresa para el piloto.
- Auditoría previa a la documentación: HEAD al iniciar esta intervención `321b3689fafd731727144ba70f677b0e6e46ac6b`; PR #3 `open`, `draft=true`, `merged=false`. Actions: el run Python `45240038830` del SHA inicial estaba queued; los runs previos del SHA `5ea81a34...` habían fallado. El detalle runner/steps debe consultarse tras el commit final; no lanzar reruns.
- Mantener PR #3 abierta, draft y sin fusionar.

- Auditoría final tras guardar el protocolo y el registro: HEAD rama y head PR #3 = `9983139ff7b81e8fd5be60449b59682192a946f2`; PR #3 sigue `open`, `draft=true`, `merged=false`. Actions para ese SHA: `45240218424` (pytest) queued al consultar; `45240208235` (pytest) y `45240208141` (probe) failure. La consulta de jobs devuelve `steps=null`, sin logs de ejecución disponibles; por ello no se atribuye el fallo a código ni se afirma que pytest/probe se ejecutaran. No se lanzaron reruns.


## Implementación parcial del ejecutor multidominio — 2026-11-23

- Se consultó primero este registro. HEAD observado al iniciar la intervención: `636b60d7d9aefa55f401e1df04866308917cdfbc`; PR #3 localizada en GitHub y se conserva la instrucción de mantenerla abierta/draft/sin merge. No se modificó su estado.
- Se inspeccionaron `src/urban_training.py`, adaptadores de datos, script de smoke test, ontología, notebook de manifiestos y protocolo. El estado real mostró que los loaders de train ya existen, pero el notebook materializa únicamente muestras del smoke test; no existe aún una factory que construya train/validation completos desde los manifiestos remotos.
- Se añadieron:
  - `src/urban_experiment_runner.py`: motor reutilizable de entrenamiento por experimento, validación semántica (mIoU/IoU por clase/soporte/matriz de confusión), scheduler, early stopping, límite temporal por época, AMP opcional solo CUDA, clipping opcional, métricas JSONL, checkpoints atómicos last/best y restauración de optimizer/scheduler/scaler/RNG. La reanudación valida el hash de configuración.
  - `scripts/run_urban_experiment.py`: CLI que requiere `run_training=true` y `--execute`, y consume una factory Python con loaders separados train/validation. No recibe test.
  - `tests/test_urban_experiment_runner.py`: cuatro pruebas sintéticas para métricas/ignore 255, loop y checkpoints, hash de reanudación y bloqueo de Mask AP sin evaluador.
  - `docs/EJECUTOR_ENTRENAMIENTO_MULTIDOMINIO.md`: contrato y bloqueos pendientes.
- Se amplió `docs/PROTOCOLO_ENTRENAMIENTO_MULTIDOMINIO.md` con el estado parcial y las puertas pendientes.
- Commits de archivos nuevos: motor `a1299c5d240f16632a48784444f4953b1cc1ba21`; CLI `d6fa2dffaa49ff6febf28ab1996a55e191d7c889`; tests `fb1ff27b4dd48b998169247f73e16eff72fd5965`; guía `adcf7fb54cc9990ab8459d317788c94faf1ba45b`. Actualización del protocolo: `1cc7a94cd87406f055146556a1549283b61ff098`.
- **Limitaciones no resueltas:** no se implementó todavía la factory/materializador remoto de los manifests completos para A2D2/UrbanSyn ni el evaluador COCO de Box AP/Mask AP. El runner bloquea correctamente la tarea de instancias si no se suministra un evaluador que devuelva `mask_ap` numérico finito; no se falseará Mask AP con AP de cajas. No se ha validado el motor contra loaders reales de train/validation, checkpoint/resume en esos loaders ni GPU.
- **Pruebas:** se añadieron tests sintéticos, pero no se ejecutaron en esta intervención. La CI del repo ya había mostrado para el commit previo `636b60d7...` el run `45240266965` con job `pytest` en failure, `steps=null` y sin logs; ese metadato no permite atribuir la causa ni demuestra que pytest llegara a ejecutarse. No se lanzaron reruns. Tampoco se afirma que CI haya probado los commits nuevos.
- No se inició entrenamiento, no se descargaron datasets completos, no se generaron checkpoints experimentales y no se cambió el notebook ni `RUN_TRAINING=False`. La autorización previa solo cubrió cuatro pasos SGD aislados ya realizados; no autoriza el piloto. La siguiente fase es implementar y validar la factory real y el evaluador COCO, luego ejecutar suite en Colab sobre SHA exacto y comprobar checkpoint/resume. Solo después pedir autorización explícita para el piloto.
- PR #3 debe seguir abierta, draft y sin fusionar.


- Ajuste final del motor: se incorporó también `mean_accuracy` semántica, además de pixel accuracy e IoU por clase; commit `c05200ed1d6ae69aa2219aebbf7ea7ed2c307fab`. Enlace de protocolo actualizado: `a1b517452d390ee7c860663cb830e3562879b080`.
- Auditoría de la rama al cerrar: último commit creado por esta intervención en `urban-models-and-benchmark`: `a1b517452d390ee7c860663cb830e3562879b080` (el registro se actualiza a continuación). La búsqueda confirma PR #3 abierta; su descripción conserva el estado “Draft intencional”. No se solicitó ni ejecutó conversión a ready ni merge. La consulta de runs asociados a los commits de implementación no devolvió ejecuciones PR disponibles; no se afirma que la suite se haya ejecutado ni aprobado. No se lanzaron reruns.
- Estado final: motor parcial y CLI guardada; suite sintética añadida pero pendiente de ejecución sobre SHA exacto; factory/materializador de datos y COCO Mask AP pendientes; `RUN_TRAINING=False`; sin entrenamiento ni descarga completa.


### Ampliación a pipeline de materialización, factory y evaluación COCO — 2026-11-23

Tras el primer motor se completaron componentes adicionales:

- `scripts/materialize_urban_experiment_data.py`: materialización remota de train/validation de A2D2 (S3 oficial) y UrbanSyn (HF, revision de cada fila). Verifica sample IDs únicos/no vacíos, igualdad de IDs manifiesto/índice y `annotation_status=ok`; no toca test. Commit inicial `5b44f53bb8a4a2c5b9edf6a3ea7b29e3d91b746b`, validación de IDs vacíos `b558d1032a68400b43c6e669db094f4e1fdcbb18`.
- `scripts/urban_experiment_factory.py`: crea datasets/loader de train y validation por dominio y tarea, comprueba no solapamiento de IDs, utiliza los pesos/sampler train-only existentes, instancia DeepLabV3+ o Mask R-CNN y SGD + ReduceLROnPlateau. Corrige la normalización del campo RGB UrbanSyn y el mapeo de categorías COCO. Commit inicial `bc55250e6388eeef7cdbdba325f86fbe18dabcae`, corrección `709b241d1d1e6c6786cb9712d1d35499600e743e`.
- `src/urban_coco_evaluator.py`: Box AP y Mask AP mediante `pycocotools.COCOeval`, AP@[.50:.95], AP50/AP75 y soporte/AP por clase. Rechaza validación sin GT. Se conserva RLE binario para el uso in-memory de COCOeval. Commits `84f187b940fc1705f795d5d2d5eef198dc4585f5`, `d7255cf5dba5668b5598f0778be8c94fa6bd6995`, `a01e7f4de436fd037c1eb875825bb63d9f1b67c1`.
- `tests/test_urban_coco_evaluator.py`: prueba sintética de Mask AP/Box AP perfecta; hace skip si pycocotools no está instalado. Commit `f436e4bc1b4dc013b8c997bea153e48d2d508149`.
- Guía de ejecución actualizada con comandos futuros, rutas/contrato y puertas de aceptación: `docs/EJECUTOR_ENTRENAMIENTO_MULTIDOMINIO.md`, commit `bc14f02e9387ba40147406e5982a889600125718`.
- Protocolo actualizado para describir componentes implementados y bloqueos restantes: commit `4f178c38b7f2faac62b3e09e7e689dbff75a688d`.

### Estado de verificación y seguridad

- No se ejecutaron las nuevas pruebas, el materializador, la factory, COCOeval ni el motor. El código nuevo está guardado, pero **no está validado aún**; no declarar tests PASS.
- El siguiente paso de validación es abrir el notebook `notebooks/colab_validacion_completa.ipynb` actualizado desde esta rama y ejecutar la suite completa sobre el HEAD final. Después, y sin optimización, ejecutar materialización/loaders train+validation y la prueba COCOeval; solo tras ello hacer prueba checkpoint/resume.
- El evaluador COCO tiene prueba sintética escrita, pero no se ha ejecutado ni contrastado con una muestra real. La métrica Mask AP todavía no debe publicarse como resultado experimental.
- No se ha iniciado materialización ni descarga de datos, no se ha iniciado entrenamiento ni se han creado checkpoints. `RUN_TRAINING=False` continúa intacto. La CLI requiere `run_training=true` y `--execute`, pero eso no sustituye autorización explícita.
- Auditoría Actions al cierre para SHA de protocolo `4f178c38...`: `fetch_commit_workflow_runs` y combined status no devolvieron runs/checks. No equivale a CI aprobado. No se lanzaron reruns. El run histórico `45240266965` para SHA previo tuvo job pytest failure con `steps=null`; no permite conocer la causa.
- PR #3 aparece abierta y su descripción mantiene explícitamente “Draft intencional. No fusionar todavía”. No se cambió estado ni se fusionó.
- Este bloque quedó guardado en la rama de trabajo mediante el commit de actualización del registro; el SHA de cierre se confirma en la auditoría GitHub de la respuesta.


#### Revisión estática posterior de factory y COCOeval — 2026-11-23

- Al inspeccionar los archivos guardados se detectaron y corrigieron detalles de integración antes de cerrar: normalización del campo `rgb` de UrbanSyn a `image` para los adapters; reordenamiento seguro de anotaciones por `sample_id`; inversión del mapping nombre→ID para categorías COCO; preservación de RLE binario en la llamada in-memory a COCOeval; eliminación de un literal de salto de línea mal insertado en la métrica semántica.
- Commits correctivos: factory `9d520bccff5e2ad1a0312305d5a581dfbffde92e`; COCO evaluator `e9b0b60eda375c8a50b942df99ceea21f9b8ec60`; motor semántico `71b14cf99879c78a5bf1e77d9f953fbf73051325`. No se han ejecutado tests ni un linter tras estas correcciones.
- Se revisó de nuevo el código fuente remoto y no se detectan ya los errores textuales de integración mencionados; sigue pendiente validación ejecutable, especialmente pycocotools/COCOeval real y factory con manifests descargados.
- Último HEAD antes de esta actualización del registro: `e9b0b60eda375c8a50b942df99ceea21f9b8ec60`. Actions/status asociados no se han considerado aprobados; no se lanzaron reruns.


#### Cierre de reproducibilidad y registro de losses — 2026-11-23

- El factory ahora fija la semilla antes de inicializar los pesos del modelo y comprueba que `num_classes` semántico coincida con `urban-v1`: commit `161e31623b083044a6da711fce2b9d4d73a14360`, ajuste de validación `7543c82e619f4e9a518cba1a70cc64717add0eaa`.
- Los checkpoints incluyen y restauran los estados de los generadores del DataLoader y del sampler, además de RNG Python/NumPy/PyTorch/CUDA: commit `cd6d5597e751c2712a5a5a473c2aefd99333c83d`. Se amplió la prueba de reanudación para comprobar la restauración del generador: `534f5fc6d3b791627eafea12106aa6e732c4d3c0`.
- El loop de instancias registra la media por época de cada componente de loss de Mask R-CNN: commit `02edad59bfdae8b556699c19681b2a6190e12df5`; prueba sintética añadida en `3918419920b36f9c686edd842d28798456ee9e99`.
- Guía y protocolo actualizados: guía `832f6a06e99415de7e9f05b2429a3141c68765d8`; protocolo `47c878b7b980b508522b69ae164efecfaed4e76d`.
- Aun así, ningún test nuevo se ha ejecutado. No afirmar compilación ni suite aprobada. Próximo paso obligatorio: ejecutar suite completa en Colab sobre el SHA final; revisar errores antes de materializar datos. Luego materialización/loaders train-validation sin entrenamiento, validación COCOeval y prueba de checkpoint/resume.
- Se mantiene `RUN_TRAINING=False`; no hubo descargas, optimización ni checkpoints. La CLI requiere doble activación, pero no se usará hasta autorización expresa. PR #3 permanece abierta y draft.


### Corrección tras validación Colab — IoU de clases sin soporte — 2026-11-23

- El usuario ejecutó el notebook sobre HEAD `9788cc2efa413845503d254bb1e6b4f0159bc411`: prueba dirigida del balanceador **1 passed**; suite completa **83 passed, 1 failed** en 30.37 s. Fallo: `tests/test_urban_experiment_runner.py::test_confusion_ignore_and_absent_class`; esperaba `iou_per_class[1] is None`, pero recibía `0.0`. No inició entrenamiento ni descargó datos.
- Causa: `semantic_metrics` calculaba IoU=0 cuando una clase no tenía soporte GT pero aparecía en predicciones (falsos positivos). El protocolo exige clases sin soporte GT como no evaluables y excluidas del mIoU, sin ocultar los FP de la matriz de confusión.
- Corrección en `src/urban_experiment_runner.py`: IoU ahora solo se define cuando `support > 0` y el denominador es positivo. Commit `cfdf1d7314c379fd29252362ad1d008fe20e061b`.
- Prueba de regresión nueva: clase ausente en GT con tres falsos positivos; exige IoU null, accuracy null y mIoU calculado solo con clase soportada. Commit `aca7e40bd3d7e4d164b3d895a7aca382ca830ef0`.
- Protocolo precisado para indicar que los FP siguen visibles en la matriz de confusión, pero la clase sin GT se excluye del mIoU: commit `7194445aba3c067c3f9a51c2f8fa5cbe28818731`.
- No se han ejecutado aún los tests tras el fix. Actions no muestra runs ni status asociados al commit de la corrección; no es evidencia de aprobación. El run anterior `45241919444` para SHA `9788cc2...` falló en job pytest; el conector devolvió `steps=null`, sin logs.
- Estado: no iniciar materialización ni entrenamiento hasta que Colab confirme suite completa verde. `RUN_TRAINING=False`; sin descargas ni entrenamiento. PR #3 permanece abierta, draft y sin fusionar.



### Segunda validación Colab y corrección de la prueba de orientación — 2026-11-23

- El usuario ejecutó el notebook sobre HEAD `d370146baf9790ef7f984bd8dd277cf786a14b24`: prueba dirigida del balanceador **1 passed**; suite completa **84 passed, 1 failed** en 25.97 s. El fallo quedó en `test_iou_absent_ground_truth_class_is_undefined_even_with_false_positives`: la matriz de confusión de la prueba producía soporte `[4,3]`, no el esperado `[4,0]`. No inició entrenamiento ni descargó datasets.
- Diagnóstico confirmado por `semantic_confusion_matrix`: las filas representan la clase real (GT) y las columnas la clase predicha; el soporte GT se calcula sumando filas. La implementación de `semantic_metrics` y su cálculo `support=m.sum(1)` son coherentes con esa convención. El test había codificado los tres falsos positivos en la fila GT de clase 1, por lo que la prueba era incorrecta; no se cambia el motor.
- Corrección de `tests/test_urban_experiment_runner.py`: matriz `[[4,3],[0,0]]`, que representa cuatro predicciones correctas de clase 0 y tres falsos positivos de clase 1, todos sobre GT clase 0. La prueba ahora exige soporte GT `[7,0]`, IoU de clase 1 indefinido, mIoU `4/7` y accuracy de clase 1 indefinida. Se documenta explícitamente la orientación filas=GT/columnas=predicción.
- Commit de la prueba corregida: `74d151a57d1a54df7962669dcedf83bc46c5cb05`. El motor `src/urban_experiment_runner.py` permanece sin cambios en esta corrección.
- Auditoría Actions del SHA anterior `d370146...`: run `45242636788`, workflow Python tests, conclusión failure; job `pytest` failure, pero GitHub devolvió `steps=[]`, sin logs. Combined status no devolvió estados. No se lanzó rerun.
- PR #3 comprobada abierta; su descripción mantiene **Draft intencional. No fusionar todavía**. No se cambió estado ni se fusionó.
- Pendiente: ejecutar nuevamente la prueba dirigida y la suite completa en Colab sobre el nuevo HEAD que incluya el commit `74d151a...` y la actualización de este registro. No iniciar materialización ni entrenamiento hasta suite completa verde. `RUN_TRAINING=False`; no se descargaron datos ni se inició entrenamiento.


### Suite completa aprobada en Colab — 2026-11-23

- El usuario ejecutó `notebooks/colab_validacion_completa.ipynb` sobre el HEAD exacto `ace39a56a3b46edb0a876cf23d0ea53e67d0aaf3`, rama `urban-models-and-benchmark`.
- Prueba dirigida del balanceador: **1 passed**, código de salida 0, 0.02 s. Log persistido en Drive: `MyDrive/ProcesamientoImagenes/validacion_colab/prueba_balanceador_20261123_185821.log`.
- Suite completa del repositorio: **85 passed**, código de salida 0, 27.29 s. Log persistido en Drive: `MyDrive/ProcesamientoImagenes/validacion_colab/suite_completa_20261123_185821.log`.
- Resumen JSON: timestamp `2026-11-23T18:58:57.562817+00:00`, `passed=true`, `focused_test_exit_code=0`, `full_suite_exit_code=0`, `training_started=false`, `datasets_downloaded=false`.
- Esta validación cubre la suite de pruebas del repositorio en el SHA indicado. No constituye validación integral de materialización remota, loaders reales, COCOeval con anotaciones reales, checkpoints/reanudación con loaders reales, ni entrenamiento.
- Auditoría al registrar: HEAD `ace39a56a3b46edb0a876cf23d0ea53e67d0aaf3`; PR #3 abierta, draft y sin fusionar. Los runs de Actions visibles en esta auditoría corresponden al mismo SHA pero aparecen fallidos; los jobs no exponen pasos/logs útiles, por lo que Actions no se declara aprobado y el PASS procede exclusivamente del log de Colab aportado por el usuario. No se lanzó ningún rerun.
- Se cierra la puerta de validación unitaria y se habilita la siguiente fase de preflight: materialización remota solo train/validation, inspección de espacio y hashes, smoke de loaders reales por cada dominio/tarea, COCOeval sintético y con muestra real, y prueba de checkpoint/resume. Esta fase debe permanecer sin backward/optimizer step/entrenamiento; test no se descarga ni se carga. La ejecución de materialización se hará de forma controlada en el runtime remoto y no en el teléfono.
- `RUN_TRAINING=False`; no se ha entrenado ningún modelo ni descargado datasets en esta validación. El piloto sigue requiriendo autorización expresa independiente. PR #3 permanece draft y sin merge.


### Implementación de preflight escalonado con datos reales — 2026-11-23

- Tras el PASS Colab de 85 pruebas en SHA `ace39a56a3b46edb0a876cf23d0ea53e67d0aaf3`, se preparó la siguiente fase, pero **no se ejecutó todavía** porque los nuevos scripts/notebook requieren validación unitaria sobre el HEAD actualizado.
- `scripts/materialize_urban_experiment_data.py` ahora tiene `--dry-run`, `--max-samples-per-split`, `--require-instances` y `--max-total-bytes`. El dry-run verifica coincidencia exacta de IDs manifest/index, `annotation_status=ok`, consulta tamaños remotos S3/Hugging Face de los assets seleccionados y calcula el presupuesto sin descargar RGB/máscaras. La ejecución limitada selecciona muestras con instancias GT, escribe manifests locales e índices de anotación filtrados/alineados por sample_id, valida tamaños descargados y procesa exclusivamente train/val. Los imports boto3/Hugging Face son lazy para que las pruebas unitarias no requieran credenciales/dependencias remotas.
- Pruebas nuevas `tests/test_materialize_urban_experiment_data.py`: selección determinista y limitada, preservación de input, validación de presupuesto de bytes, selección de muestras con instancias y rechazo de pools vacíos. **No ejecutadas todavía**.
- Nuevo `scripts/smoke_test_urban_experiment_factory.py`: prueba las cuatro combinaciones A2D2/UrbanSyn × semántica/instancias sobre muestras locales; valida batches train/val, targets, forward semántico, COCOeval real para instancias y round-trip de checkpoint/RNG del DataLoader. No llama `backward()`, `optimizer.step()` ni al loop de entrenamiento; no consume test.
- Nuevo notebook `notebooks/colab_preflight_datos_reales.ipynb`: recupera y verifica el artifact existente `14770171764`, reconstruye manifests/índices, hace preflight de una muestra por split/dataset y materializa solo cuatro muestras train/val con instancias positivas, límite de 2 GiB; después ejecuta el smoke. Solo informes/logs se copian a Drive; datos de muestra permanecen en disco temporal Colab. El notebook indica expresamente ejecutar primero la suite completa sobre HEAD actualizado.
- Documentación actualizada: `docs/EJECUTOR_ENTRENAMIENTO_MULTIDOMINIO.md` y `docs/PROTOCOLO_ENTRENAMIENTO_MULTIDOMINIO.md`.
- Commits relevantes: materializador `02d9f4120c31c37c33f60a865a89187e60803393`, selección por instancias `e5f525744dcb617927cd2cae1d45f8d5ff964322`, rechazo pool vacío `671c5749b059a26c3218a6fc5b670db66bc736df`, lazy imports `9e0bc2922fae3982b5c40aa3d56ede084482df59`; tests `be39daf3d27950903caa482ff8c03dc9213ff2c3`, `6298003d409a55613a3310dab9280594d8e9091d`, `a0f47cb6dec87f21e29cce7f419379be7d10e4bf`; smoke script `ab01a7adba4f31f1b36f44676c9084c48a107a10`; notebook `6c2b4e2b80edf503487c9dfa63391e45e8fdb531`, ajuste de orden de validación `4c70cc814a21363b52a961583d57ddd16ed57be4`; guía `6922cf2ac815462160f9228a36e68649cde6da29`; protocolo `2bc6c43c4757abc3330909018a511a5d1e6fc7d4`.
- Auditoría final: HEAD `4c70cc814a21363b52a961583d57ddd16ed57be4`; PR #3 abierta, draft y sin fusionar. Actions registra fallos en los últimos runs de la rama, pero el job `pytest` no expone `steps`/logs útiles. No se lanzó ningún rerun ni se declara CI aprobado.
- **Puerta inmediata:** ejecutar `notebooks/colab_validacion_completa.ipynb` de nuevo (la celda inicial actualiza branch) y compartir el resumen. No ejecutar aún el nuevo notebook de preflight hasta que la suite completa pase en el HEAD actualizado.
- Si la suite pasa, ejecutar `notebooks/colab_preflight_datos_reales.ipynb`. Ese primer smoke materializa solo 1 train + 1 val por dataset, seleccionados con instancias positivas; estima y limita esa descarga a 2 GiB. No representa una estimación de tamaño del dataset completo. La materialización completa se decide en una fase posterior con cálculo de almacenamiento.
- `RUN_TRAINING=False`; no se descargaron datos ni se inició entrenamiento durante esta implementación. PR #3 permanece draft y sin merge.



### Corrección de sintaxis tras validación Colab — 2026-11-23

- El usuario ejecutó la prueba dirigida del balanceador en HEAD `47b911ed275528d0482ace572fa9c1b72c023494`: **1 passed**.
- La suite completa no pudo recopilarse: `SyntaxError` en `scripts/materialize_urban_experiment_data.py:178`, causado por una secuencia literal `\\n` insertada entre dos entradas del diccionario del informe.
- El preflight remoto falló al importar el mismo script antes de iniciar materialización. El resumen aportado indica `datasets_downloaded=false` y `training_started=false`; no hay evidencia de que se haya tocado test.
- Corrección aplicada en el repositorio: reemplazada la secuencia literal por un salto de línea real. Commit: `646f27d30ae3400b4b0259ee6b309fffd863b1d3`. Se volvió a leer el archivo desde GitHub y se verificó visualmente que las dos entradas del diccionario están separadas correctamente.
- Actions consultado para el commit de corrección: no devuelve runs asociados en esta consulta. No se declara CI aprobado. No se lanzaron reruns.
- **Pendiente obligatorio:** volver a ejecutar la suite completa en Colab sobre el HEAD corregido. No ejecutar todavía el notebook de preflight remoto hasta obtener PASS. Si pasa, repetir el preflight; mantener el límite de 2 GiB, solo train/val y sin entrenamiento.
- No se ha ejecutado localmente pytest ni se ha confirmado aún que el módulo importe correctamente en Colab. `RUN_TRAINING=False`; PR #3 debe permanecer abierta, draft y sin fusionar.


### Validación unitaria del preflight escalonado — 2026-11-23

- El usuario ejecutó `notebooks/colab_validacion_completa.ipynb` sobre HEAD exacto `b813e1a5c3917c3b25f42cb049b976a1eeab3754`, rama `urban-models-and-benchmark`.
- Prueba dirigida del balanceador: **1 passed**, código 0, 0.03 s. Log: `MyDrive/ProcesamientoImagenes/validacion_colab/prueba_balanceador_20261123_192103.log`.
- Suite completa: **93 passed**, código 0, 31.14 s. Log: `MyDrive/ProcesamientoImagenes/validacion_colab/suite_completa_20261123_192103.log`.
- Resumen JSON: `2026-11-23T19:21:47.908250+00:00`, `passed=true`, `training_started=false`, `datasets_downloaded=false`. Se cierra la puerta de pruebas unitarias para el materializador corregido.
- Auditoría del código de preflight: notebook limita la materialización a 1 muestra por dataset/split, solo train/val, exige anotaciones con instancias positivas y fija presupuesto máximo de 2 GiB; valida SHA-256 del artifact de estadísticas; smoke posterior corre las cuatro combinaciones A2D2/UrbanSyn × semántica/instancias, COCOeval en instancias y round-trip de checkpoint/RNG, con 0 backward y 0 optimizer steps. El notebook reconstruye y verifica metadatos/manifiestos del artifact incluyendo filas de test, pero el materializador y loaders solo consumen train/val; no descarga imágenes/máscaras de test ni las pasa al modelo.
- GitHub Actions para HEAD `b813e1a...`: run `45247784488` de Python tests concluyó failure; job `pytest` no expone steps/logs (`steps=null`, `logs_url=null`). No se declara CI aprobado ni se lanza rerun. PASS de esta puerta procede exclusivamente de Colab aportado por el usuario.
- PR #3 sigue localizada y abierta en la búsqueda de PRs; conservar draft y sin merge.
- **Siguiente paso habilitado:** el usuario puede ejecutar ahora `notebooks/colab_preflight_datos_reales.ipynb` en Colab. La primera celda de trabajo remoto verifica artifact, manifests e índices; luego estima tamaños de cuatro muestras train/val y aplica límite 2 GiB antes de descargar. Si preflight PASS, materializa esas cuatro muestras y ejecuta smoke de loaders/forward/COCOeval/checkpoint. Si falla cualquier puerta, detener y compartir stdout/stderr; no ampliar materialización.
- `RUN_TRAINING=False`; el notebook de preflight no debe llamar backward/optimizer.step ni consumir test. No se ha iniciado entrenamiento ni descargado dataset completo.


### Corrección de importación del smoke de datos reales en Colab — 2026-11-23

- El usuario ejecutó la celda 7 del notebook `notebooks/colab_preflight_datos_reales.ipynb`; el proceso terminó antes de crear loaders o modelos con `ModuleNotFoundError: No module named 'scripts'` al importar `scripts.urban_experiment_factory`.
- Diagnóstico: al invocar un archivo por ruta (`python scripts/smoke_test_urban_experiment_factory.py`), Python coloca `scripts/` como primera entrada de `sys.path`; no garantiza que la raíz del repositorio esté disponible para imports absolutos `scripts.*`/ `src.*`, aunque subprocess use `cwd=WORKDIR`. El error ocurre durante importación y no implica fallo de anotaciones, loaders, COCOeval ni checkpoint.
- Corrección: el smoke script calcula `REPOSITORY_ROOT = Path(__file__).resolve().parents[1]` e inserta esa ruta al principio de `sys.path` antes de importar `torch`, `scripts.urban_experiment_factory` o `src.urban_experiment_runner`. Esto hace el script autocontenido respecto al directorio de trabajo y evita depender de configuración externa de `PYTHONPATH`.
- No se modificó el materializador ni el notebook de descarga; no se cambió el alcance de muestras (1 por split en preflight, materialización limitada a train/val y presupuesto 2 GiB). El fallo reportado ocurrió en la celda 7, después de materialización, por lo que no se afirma aún que el smoke real haya pasado.
- No se inició entrenamiento: el script conserva `training_started=false`, cero backward y cero optimizer steps. No se lanzó rerun de GitHub Actions.
- Pendiente: el usuario debe volver a ejecutar únicamente la celda 7 en el mismo runtime donde la celda 6 materializó los datos. Si el runtime se reinició, ejecutar de nuevo el notebook en orden para reconstruir los datos temporales. Compartir `urban_real_data_preflight_smoke.json` y logs si aparece otro error.
- Estado auditado antes de la corrección: HEAD `a7e6cf8f85aa5c3bf9d84c12bc63d5ef01e03848`; PR #3 abierta, draft y sin fusionar; último run Actions visible `45248530874` terminó failure sin que ello constituya evidencia sobre este error de Colab.
- `RUN_TRAINING=False`; no descargar dataset completo ni iniciar piloto hasta que el smoke de cuatro combinaciones termine PASS y se autorice expresamente.


### Preflight completo con datos reales: PASS — 2026-11-23

- El usuario ejecutó las celdas 4, 5, 6 y 7 de `notebooks/colab_preflight_datos_reales.ipynb` y compartió los resultados JSON/salidas. Se registra como evidencia aportada por el usuario; no se afirma que el agente haya ejecutado Colab.
- **Celda 4 — integridad manifests/índices:** PASS en los seis pares dataset/split. A2D2 train/val/test: 1000 filas cada uno; UrbanSyn train 1000, val 751, test 783. En los seis: IDs únicos, `ids_match=true`, `stats_match=true`, `task_manifests_match=true`. Esto valida concordancia de metadatos/índices, no descarga ni inspección de imágenes del split test.
- **Celda 5 — dry-run:** `PREFLIGHT_PASS`, `dry_run=true`, splits train/val, `test_touched=false`, `training_started=false`, 1 muestra por cada uno de los cuatro pares train/val, `require_instances=true`. Estimación remota 12,980,207 bytes (0.012 GiB), 10 activos; debajo del límite configurado de 2 GiB. Se identificaron 2 activos por muestra A2D2 (RGB/semantic) y 3 por muestra UrbanSyn (RGB/semantic/panoptic). Output previsto `/content/urban_data_preflight`.
- **Celda 6 — materialización real:** PASS, `dry_run=false`; materializadas 4 muestras en total: A2D2 train 1, val 1; UrbanSyn train 1, val 1. `test_touched=false`, `training_started=false`, `max_samples_per_split=1`, `require_instances=true`. Informe `materialization_report.json`; datos en runtime Colab `/content/urban_data_preflight`, índices locales en `/content/urban_data_preflight/local_annotation_index`. No se descargaron activos de test ni dataset completo.
- **Celda 7 — smoke de factory/evaluación/checkpoint:** `status=PASS` en las cuatro combinaciones:
  - A2D2 semantic: batches train/val [1,3,256,256], targets [1,256,256], 26,889 y 15,624 píxeles semánticos válidos; DeepLabV3+ forward [1,20,256,256], logits finitos; checkpoint/resume PASS.
  - A2D2 instances: train 6 instancias, val 2; cajas [N,4], máscaras [N,256,256], labels válidas; pycocotools.COCOeval PASS, 1 imagen y 2 GT de validación; Box AP/AP50/AP75 y Mask AP/AP50/AP75 = 0.0. Solo clase car tiene soporte (2 GT); las demás clases salen null por cero GT.
  - UrbanSyn semantic: batches train/val [1,3,256,256], targets [1,256,256], 64,942 y 65,247 píxeles válidos; DeepLabV3+ forward [1,20,256,256], logits finitos; checkpoint/resume PASS.
  - UrbanSyn instances: train 32 instancias, val 18; cajas [N,4], máscaras [N,256,256], labels válidas; pycocotools.COCOeval PASS, 1 imagen y 18 GT de validación; Box AP/AP50/AP75 y Mask AP/AP50/AP75 = 0.0. Clases person (12 GT) y car (6 GT) tienen soporte; otras clases null por cero GT.
- Los AP=0.0 son coherentes con inferencia de modelos no entrenados/pesos aleatorios y una sola imagen de validación por experimento. Confirman ejecución técnica del evaluador y estructura de targets, no calidad ni rendimiento predictivo. Los AP por clase con `null` significan que esa muestra no contiene GT para esa clase, no AP cero.
- Seguridad del experimento: dispositivo CPU, resolución smoke 256; `training_started=false`, `optimizer_steps=0`, `backward_calls=0`, `test_split_touched=false`. Checkpoint round-trip PASS en las cuatro tareas. No se entrenó ni se guardó checkpoint de entrenamiento.
- Informes en Drive del usuario:
  - `MyDrive/ProcesamientoImagenes/preflight_datos_reales/materialization_preflight.json`
  - `MyDrive/ProcesamientoImagenes/preflight_datos_reales/materialization_report.json`
  - `MyDrive/ProcesamientoImagenes/preflight_datos_reales/urban_real_data_preflight_smoke.json`
  - stdout/stderr del smoke en el mismo directorio.
- Dictamen: se cierra PASS la puerta de preflight de datos reales, integración factory/loaders, forward semántico, evaluación COCO y checkpoint/resume con muestras mínimas. No equivale a validación de entrenamiento, calidad del modelo, métricas fiables ni escalabilidad de memoria/tiempo a dataset completo.
- Próxima fase permitida: diseñar y ejecutar una auditoría de capacidad/almacenamiento y materialización incremental controlada de un subconjunto mayor de train/val, con límites explícitos y sin test; revisar memoria/VRAM y coste de cómputo. Antes de entrenar, revisar configuración final del piloto y solicitar autorización explícita. No activar `RUN_TRAINING` por este PASS.
- Auditoría GitHub al registrar: HEAD `af8a9f71a67aa03790a4f06b3780917f46337a08`; PR #3 `open=true`, `draft=true`, `merged=false`. Actions más recientes visibles para ese HEAD: Python tests run `45249418927` failure (y otro run `45249408008` failure); BDD probe `45249406181` failure. No se lanzaron reruns; el PASS de esta fase procede de Colab y no cambia el estado de CI.
- `RUN_TRAINING=False`; PR #3 permanece abierta, draft y sin fusionar.


### Implementación de auditoría de capacidad incremental — 2026-11-23

- A petición del usuario se implementó la siguiente fase, sin ejecutar materialización ni entrenamiento desde el agente.
- Nuevo notebook `notebooks/colab_auditoria_capacidad_incremental.ipynb`: reutiliza la reconstrucción/verificación de artifact, manifests e índices; registra entorno/CPU/GPU/RAM/espacio; ejecuta dry-run remoto de 50 muestras elegibles por dataset/split (hasta 200, train/val); luego dry-run exacto de 10 por split; requiere espacio libre >= 2× bytes estimados del lote + 1 GiB; materializa solo 10 train + 10 val por cada dataset (40 muestras totales) con presupuesto de 2 GiB; guarda reportes/logs en Drive y datos temporales en /content.
- Nuevo script `scripts/audit_urban_materialized_capacity.py`: crea las factories/loader datasets de las cuatro combinaciones, recorre directamente cada elemento de train/val una vez para evitar el muestreo con reemplazo de WeightedRandomSampler, valida shapes/valores finitos/máscaras/boxes/labels y cuenta píxeles o instancias; reporta tiempo de decodificación, bytes locales, espacio libre y RSS pico. No ejecuta forward, backward, optimizer.step, COCOeval ni entrenamiento.
- Límites explícitos: nunca pasa test al materializador ni a la factory; el notebook verifica metadatos de splits pero no descarga ni decodifica activos test. La selección del materializador es el prefijo determinista de muestras con instancias positivas, no estratificada por clase ni estadísticamente representativa. Los resultados sirven para capacidad de almacenamiento/lectura, no para calidad del modelo.
- La fase no fue ejecutada por el agente; requiere que el usuario ejecute el notebook en Colab y comparta `capacity_environment.json`, `capacity_estimate_50.json`, `capacity_estimate_10.json`, `capacity_materialization_report.json`, `urban_capacity_audit.json` y logs si falla.
- Auditoría previa al cambio: HEAD `d3faf18b65719f7934c446773afa4d0ebbddf293`; PR #3 abierta, draft y sin merge. Actions más recientes visibles en ese HEAD: Python tests `45250672339` y `45250658663` failure; BDD probe `45250658478` failure. No se lanzaron reruns ni se declara CI verde.
- No se modificó `RUN_TRAINING=False`; no se ejecutó entrenamiento, no se descargó material adicional y test sigue bloqueado.
- Commit de implementación esperado en esta rama; después de publicarse, Colab debe clonar/actualizar el nuevo HEAD al ejecutar el notebook.


### Ajuste de formato del notebook de capacidad — 2026-11-23

- Durante la verificación posterior a la publicación se detectó que las listas `source` del notebook nuevo podían concatenar líneas sin saltos. Se normalizó el contenido de las 20 celdas a texto con saltos de línea explícitos; se verificó el tipo/contenido de cada celda y el formato JSON del notebook.
- Commit correctivo: `28c6bea95c65f7f0f6d0aa90f3bb4689e1a2782c`. HEAD actualizado tras la corrección.
- La notebook final conserva 20 celdas: montaje Drive, actualización del repositorio, recuperación artifact, reconstrucción/verificación de seis manifiestos/índices, inventario de hardware/almacenamiento, dry-run 50, dry-run 10 + guardia de espacio, materialización 10 por split, auditoría de decodificación y entrega de reportes.
- No se ejecutó la notebook desde el agente. Los scripts/notebook nuevos todavía requieren validación de ejecución en Colab; Actions continúa sin CI verde y no se lanzaron reruns. La siguiente acción depende del usuario ejecutando la notebook final publicada.
- No se descargó ningún activo nuevo, no se ejecutó entrenamiento y no se tocó test.


### Corrección del SyntaxError en la primera celda de Colab — 2026-11-23

- El usuario reportó que la celda inicial ejecutaba instrucciones concatenadas (por ejemplo, drivefrom pathlib) y producía SyntaxError. Causa confirmada al inspeccionar el notebook publicado: las entradas de source en varias celdas eran líneas sin caracteres de salto de línea, por lo que Jupyter las concatenaba.
- Se restauraron los saltos de línea en las 20 celdas usando el contenido previo a la normalización defectuosa; cada celda conserva ahora su texto completo con separadores de línea explícitos.
- Verificación remota posterior: notebook JSON parseable; las 20 celdas tienen contenido íntegro y las celdas de código presentan saltos de línea reales. En particular, la celda 2 comienza con from google.colab import drive, sigue con imports en líneas separadas y contiene drive.mount como instrucción independiente.
- Commit correctivo definitivo: dafa49faf2ba80a71fa9d0c7f16595ac1743e2ba. La corrección se verificó en GitHub; todavía no se ha ejecutado nuevamente en Colab.
- No se modificó la lógica de descarga/materialización ni los límites. No se descargaron activos, no se accedió a test y no se inició entrenamiento.
- La auditoría de Actions previa a esta corrección mostraba runs 45251656751, 45251641828 y 45251641804 fallidos para el HEAD anterior e505de93bac55924571eeaffb00721e0326457f8; no se lanzaron reruns. PR #3 seguía abierta, draft y sin merge al inicio de esta corrección; debe permanecer así.


### Auditoría incremental de capacidad con datos reales — 2026-11-23

- El usuario ejecutó en Colab las celdas 4–9 del notebook corregido y compartió sus salidas. Se registra como evidencia aportada por el usuario; el agente no ejecutó Colab.
- **Celda 4 — integridad:** PASS en los seis pares dataset/split. A2D2 train/val/test: 1000 filas; UrbanSyn train 1000, val 751 y test 783. En todos: IDs únicos, `ids_match=true`, `stats_match=true`, `task_manifests_match=true`. Es validación de metadatos/índices; no implica descargar activos test.
- **Celda 5 — entorno:** HEAD usado por Colab `b837faba46b3507f58951edf2d72679bfa9a321a`; Python 3.13.18, PyTorch 2.14.1+cpu, Linux, CPU 2 núcleos, RAM total 13.61 GB y disponible 12.07 GB, disco total 115.66 GB y libre 115.31 GB. Sin GPU/CUDA. No test ni entrenamiento.
- **Celda 6 — estimación/materialización:** dry-run de hasta 50 muestras elegibles por dataset/split (hasta 200 muestras y 500 activos) estimó 0.607 GiB. El lote acotado de 10 muestras por cada dataset/split (40 muestras, 120 activos) estimó 0.12 GiB. Espacio libre antes de materializar 107.54 GiB; requisito calculado 1.24 GiB. Materialización PASS: A2D2 train/val 10/10 cada uno y UrbanSyn train/val 10/10 cada uno; 129,234,893 bytes locales. Espacio libre pasó de 115,472,338,944 a 115,340,476,416 bytes. Datos temporales en `/content/urban_data_capacity`, índice local en `/content/urban_data_capacity/local_annotation_index`; informes en Drive del usuario.
- **Celda 9 — auditoría de decodificación:** `status=PASS`, resolución 256, dispositivo CPU, 40/40 muestras decodificadas en las cuatro combinaciones. A2D2 semántica: 10 train/10 val, 243,701/254,833 píxeles válidos, 4.304/5.711 muestras/s. A2D2 instancias: 89/65 instancias GT, 5.589/5.795 muestras/s. UrbanSyn semántica: 652,053/646,562 píxeles válidos, 7.043/6.277 muestras/s. UrbanSyn instancias: 227/239 instancias GT, 3.135/4.886 muestras/s.
- RSS pico del proceso: 303.30 MiB al inicio y 554.34 MiB al final. Espacio libre reportado después de la auditoría: 115,309,649,920 bytes. No hubo llamadas forward, backward ni optimizer: `model_forward_calls=0`, `backward_calls=0`, `optimizer_steps=0`. `test_split_touched=false`, `training_started=false`.
- **Alcance de la conclusión:** la fase valida integridad de índices, materialización limitada, lectura/decodificación de RGB y anotaciones y consumo observado en un recorrido secuencial de 40 muestras. No es una prueba representativa estadística, ni estima VRAM o rendimiento de GPU, ni demuestra escalabilidad/tiempo/coste de entrenamiento completo. La selección es prefijo determinista de muestras con instancias positivas, no estratificada por clase. La máquina probada no tenía GPU y solo disponía de 2 núcleos CPU.
- Informes principales: `MyDrive/ProcesamientoImagenes/auditoria_capacidad/capacity_environment.json`, `capacity_estimate_50.json`, `capacity_estimate_10.json`, `capacity_materialization_report.json`, `urban_capacity_audit.json` y logs stdout/stderr.
- Auditoría GitHub al registrar: HEAD `b837faba46b3507f58951edf2d72679bfa9a321a`; PR #3 `state=open`, `draft=true`, `merged=false`; run de Actions asociado al HEAD `45253422295` (Python tests) terminó `failure`. No se lanzaron reruns; no se declara CI verde.
- No se entrenó, no se activó `RUN_TRAINING`, no se descargó el dataset completo y no se usaron activos de test. PR #3 debe seguir abierta, draft y sin merge.
- **Próximo paso técnico:** consolidar el dictamen de capacidad y revisar la configuración/estrategia del piloto de entrenamiento y la infraestructura disponible (GPU remota y almacenamiento persistente) antes de plantear entrenamiento. No iniciar entrenamiento hasta autorización expresa del usuario.


### Confirmación y corrección de auditoría de capacidad — 2026-11-23

- El usuario compartió los resultados completos de las celdas 4–9 del notebook de capacidad. La ejecución fue realizada por el usuario en Colab; el agente no ejecutó Colab.
- **Celda 4 — integridad:** PASS en los seis pares dataset/split. A2D2 train/val/test: 1000 filas cada uno; UrbanSyn train 1000, val 751 y test 783. En los seis casos: IDs únicos, `ids_match=true`, `stats_match=true`, `task_manifests_match=true`. La comprobación de test fue solo de metadatos/manifiestos; no se descargaron ni decodificaron activos test.
- **Celda 5 — entorno real:** el notebook informó HEAD `784676b6793151e3c36cee820a598232f59b9872`, Python 3.13.18, PyTorch 2.14.1+cpu, Linux, 2 CPU, RAM total 13,605,810,176 bytes y disponible 11,520,811,008 bytes, disco total 115,658,190,848 bytes y libre 115,304,906,752 bytes. CUDA no disponible y GPU list vacía.
- **Celdas 6–7 — estimación:** el dry-run de hasta 50 muestras elegibles por dataset/split (máximo 200 muestras y 500 activos) estimó 0.607 GiB. La selección exacta de 10 muestras por dataset/split (40 muestras, 120 activos) estimó 0.12 GiB. Antes de materializar había 107.39 GiB libres y el guardia calculó 1.24 GiB requeridos.
- **Celda 8 — materialización:** PASS. A2D2 train/val 10/10 cada uno; UrbanSyn train/val 10/10 cada uno. Se materializaron 129,234,895 bytes en `/content/urban_data_capacity`; índice local en `/content/urban_data_capacity/local_annotation_index`. El espacio libre reportado pasó de 115,435,266,048 a 115,303,641,088 bytes. Informes y logs guardados en `MyDrive/ProcesamientoImagenes/auditoria_capacidad/`.
- **Celda 9 — decodificación:** `status=PASS`, tamaño 256, CPU, 40/40 muestras decodificadas. A2D2 semántica: 10 train/10 val, 243,701/254,833 píxeles válidos, 4.176/3.901 muestras/s. A2D2 instancias: 89/65 instancias GT, 5.606/5.737 muestras/s. UrbanSyn semántica: 652,053/646,562 píxeles válidos, 7.163/7.233 muestras/s. UrbanSyn instancias: 227/239 instancias GT, 4.510/3.188 muestras/s.
- RSS pico: 317.30 MiB al inicio y 553.41 MiB al final. Espacio libre después de la auditoría: 115,303,514,112 bytes. `model_forward_calls=0`, `backward_calls=0`, `optimizer_steps=0`, `test_split_touched=false`, `training_started=false`.
- **Dictamen:** PASS para integridad de metadatos, materialización acotada y lectura/decodificación secuencial de RGB y anotaciones en 40 muestras. No es una prueba estadísticamente representativa, no estima VRAM ni velocidad GPU, y no demuestra que el entrenamiento completo quepa en RAM/VRAM o termine dentro del límite temporal. La selección es prefijo determinista de muestras elegibles con instancias, no estratificada por clase. El entorno medido fue CPU-only con dos núcleos.
- Archivos de evidencia principales: `capacity_environment.json`, `capacity_estimate_50.json`, `capacity_estimate_10.json`, `capacity_materialization_report.json`, `urban_capacity_audit.json` y logs stdout/stderr, en `MyDrive/ProcesamientoImagenes/auditoria_capacidad/`.
- Auditoría GitHub después de esta ejecución: el commit reportado por Colab es `784676b6793151e3c36cee820a598232f59b9872` (`docs: record incremental capacity audit results`). Actions asociado: run `45255474895` (Python tests) completado con `failure`; no se lanzaron reruns y no se declara CI verde. PR #3 verificada abierta; conservarla en draft y sin fusionar.
- No se activó `RUN_TRAINING`, no se inició entrenamiento, no se descargó el dataset completo y no se accedió a activos test.
- **Próximo paso:** consolidar la configuración del piloto y resolver/verificar un entorno GPU remoto persistente antes de cualquier entrenamiento. Mantener `RUN_TRAINING=False` y solicitar autorización expresa antes de ejecutar entrenamiento.


### Preparación de preflight GPU y persistencia — 2026-11-23

- Tras el dictamen PASS de decodificación en 40 muestras, el usuario indicó continuar con la prevalidación del entorno de entrenamiento. Se auditó primero el registro, HEAD, PR #3 y Actions.
- Estado inicial: HEAD fcab1dd7b851370b501142e8825343b37ba29571; PR #3 abierta, draft y no fusionada. Actions para ese HEAD: 45257510495 (pull_request), 45257491965 y 45257491972 (push), todos completados con failure. No se lanzaron reruns; no se infiere la causa del fallo.
- Revisión del protocolo: cuatro experimentos separados (DeepLabV3+ semántica A2D2/UrbanSyn y Mask R-CNN instancias UrbanSyn/A2D2); la factory crea modelos sin pesos preentrenados; configuración de piloto propuesta hasta 5 épocas, 90 min/job, 512×512 objetivo, batch mínimo 1, early stopping, checkpoint last/best. Estos valores siguen siendo propuestas, no config congelada ni autorizada.
- Añadido scripts/audit_training_runtime.py: informa versiones, GPU/CUDA/VRAM, RAM y disco de runtime/Drive; si hay CUDA, prueba una reserva sintética de 64 MiB; realiza escritura/renombrado/lectura y verificación SHA-256 de un checkpoint sintético en el Drive montado. El archivo de prueba se elimina. No usa dataset ni modelos, no ejecuta forward/backward/optimizer y deja explícitos training_started=false, dataset_downloaded=false, test_split_touched=false.
- Añadido notebooks/colab_preflight_entorno_entrenamiento.ipynb: monta Drive, actualiza repo privado mediante PAT read-only/Colab Secret, ejecuta auditor y guarda training_runtime_preflight.json en MyDrive/ProcesamientoImagenes/auditoria_entorno_entrenamiento/. Corregido el escape de saltos de línea de GIT_ASKPASS y verificado el JSON del notebook.
- Límite de la prueba: el checkpoint sintético verifica I/O en el montaje actual, no persistencia después de destruir/reiniciar la VM. La reserva CUDA de 64 MiB no estima la memoria requerida por DeepLabV3+ o Mask R-CNN. Una sesión CPU-only deja cerrada la puerta GPU aunque la parte Drive pase.
- El agente no ejecutó Colab. No se han descargado datasets, no se han usado activos test, no se ha ejecutado ningún modelo, no se ha probado un batch de entrenamiento, no se ha creado checkpoint experimental y no se ha activado RUN_TRAINING.
- Commits de implementación: auditor 3e721f2df81e379e5dfc13b38d2b500a9c90ebce; notebook 5554f608dbf3cc081d0a59bc4a87b1c960984357; corrección de askpass b4666f47d0a4dc77bdc37cc4e21e3e74a5f47f87.
- Próximo paso del usuario: abrir el notebook y ejecutar las celdas en orden, preferiblemente con acelerador GPU T4 si Colab lo ofrece. Si GPU_PASS=False, detenerse y compartir el JSON; si Drive I/O falla, no materializar datos ni entrenar. Aunque ambos pasen, se requiere una fase adicional de prueba de memoria específica por modelo/batch y revisión de pesos iniciales/configuración antes de solicitar autorización para el piloto.
- PR #3 debe seguir abierta, draft y sin merge. RUN_TRAINING=False.

- Verificación final después de publicar los documentos: HEAD `ce2ed931f66e4dd5d546f14b0bf589e582cd400f`; notebook JSON parseable con 8 celdas y línea GIT_ASKPASS corregida; auditor remoto no contiene llamadas a `optimizer.step()`, `backward()` ni al runner de entrenamiento. Actions automáticos asociados a los commits de documentación: `45258189245`, `45258179926` y `45258179878` para HEAD final, además de `45258170397` y `45258164795` para commits intermedios; todos terminaron `failure`. No se lanzaron reruns y no se atribuye una causa sin inspeccionar evidencia de los jobs. PR #3 continúa `open`, `draft=true`, `merged=false`.


### Corrección del preflight por error reportado en Colab — 2026-11-23

- El usuario compartió el informe `training_runtime_preflight.json` del 2026-11-23 20:23 UTC. Entorno: Python 3.13.18, PyTorch `2.14.1+cpu`, CUDA no disponible, cero dispositivos GPU; RAM disponible 12,185,280,512 bytes; Drive con 5,231,751,168 bytes libres. `training_started=false`, `dataset_downloaded=false`, `test_split_touched=false`, `forward_calls=0`, `backward_calls=0`, `optimizer_steps=0`.
- Diagnóstico GPU: runtime sin CUDA y PyTorch CPU-only; no puede aprobarse preflight para entrenamiento GPU. Debe seleccionarse acelerador GPU en Colab, verificar `nvidia-smi` y volver a ejecutar el notebook desde la primera celda. No instalar PyTorch manualmente sin conocer compatibilidad del runtime.
- Diagnóstico Drive: el checkpoint sintético se escribió, pero `torch.load(weights_only=True)` rechazó `torch.torch_version.TorchVersion` porque el script guardaba el objeto `torch.__version__` directamente. No es evidencia de fallo de Drive. Corregido a `str(torch.__version__)`; se conserva carga segura `weights_only=True`, sin desactivar protección.
- Cambiado el dictamen: se publican `drive_status` y `gpu_status` por separado y `status=PASS` exige ambos PASS. Notebook ahora imprime `nvidia-smi`, muestra instrucciones para activar GPU y permite leer el informe incluso si el proceso devuelve código 2; no aborta antes del dictamen.
- Cambios publicados: auditor corregido en commit `16f26fc0e68fae575abc965c9f5032a0bbcb7f7d`; notebook actualizado en commit `2a2c603bfd1fef446a8fe70faefdbd3570d93c53`. Sintaxis Python del auditor comprobada localmente con `compile()` (PASS); se debe volver a ejecutar en Colab para validar el I/O real.
- Sin entrenamiento, sin descarga adicional, sin acceso a test. `RUN_TRAINING=False`. PR #3 se mantiene abierta, draft y sin merge.


## 16. Preflight GPU/Drive aprobado y auditoría de memoria por arquitectura — 2026-11-23

El usuario ejecutó el notebook corregido en Colab y compartió el informe persistido. Evidencia recibida:

- GPU NVIDIA Tesla T4, 15,637,086,208 bytes de VRAM; nvidia-smi exit 0.
- PyTorch 2.14.1+cu130, CUDA 13.0, cuda_available=true, device_count=1, compute capability 7.5.
- Prueba de asignación GPU PASS (64 MiB; peak allocated 67,110,400 bytes).
- Drive checkpoint I/O PASS: 1,050,513 bytes, SHA-256 antes/después idéntico (ecc59f98a7a6600d67695805d5c423a954bdedf1ad0a43087575552b6d1a0c83), tensor_equal=true.
- Dictamen de la celda 4: DRIVE_IO_PASS=True, GPU_PASS=True, PREFLIGHT_READY=True.
- training_started=false, dataset_downloaded=false, test_split_touched=false, forward_calls=0, backward_calls=0, optimizer_steps=0.

Se considera superada la puerta de disponibilidad de GPU y escritura/lectura en el montaje actual de Drive. Esto no garantiza que la GPU siga disponible en otra sesión ni demuestra recuperación tras destruir la VM; los checkpoints de cualquier futuro piloto requerirán guardado frecuente y verificación de reconexión.

### Siguiente fase creada: auditoría aislada de memoria

Se añadieron:
- scripts/audit_model_memory.py: mide DeepLabV3+ semántico o Mask R-CNN de instancias con tensores sintéticos, un forward y un backward; registra VRAM pico/peak reserved/tiempo y clasifica OOM por caso. Nunca llama optimizer.step(), no abre datasets, no toca test y no guarda checkpoints.
- notebooks/colab_auditoria_memoria_gpu_por_arquitectura.ipynb: ejecuta en procesos aislados batch 1, 2 y 4 a 512×512 para cada arquitectura, AMP desactivado, valida el preflight persistido y guarda informes JSON en Drive. Un OOM en una combinación no aborta las siguientes; errores distintos de OOM sí detienen la auditoría.

Los resultados de memoria aún no se han ejecutado. Esta medición sintética aproxima memoria de forward/backward, pero no representa la variabilidad real de objetos/propuestas, augmentations, DataLoader ni validación. No autoriza materialización completa ni entrenamiento. Seleccionar inicialmente el batch más conservador con margen de VRAM; revisar los seis resultados antes de proponer el piloto.

### Estado de control

- RUN_TRAINING=False; no se activó entrenamiento ni se descargaron datasets como parte de esta fase.
- PR #3 permanece abierta, draft y sin fusionar.
- HEAD al crear los artefactos: 245127104bed00152b27c0335a73afc4c2aa4a93 (notebook); script: 5c15bb22187f431f5985ffa2f98354b678c7cc5f.
- Auditoría de Actions en HEAD anterior cea5231dff45e48ff1d9a1251f75d6c3d9245e0b: run más reciente observado 45259225867, failure. No se hizo rerun ni se atribuye causa.
- Próximo paso: ejecutar el nuevo notebook de memoria en Colab y compartir gpu_memory_audit_summary.json o la salida de la tabla. Después revisar margen de VRAM y decidir si hace falta una segunda medición con AMP o menor resolución.


### Verificación final de esta intervención — 2026-11-23

- Script audit_model_memory.py recuperado desde GitHub y compilado localmente con compile(): sintaxis Python PASS.
- Notebook colab_auditoria_memoria_gpu_por_arquitectura.ipynb recuperado desde GitHub y parseado como JSON: PASS, 9 celdas.
- HEAD final de la rama y head de PR #3: 7dc5046eefaa1c9c1b56628f90e80770ad0468b2.
- PR #3 verificada: open=true, draft=true, merged=false.
- Actions en HEAD final: runs 45261058618 y 45261047638 completados con failure. No se relanzaron; no se atribuye causa. Mantener pendiente el estado de runners/CI.
- Los artefactos de auditoría de memoria están publicados; todavía no se han ejecutado en Colab. RUN_TRAINING=False.


### Corrección del notebook de auditoría de memoria por SyntaxError en celda 1 — 2026-11-23

- El usuario reportó que la primera celda Python mostraba todo el código como una única línea con secuencias literales `\\n`, provocando `SyntaxError: unexpected character after line continuation character`. Diagnóstico confirmado al recuperar el notebook: las celdas tenían saltos de línea serializados incorrectamente como texto `\\n`, no como líneas reales.
- Corregido `notebooks/colab_auditoria_memoria_gpu_por_arquitectura.ipynb`: se reescribieron las nueve celdas con líneas reales. También se simplificó la autenticación Git del clon privado para usar un header temporal en el entorno del proceso, sin incluir el token en la URL ni dejarlo en la configuración del repositorio.
- Commit de la corrección: `a9b0bab093a34b2e194517a8fbc26a40b1ad6e07`.
- Verificación posterior desde GitHub: JSON válido, 9 celdas, 4 celdas de código; las celdas de código ya no contienen la secuencia literal `\\nfrom` que causó el error. HEAD de rama y PR #3 coinciden en `a9b0bab093a34b2e194517a8fbc26a40b1ad6e07`.
- PR #3 sigue `open`, `draft=true`, `merged=false`.
- Actions automáticos sobre el nuevo HEAD: runs `45266228739` y `45266220415`, ambos `failure`. No se hicieron reruns ni se infiere causa.
- La auditoría GPU de memoria aún no se ha ejecutado. La corrección resuelve el error de formato de la celda; no es todavía evidencia de que las seis pruebas de memoria pasen. RUN_TRAINING=False, no se cargan datasets ni se toca test.
- Próximo paso del usuario: volver a abrir/actualizar el notebook en Colab (recargar la pestaña para obtener la última versión) y ejecutar desde la primera celda. Si Colab conserva la copia anterior, cerrar y volver a abrir el enlace del notebook actualizado.

### Segunda corrección del notebook de auditoría de memoria: serialización de source — 2026-11-23

- El usuario volvió a reportar SyntaxError en la primera celda. El error mostraba instrucciones concatenadas (drivefrom pathlib, import pandas as pddrive.mount).
- La revisión directa del JSON publicado identificó la causa exacta: cada elemento de cells[].source contenía una línea sin terminador de salto de línea. En Jupyter, los elementos de esa lista se concatenan literalmente; separar cada línea en un elemento no inserta \n automáticamente. Por eso la corrección anterior parecía tener varias entradas pero Colab seguía recibiendo una sola línea.
- Corregido el notebook convirtiendo el contenido de cada una de las cuatro celdas de código en una cadena con saltos de línea reales explícitos dentro de source. Commit: 75349142448c4de32d3e2669d3ebcbc0ee9ebd1c.
- Verificación del commit: diff confirma \n dentro del contenido de cada celda; el archivo conserva 9 celdas y no se modificó la lógica de auditoría. El endpoint de runs asociado a este commit no devolvió ejecuciones; no se lanzó ningún rerun.
- Esta es una corrección del formato del notebook, no una prueba de ejecución en Colab. El usuario debe cerrar la copia abierta, abrir el notebook actualizado desde GitHub/Colab y ejecutar solo la primera celda para comprobar que desapareció el SyntaxError antes de continuar.
- Sin datasets, sin test, sin forward/backward/optimizer de entrenamiento; RUN_TRAINING=False. PR #3 se mantiene sin fusionar y en draft.

### Corrección de importación del paquete src en auditoría de memoria GPU — 2026-11-24

- El usuario ejecutó correctamente las celdas 1 y 2 del notebook. La celda 3 inició el caso semantic/batch=1 y el script devolvió FAIL con ModuleNotFoundError: No module named 'src'. El JSON confirma Tesla T4, PyTorch 2.14.1+cu130, CUDA 13.0; no cargó dataset, no tocó test y optimizer_steps=0.
- Diagnóstico: el notebook invoca el archivo como `python scripts/audit_model_memory.py`. En esa modalidad, `sys.path[0]` es el directorio scripts y el script no garantizaba incluir la raíz del repositorio para resolver imports `src.*`.
- Corregido `scripts/audit_model_memory.py`: calcula la raíz mediante `Path(__file__).resolve().parents[1]` y la inserta explícitamente en `sys.path` antes de importar el modelo. Commit: `71c94d96f7c1388622220705130f56665a25d0d6`.
- Comprobación estática: el módulo `src/models/deeplabv3plus.py` y el paquete `src/__init__.py` existen en la rama. Aún falta que el usuario repita la celda 3 para validar importación y medición real en la Tesla T4; no se afirma que el script ya haya pasado en Colab.
- No se modificó el notebook ni los parámetros de la auditoría. No se cargan datasets, no se toca test, no se llama optimizer.step(); esto es una prueba sintética de memoria, no entrenamiento. RUN_TRAINING=False.
- Antes de continuar, auditar HEAD/PR #3/Actions y comprobar la nueva versión publicada. PR #3 debe seguir abierta, draft y sin fusionar.


### Auditoría de memoria GPU por arquitectura completada en Colab — 2026-11-24

- El usuario ejecutó la auditoría completa en Google Colab sobre GPU Tesla T4; las seis combinaciones terminaron en PASS: DeepLabV3+ semántica e instancia/Mask R-CNN, batch 1, 2 y 4, resolución 512×512. No hubo OOM ni fallos reportados.
- DeepLabV3+ semántica: pico allocated 0.834/1.503/2.853 GiB y reserved 1.025/1.893/3.578 GiB para batch 1/2/4; pico incremental sobre modelo 0.682/1.350/2.700 GiB.
- Mask R-CNN instancias: pico allocated 0.844/1.422/2.585 GiB y reserved 0.939/1.563/2.834 GiB para batch 1/2/4; pico incremental sobre modelo 0.676/1.253/2.417 GiB.
- Tiempos por caso: semántica 2.582/0.726/0.863 s; instancias 1.340/1.097/1.242 s. Una llamada backward por caso; cero optimizer steps.
- El JSON quedó en Google Drive: `MyDrive/ProcesamientoImagenes/auditoria_memoria_gpu/gpu_memory_audit_summary.json`.
- El usuario confirmó explícitamente: `TRAINING_STARTED=False`, `DATASETS_LOADED=False`, `TEST_SPLIT_TOUCHED=False`, `OPTIMIZER_STEPS=0`. La auditoría usa tensores sintéticos y no representa entrenamiento completo, no evalúa memoria de optimizador tras inicialización/step ni pipeline real de datos, validación, checkpoints o fragmentación acumulada.
- Interpretación: en esta prueba la combinación más exigente fue semántica batch 4, con 3.578 GiB reservados (2.853 GiB allocated). Los seis casos caben en la T4, pero no se debe tomar batch 4 como configuración de entrenamiento garantizada. Para la primera prueba de entrenamiento real se recomienda comenzar conservadoramente con batch 1; evaluar batch 2 solo después de medir un paso real con datos y optimizador. No aumentar a batch 4 sin esa comprobación.
- Auditoría GitHub previa a registrar: HEAD de `urban-models-and-benchmark` y head de PR #3 coinciden en `ef6e0425954bd29af6e2a8e3d366ad6a59f3dacb`; PR #3 sigue abierta, draft y sin fusionar. Actions asociadas a ese HEAD siguen mostrando el run 45386028662 (Python tests) en failure; no se relanzó y no se atribuye causa.
- No se inició entrenamiento ni se descargaron datasets. `RUN_TRAINING=False` permanece vigente. Siguiente paso: preparar una validación controlada del primer paso de entrenamiento real, inicialmente batch 1, manteniendo separados dominio/tarea y sin tocar test; no iniciar el entrenamiento piloto hasta revisar ese preflight y recibir autorización.


### Preparación del preflight de un paso real con datos — 2026-11-24

- El usuario autorizó avanzar a la siguiente fase. Se consultó primero este registro y se auditó el estado actual: HEAD inicial `f9541a9d4a0d78a22f1b77e72d7ac0e14c7ff92d`; PR #3 abierta, draft y sin fusionar.
- Se revisaron `src/urban_experiment_runner.py`, `scripts/urban_experiment_factory.py`, `scripts/run_urban_experiment.py`, `scripts/materialize_urban_experiment_data.py`, `src/urban_training.py` y el protocolo. El runner existente ejecuta épocas y evaluación; no debe utilizarse para esta prueba de un solo batch.
- Añadido `scripts/urban_single_step_preflight.py`. Está separado del runner de épocas, exige `--execute-single-step`, requiere CUDA y usa la factory existente para una combinación por proceso. Solo itera un batch TRAIN real, batch 1, 512×512, workers 0 y AMP desactivado. Para semántica usa CrossEntropy con pesos calculados desde train; para instancias suma los losses de Mask R-CNN. Verifica loss/gradientes finitos, ejecuta un único `optimizer.step()` y comprueba cambio de parámetros.
- El script registra dataset/tarea, hardware, VRAM total/libre, peak allocated/reserved, tiempo, loss, norma de gradiente, número/tamaño de tensores del estado del optimizador y conteo de pasos. No itera validation (la factory solo carga metadatos y construye su loader), no abre test, no descarga ni materializa datos y no guarda checkpoints. Modelos aleatorios sin pretraining; LR 1e-4 solo de sondeo, no hiperparámetro aprobado.
- Añadido `notebooks/colab_preflight_un_paso_real.ipynb`. Verifica el preflight GPU/Drive persistido, seis casos PASS de la auditoría sintética de memoria y los 10 ejemplos train/val ya materializados por dataset. Si el runtime perdió `/content/urban_data_capacity`, se detiene y pide repetir la auditoría incremental; no descarga datos.
- La notebook contempla cuatro procesos aislados: A2D2 semántica, UrbanSyn semántica, A2D2 instancias y UrbanSyn instancias. Cada proceso puede completar como máximo un paso del optimizador. La ejecución queda bloqueada por defecto con `EXECUTE_SINGLE_STEP=False`; el usuario debe cambiarlo manualmente a `True` en la celda de autorización para permitir los cuatro pasos de preflight.
- Se corrigió el traslado de máscaras semánticas a CUDA mediante `.to(device='cuda', dtype=torch.long, ...)` y el esquema de lectura del informe sintético (`cases`). Se aclaró que la factory lee metadatos train/val, pero el preflight no itera validation.
- Actualizado `docs/PROTOCOLO_ENTRENAMIENTO_MULTIDOMINIO.md` con la sección 14 que describe alcance, guardias y limitaciones del preflight.
- Verificación de publicación: notebook JSON válido, 14 celdas, 6 celdas de código; `EXECUTE_SINGLE_STEP=False` en la celda de guardia. El script contiene el gate explícito `--execute-single-step`, una sola llamada a `optimizer.step()` y la corrección de dtype CUDA. No se ejecutó Colab ni se afirma que los cuatro pasos hayan pasado.
- Commits relevantes: script inicial `78718dcd8dad9e893106e3e88fe6a73213fb52d4`, corrección CUDA `0a4d6712a04897f11642d88851ba38c94db08ce5`, documentación de protocolo `e98aa0a858f5c9433d9e19ddfe78bfc6540c5904`, notebook final `5ecf535c3d22283c5b31cef7b0097cf97ae440f6`, última corrección/docstring script `0aa321da6dbdd3580b0d2bfd67d594890aded4ed`.
- HEAD de implementación inmediatamente antes de esta actualización del registro: `0aa321da6dbdd3580b0d2bfd67d594890aded4ed`; el commit de actualización del registro pasa a ser el HEAD de rama y de PR #3. PR #3 verificada abierta, `draft=true`, `merged=false`.
- GitHub Actions en el HEAD de registro previo `f220be5af0c34e3da64c70c988c8a369fc3b914b`: run `45389719529` estaba en curso al consultar; runs `45389711204` y `45389711187` completados con `failure`. En el HEAD de implementación anterior también fallaron `45389640418` y `45389627370`. No se relanzaron y no se atribuye causa sin evidencia de los jobs.
- No se ejecutó entrenamiento ni el preflight de un paso; no se descargaron datos, no se iteró validation/test, no se generaron checkpoints. `RUN_TRAINING=False` sigue vigente.
- Próximo paso: abrir `notebooks/colab_preflight_un_paso_real.ipynb` en Colab, ejecutar celdas 1–5 para comprobar precondiciones y revisar el guardia. Solo si se decide autorizar esta prueba acotada, cambiar `EXECUTE_SINGLE_STEP=False` a `True` y ejecutar la celda 6. Compartir `single_step_preflight_summary.json` y logs por combinación. No iniciar el piloto de épocas; analizar memoria real, pérdidas y fallos antes de proponer cualquier piloto.


### Error de materialización ausente en celda 4 del preflight de un paso real — 2026-11-24

- El usuario ejecutó la celda 4 de `notebooks/colab_preflight_un_paso_real.ipynb` y recibió `FileNotFoundError` porque no existe `/content/urban_data_capacity/materialization_report.json`.
- Diagnóstico: la auditoría incremental anterior materializó correctamente 40 muestras (10 por combinación A2D2/UrbanSyn × train/val; 129,234,893 bytes) en almacenamiento temporal `/content/urban_data_capacity`. Los informes sí quedaron persistidos en Google Drive (`MyDrive/ProcesamientoImagenes/auditoria_capacidad/`), pero los datos y el archivo `materialization_report.json` no. Al reiniciarse o cambiarse el runtime de Colab, el contenido temporal desaparece; por tanto, el preflight no puede reutilizarlo automáticamente.
- Remediación indicada: abrir y ejecutar en orden las celdas 1–9 de `notebooks/colab_auditoria_capacidad_incremental.ipynb` para reconstruir manifiestos, índices y materialización limitada de 40 muestras; no es necesario volver a ejecutar la celda 10 si solo se necesita restaurar el directorio, aunque ejecutarla completa vuelve a verificar decodificación. La celda 8 recrea `/content/urban_data_capacity/materialization_report.json` y copia el reporte a Drive.
- Después, volver a `notebooks/colab_preflight_un_paso_real.ipynb` y reejecutar las celdas 1–5. Mantener `EXECUTE_SINGLE_STEP=False`; no ejecutar la celda 6 ni iniciar entrenamiento sin decisión/ autorización explícita.
- Esta intervención no modifica código ni inicia ejecución en Colab. No se descargó ningún dataset desde esta conversación, no se tocó test ni se ejecutó entrenamiento; `RUN_TRAINING=False` permanece vigente.
- Auditoría de GitHub realizada antes de registrar: HEAD observado `02a69a9a2b776ffa00606d94e3d60f7e10020a53`; PR #3 sigue abierta y draft según la última verificación registrada, sin autorización de merge. Actions asociada al HEAD: run `45389800096`, `Python tests`, completed/failure. No se relanzó y no se atribuye causa.


### Reincidencia del FileNotFoundError y persistencia de datos entre runtimes Colab — 2026-11-24

- El usuario volvió a ejecutar la celda `data` (celda 4 visible) de `colab_preflight_un_paso_real.ipynb`; persiste la ausencia de `/content/urban_data_capacity/materialization_report.json`.
- Auditoría del código: la notebook incremental materializaba en `/content/urban_data_capacity`, pero la notebook de preflight usa su propio runtime Colab. Los runtimes de dos notebooks pueden ser distintos; por tanto, ejecutar la auditoría en uno no garantiza que el directorio temporal exista en el otro. La respuesta anterior no contempló esta separación y no debía asumir que ambas notebooks compartían el mismo almacenamiento temporal.
- Corrección publicada: `notebooks/colab_auditoria_capacidad_incremental.ipynb` ahora copia el directorio validado completo a `/content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity` al terminar la celda de materialización (celda 8). `notebooks/colab_preflight_un_paso_real.ipynb` ahora exige esa copia persistente en Drive, la restaura a `/content/urban_data_capacity` en su runtime y después verifica reporte/manifiestos/índices. Se conserva la limitación de 40 muestras, solo train/val.
- Commits de notebooks: preflight `556d756dd07cb804ab92fc233bfafa9b09eb159d`; auditoría incremental `8da41149f547765cd335c7b849cde87c27b47726`. Ambos JSON fueron parseados tras la edición. No se ejecutaron en Colab desde esta sesión.
- Próxima secuencia: abrir la notebook incremental actualizada desde GitHub, ejecutar celdas 1–8 y confirmar el mensaje `Copia persistente en Drive: /content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity`. Luego abrir la notebook de preflight actualizada, ejecutar celdas 1–4; la celda de datos copiará desde Drive al runtime actual. No ejecutar la celda de autorización ni el paso real todavía; mantener `EXECUTE_SINGLE_STEP=False`.
- No se ha ejecutado entrenamiento, no se ha tocado test y no se ha autorizado ningún optimizer step. `RUN_TRAINING=False` permanece vigente.


### Diagnóstico ampliado de la persistencia ausente en Drive — 2026-11-24

- El usuario ejecutó la celda de datos del preflight y recibió FileNotFoundError en /content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity/materialization_report.json. Esto confirma que la carpeta persistente no está disponible en el Drive montado por ese runtime; no demuestra por sí solo si la celda de materialización de la otra notebook no llegó al bloque de copia, si la copia falló o si se montó otra cuenta de Google.
- Revisión de la notebook incremental: la copia persistente está en la celda de código de la sección 8 (Materializar 10 muestras por dataset/split), índice 16 del JSON de la notebook. El mensaje de éxito solo se imprime después de copiar y verificar el informe y los ocho manifiestos/índices esperados. Por ello, es imprescindible confirmar ese mensaje exacto; completar secciones anteriores no basta.
- Se actualizó la celda data de notebooks/colab_preflight_un_paso_real.ipynb para diagnosticar si Drive está montado, si existe ProcesamientoImagenes, listar su contenido cuando falta urban_data_capacity y distinguir entre carpeta ausente y copia incompleta. Commit de diagnóstico: b31413aa334eb6ed54d9e5550c29690aa301a2d4.
- La celda de diagnóstico no descarga ni materializa datos, no itera loaders y no ejecuta entrenamiento. Se mantiene el gate EXECUTE_SINGLE_STEP=False; no ejecutar la celda posterior de autorización.
- Próximo paso: en la notebook incremental, ejecutar la celda de código de la sección 8 y confirmar si aparece el mensaje exacto: Copia persistente en Drive: /content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity. Si aparece, verificar que ambas notebooks montan la misma cuenta de Drive; después reabrir/actualizar la notebook de preflight desde GitHub y ejecutar la celda de datos para obtener el diagnóstico ampliado.
- No se ejecutó Colab desde esta sesión, no se inició entrenamiento, no se tocó test y no se autorizó ningún paso del optimizador.


### Confirmación del usuario: persistencia en Drive y auditoría incremental PASS — 2026-11-24

- El usuario compartió los resultados de los puntos 4–9 de `colab_auditoria_capacidad_incremental.ipynb`, ejecutados sobre HEAD `bddaf7e593c015d2fe28dabb15490350866d6f81`.
- Punto 4: seis combinaciones dataset/split (A2D2 train/val/test y UrbanSyn train/val/test) con IDs únicos y `ids_match`, `stats_match`, `task_manifests_match` en true. Son comprobaciones de manifiestos/índices; la presencia de metadatos de test no significa que se descargaran/leyeran assets de test.
- Punto 5: entorno detecta Tesla T4 (15,637,086,208 bytes VRAM), CUDA disponible, 2 CPU, RAM 13.6 GB y disco libre ~120.8 GB. El propio informe indica `training_started=false`, `test_split_touched=false`.
- Puntos 6–7: estimación de capacidad de 200 muestras ~0.607 GiB y 40 muestras ~0.12 GiB; estimaciones de almacenamiento, no entrenamiento ni uso del split test.
- Punto 8: materialización PASS de 40 muestras (10 A2D2 train, 10 A2D2 val, 10 UrbanSyn train, 10 UrbanSyn val), 129,234,883 bytes. La copia persistente en `/content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity` se completó y se imprimió el mensaje de confirmación; esto confirma que la carpeta quedó escrita/verificada por esa notebook en la cuenta Drive montada en ese runtime.
- Punto 9: auditoría de decodificación PASS en CPU, image_size 256, 10/10 muestras decodificadas en train y val para las cuatro combinaciones dataset/tarea (A2D2 semantic/instances, UrbanSyn semantic/instances). 0 test touched, 0 model forward, 0 backward, 0 optimizer steps; `training_started=false`.
- Interpretación: la persistencia de la materialización en Drive y la decodificación de las 40 muestras están confirmadas por los outputs aportados. El siguiente paso es reabrir/actualizar `colab_preflight_un_paso_real.ipynb` y ejecutar sus celdas iniciales hasta la celda de datos (la antigua celda 4) para verificar la recuperación desde Drive en ese runtime distinto. Si falla, conservar el nuevo diagnóstico que lista el estado de montaje y el contenido de la carpeta. No activar `EXECUTE_SINGLE_STEP` ni ejecutar la celda de paso real.
- Se auditó GitHub: HEAD de `urban-models-and-benchmark` = `bddaf7e593c015d2fe28dabb15490350866d6f81`; PR #3 sigue `open`, `draft=true`, `merged=false`. El workflow asociado a HEAD reporta un run completado con conclusión failure (ID 45410082612); no se relanzó. No inferir que el fallo tenga relación con los resultados Colab.
- No se ejecutó Colab desde esta sesión; no se inició entrenamiento, no se accedió a assets de test y no se autorizó ningún paso del optimizador.


### Preflight de entorno/memoria recuperado, pero CUDA no disponible en la sesión actual — 2026-11-24

- El usuario ejecutó el punto 3 de `notebooks/colab_preflight_un_paso_real.ipynb`. La celda leyó desde Drive un informe de runtime con timestamp `2026-11-23T20:31:12Z`: `status=PASS`, PyTorch 2.14.1+cu130, CUDA 13.0, Tesla T4 (15,637,086,208 bytes), `gpu_status=PASS`, `drive_status=PASS`; la prueba de escritura/lectura de checkpoint en el Drive montado también figura PASS. El informe indica cero entrenamiento, cero descargas, cero test y cero pasos de optimizador.
- El informe de auditoría de memoria recuperado contiene seis casos sintéticos PASS (DeepLabV3+ semantic y Mask R-CNN instances, batch 1/2/4, 512×512, AMP off), todos con `optimizer_steps=0`, `training_dataset_loaded=false` y `test_split_touched=false`. El artefacto declara HEAD `ef6e0425954bd29af6e2a8e3d366ad6a59f3dacb`; es una auditoría previa y no acredita el estado CUDA del runtime actual.
- La celda se detuvo en la comprobación local `torch.cuda.is_available()`, que devolvió false: `RuntimeError: CUDA no está disponible en esta sesión.` Por tanto, los informes persistidos son evidencia válida de que una sesión anterior pasó las pruebas, pero no demuestran que la sesión Colab actual tenga GPU. Tampoco se alcanzó la verificación/restauración de datos de la celda siguiente; la recuperación cross-runtime desde Drive sigue pendiente de confirmar en este intento.
- Instrucción operativa: en Colab seleccionar Runtime > Change runtime type > Hardware accelerator: GPU (si está disponible), guardar y reconectar; después ejecutar de nuevo las celdas iniciales de montaje/sincronización y el preflight GPU para obtener evidencia del runtime actual. Si Colab no ofrece/asigna GPU, detenerse y compartir el resultado de `torch.cuda.is_available()` y `nvidia-smi`; no intentar el paso del optimizador. No cambiar `EXECUTE_SINGLE_STEP=False`, no ejecutar la celda de paso real, no iniciar entrenamiento ni tocar test.
- Auditoría GitHub al registrar: HEAD de `urban-models-and-benchmark` = `0ec0544ec8fecc2d509cc25413b75a05b7c7d3fc`; PR #3 sigue `open`, `draft=true`, `merged=false`, head SHA igual a HEAD. Los cinco runs más recientes consultados (IDs 45412565501, 45412551733, 45412551730, 45410082612 y 45410070832) aparecen completed/failure. No se relanzó ninguno y no se atribuye la causa sin inspección de jobs/logs.
- No se ejecutó Colab desde esta conversación, no se ejecutó optimizer.step(), no se inició entrenamiento, no se descargaron datos y no se accedió a assets de test. `RUN_TRAINING=False` permanece vigente.


### Repetición del error CUDA en celda 3; informe mostrado sigue siendo histórico — 2026-11-24

- El usuario volvió a compartir exactamente la misma salida de la celda 3 de `notebooks/colab_preflight_un_paso_real.ipynb`. El JSON de runtime mantiene timestamp `2026-11-23T20:31:12Z`, Tesla T4 y `gpu_status=PASS`; el JSON de memoria mantiene seis casos sintéticos PASS y HEAD auditado `ef6e0425954bd29af6e2a8e3d366ad6a59f3dacb`. Son informes persistidos de una ejecución anterior, no una nueva detección del hardware en la sesión actual.
- La ejecución actual vuelve a fallar en `if not torch.cuda.is_available()` con `RuntimeError: CUDA no está disponible en esta sesión.`. Por tanto, sigue sin demostrarse que el runtime activo tenga CUDA; no se ha llegado a la celda posterior que restaura/valida `urban_data_capacity` desde Drive.
- Diagnóstico operativo: el usuario debe comprobar en Colab que el acelerador del runtime activo es GPU y que la sesión se reconectó después del cambio. Ejecutar primero una celda diagnóstica independiente con `!nvidia-smi`, `import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available(), torch.cuda.device_count())`. Si `nvidia-smi` no detecta GPU o `is_available()` es false, no continuar con el preflight de un paso; revisar Hardware accelerator/recursos disponibles y compartir esa salida. Si CUDA da true, reejecutar la celda 3 completa para que pase la comprobación local; no basta con leer los JSON antiguos.
- No volver a ejecutar auditoría sintética de memoria por ahora: sus seis casos ya están aprobados en el informe histórico y repetirlos no resolvería la ausencia de CUDA en el runtime activo. No cambiar `EXECUTE_SINGLE_STEP=False`, no ejecutar optimizer step, no iniciar entrenamiento ni tocar test.
- Auditoría GitHub al registrar: HEAD `urban-models-and-benchmark` = `fa5493f6ea193ef252a2de02eb7882e8e26436af`; PR #3 continúa `open`, `draft=true`, `merged=false`. Los tres runs más recientes de ese SHA (45414347529, 45414336229, 45414336222) están completed/failure; no se relanzaron y no se atribuye causa sin logs del job.
- Esta intervención no ejecutó Colab ni modificó código; solo se añadió este diagnóstico al registro. `RUN_TRAINING=False` permanece vigente.


### Diagnóstico GPU integrado directamente en la notebook Colab — 2026-11-24

- A petición del usuario, se actualizó `notebooks/colab_preflight_un_paso_real.ipynb` para incorporar una sección independiente **2.1. Diagnóstico del acelerador GPU en esta sesión**, situada inmediatamente antes del preflight que valida informes persistidos.
- La nueva celda ejecuta `nvidia-smi`, imprime timestamp UTC, versión de PyTorch, versión CUDA con la que fue compilado, `torch.cuda.is_available()`, número de GPU detectadas y, si existe, nombre y VRAM total de la GPU activa. Si no hay CUDA, imprime instrucciones para seleccionar GPU en Colab y reconectar.
- La celda es solo diagnóstica: no carga datasets, no ejecuta modelos, no hace forward/backward ni pasos del optimizador. La celda 3 conserva su guardia y seguirá deteniendo el flujo si CUDA no está disponible.
- Commit de notebook: `4807208ef44891a50b194cc511844225c14494e5`. El usuario debe volver a abrir/recargar la notebook desde la rama para ver la nueva sección y ejecutar la celda diagnóstica antes de la celda 3.
- No se ejecutó Colab desde esta conversación. No se inició entrenamiento, no se ejecutó optimizer.step(), no se descargaron ni materializaron datos y no se tocó test. `EXECUTE_SINGLE_STEP=False` y `RUN_TRAINING=False` permanecen vigentes.


### Corrección de la celda 2.1 por SyntaxError — 2026-11-24

- El usuario ejecutó la sección 2.1 y compartió `SyntaxError: unexpected character after line continuation character`. La salida mostraba que el código completo contenía secuencias literales `\\n` en vez de saltos de línea reales; por tanto, Python recibió la celda como una sola línea.
- Se corrigió `notebooks/colab_preflight_un_paso_real.ipynb`: el código de la celda `gpu-diagnostic` ahora se almacena como líneas reales del notebook (y el texto de la celda Markdown también tiene saltos normales). La lógica diagnóstica no cambia: consulta `nvidia-smi` y PyTorch/CUDA, sin datos ni entrenamiento.
- No se ejecutó Colab desde esta conversación. Esta corrección no prueba disponibilidad de GPU; después de recargar la notebook, el usuario debe ejecutar de nuevo la celda 2.1 y compartir su salida. No continuar a la celda 3 si CUDA no está disponible.
- No se inició entrenamiento, no se ejecutó `optimizer.step()`, no se descargaron/materializaron datos ni se accedió a test. `EXECUTE_SINGLE_STEP=False` y `RUN_TRAINING=False` permanecen vigentes. PR #3 debe permanecer abierta y en draft.


### Preflight de un paso real completado en Colab — 2026-11-24

El usuario compartió la salida completa de las secciones 3–6 de `notebooks/colab_preflight_un_paso_real.ipynb`. La celda 5 mostró autorización explícita para ejecutar exactamente un paso por combinación, en cuatro procesos aislados. Se registran los resultados reportados por Colab; no se ejecutó esta prueba desde ChatGPT.

**Entorno y datos**
- Runtime preflight: `PASS`; PyTorch `2.14.1+cu130`, CUDA `13.0`, una Tesla T4, 15,637,086,208 bytes de VRAM (≈14.56 GiB). La comprobación GPU/Drive guardada en ese informe tiene timestamp `2026-11-23T20:31:12Z`; no confundir ese timestamp con la ejecución de los cuatro pasos del día 24.
- Drive checkpoint I/O: `PASS`; escritura/lectura y SHA-256 coincidentes en el filesystem montado.
- Auditoría sintética: seis casos `PASS` (semantic e instances, batch 1/2/4, 512 px); todos con cero optimizer steps y sin datasets. Esos resultados son una auditoría sintética, no entrenamiento.
- Sección 4: Drive montado, carpeta `ProcesamientoImagenes` presente y materialización existente `PASS`; 10 muestras por split/dataset. No se descargaron datos.
- La sección 5 mostró: `AUTORIZADO: solo un paso por combinación; 4 procesos aislados; sin epochs/validation/test/checkpoints.`

**Cuatro ejecuciones reales reportadas por la sección 6**
| Dataset | Tarea | Estado | Loss | Gradientes | Norm L2 antes de clipping | Tiempo |
|---|---|---:|---:|---:|---:|---:|
| A2D2 | Semántica | PASS | 3.0183186531 | 186 | 164.0818 | 9.775 s |
| UrbanSyn | Semántica | PASS | 3.0219416618 | 186 | 80.0453 | 2.841 s |
| A2D2 | Instancias | PASS | 9.3387947083 | 201 | 1521.3171 | 4.529 s |
| UrbanSyn | Instancias | PASS | 9.2118835449 | 201 | 897.6709 | 3.878 s |

- Cada caso utilizó Tesla T4, imagen 512×512, batch 1, AMP desactivado y pesos aleatorios sin preentrenamiento.
- Cada caso ejecutó exactamente un `optimizer.step()`; los parámetros cambiaron. El resumen consolidado reporta `status=PASS`, `optimizer_steps=4`, `single_step_preflight_executed=true`, timestamp `2026-11-24T15:02:15.605634+00:00` y HEAD `571b15defa2362e2b8f141aeb21991de9b10c431`.
- No se iteraron batches de validación, no se tocó test, no se escribió checkpoint, no se descargaron datasets mediante el notebook y `pilot_training_started=false`.
- Pico de memoria asignada reportado: semántica 896,020,992 bytes por caso; instancias 908,294,144 (A2D2) y 913,029,632 (UrbanSyn). Los cuatro procesos finalizaron con return code 0.
- El informe resumen quedó en Drive: `/content/drive/MyDrive/ProcesamientoImagenes/preflight_un_paso_real/single_step_preflight_summary.json`. Los informes individuales y logs están bajo los subdirectorios `a2d2_semantic`, `urbansyn_semantic`, `a2d2_instances` y `urbansyn_instances` del mismo directorio.

**Interpretación y límites**
- El preflight de un paso real queda aprobado para las cuatro combinaciones y confirma compatibilidad operativa básica con la Tesla T4 y los batches seleccionados.
- Las pérdidas de una sola actualización no son métricas de calidad ni comparables como resultado de rendimiento entre datasets/tareas. No prueban convergencia, generalización, estabilidad de varias iteraciones ni calidad de segmentación.
- No se ha iniciado entrenamiento piloto, no se han entrenado modelos de forma sostenida ni generado checkpoints experimentales. No iniciar el piloto, evaluación o benchmark sin una autorización posterior explícita y un protocolo/configuración revisados.
- No se modificaron datasets ni assets de test. PR #3 debe continuar abierta y en draft.

**Próximo paso recomendado**
- Conservar o aportar al repositorio los JSON individuales, logs y `single_step_preflight_summary.json` como evidencia reproducible (sin subir datasets ni checkpoints). Antes de un piloto, revisar el script y la configuración de entrenamiento, inicialización/preentrenamiento, mapeo de clases, métricas y estrategia de checkpoints; definir presupuesto de tiempo/GPU y criterios de parada. No ejecutar nuevas actualizaciones hasta nueva autorización.


### Revisión estática de configuración y paquete de continuidad de un bloque — 2026-11-24

- Se consultó primero este registro y se revisaron `docs/PROTOCOLO_EXPERIMENTAL.md`, `docs/ESTRATEGIA_MULTIDATASET.md`, `docs/PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md`, `docs/REVISION_PREVIA_AL_PILOTO.md`, `configs/config.yaml`, `configs/urban_ontology_v1.json`, `scripts/urban_experiment_factory.py`, `scripts/urban_single_step_preflight.py`, `src/urban_training.py` y `src/urban_experiment_runner.py`.
- Hallazgos confirmados en el código: (1) DeepLabV3+ usa `pretrained_backbone=False`; Mask R-CNN usa `weights=None, weights_backbone=None`, por lo que el preflight de un paso partió de pesos aleatorios. (2) La factoría usa SGD para ambas tareas, mientras el protocolo propone AdamW para semántica y SGD para instancias. (3) La factoría usa `ReduceLROnPlateau(patience=1)`, frente a patience 2 en el protocolo. (4) Los adaptadores/factoría redimensionan directamente a 512×512 y deforman la relación de aspecto; falta letterbox/preservación de aspecto con transformación coordinada de máscaras y cajas. (5) `configs/config.yaml` es una configuración heredada Cityscapes/11 clases y no debe confundirse con el flujo multidataset `urban-v1` de 20 clases. (6) El reporte de paso único no congela hashes completos de manifests/índices/ontología, configuración efectiva, soporte por clase ni procedencia/versiones de pesos.
- La revisión previa al piloto ya documenta además que 10 muestras por split/dataset no son representativas; se requieren manifiestos completos y soporte por clase, auditoría visual de instancias A2D2 reconstruidas y prueba de métricas/checkpoint end-to-end antes de cualquier piloto.
- Se creó `docs/PAQUETE_CONTINUIDAD_UN_BLOQUE.md`, con un único bloque de texto para pegar en una conversación futura. Incluye reglas de seguridad, estado real, resultados reportados por Colab, hallazgos, próximos pasos y la instrucción de leer primero los documentos de continuidad.
- Se buscó la integración Google Drive/Docs: el conector Google Drive aparece `DISABLED_BY_ADMIN` y `NOT_AVAILABLE`. No fue posible crear ni actualizar un Google Doc. Como alternativa persistente, el paquete se guardó en el repositorio privado. No afirmar que existe una copia en Drive; la creación de esa copia queda pendiente de que la integración esté habilitada.
- Esta intervención fue de lectura y documentación: no se modificó código de entrenamiento, no se ejecutó Colab, no se ejecutó `optimizer.step()`, no se descargaron datos, no se abrió ni modificó test, no se inició piloto y no se lanzaron GitHub Actions. `RUN_TRAINING=False` se mantiene.
- Auditoría al registrar: HEAD previo observado `6117ef4703f56184c6ec9dbbeef37264631a0107`; PR #3 estaba abierta, draft y sin merge. Mantener ese estado.
- Próximo paso seguro: resolver las discrepancias de configuración y las transformaciones geométricas con pruebas unitarias, congelar configuración/hashes y auditar soporte de clases; después pedir autorización expresa antes de cualquier piloto.

## 2026-11-24 — Correcciones de configuración y transformaciones; notebook de auditoría segura

El usuario pidió preparar la actualización de pruebas anunciada previamente. Se consultaron primero este registro y `docs/PAQUETE_CONTINUIDAD_UN_BLOQUE.md`, además de inspeccionar el protocolo, notebook previa, factoría, adaptadores y runner en `urban-models-and-benchmark`.

### Cambios guardados en GitHub
- Se añadió `src/urban_optimizer.py`: semántica usa AdamW; instancias usa SGD; ambas tareas usan ReduceLROnPlateau con `mode="max"` y `patience=2`, según la tabla del protocolo.
- Se actualizó `scripts/urban_experiment_factory.py` para usar la factoría común.
- Se añadió `src/urban_geometry.py` con geometría letterbox, preservación de relación de aspecto, interpolación apropiada y conversión de cajas xyxy.
- Se actualizó `src/data_adapters.py`: imágenes y máscaras mantienen la misma geometría; padding semántico usa ignore 255 y padding de instancias usa background 0. Las cajas de instancias se derivan de máscaras ya transformadas.
- Se añadió `tests/test_urban_geometry_optimizer.py` con pruebas sintéticas de optimizador/scheduler, letterbox, máscara y geometría de cajas.
- Se sustituyó el contenido de `notebooks/colab_preflight_un_paso_real.ipynb` por una auditoría segura: no entrena, no hace backward/optimizer.step, no descarga datasets, no abre test ni escribe checkpoints. Comprueba las correcciones con datos sintéticos, calcula SHA-256 de código/ontología y de manifiestos/índices TRAIN/VAL existentes, registra versiones y soporte por clase cuando los campos estén disponibles, guarda JSON en Drive y muestra un bloque único de continuidad.

### Límites explícitos
- La notebook aún debe ejecutarse por el usuario en Colab; no se ha ejecutado desde esta conversación.
- Si faltan manifiestos/índices esperados, el reporte queda INCOMPLETE.
- La auditoría de soporte depende de los campos presentes en los índices; no inventa conteos.
- No existe todavía una configuración efectiva congelada por experimento ni procedencia completa de pesos de los modelos; la auditoría lo declara pendiente. No considerar este trabajo como autorización para piloto.
- Las pruebas sintéticas y el análisis estático no sustituyen pytest en runtime, inspección visual real, pruebas end-to-end de loaders/checkpoints ni CI.
- No se ejecutó entrenamiento, backward, optimizer.step, validación experimental, descarga de datos ni Actions. No se tocó test. `RUN_TRAINING=False`.

### Commits de implementación
- Geometría: `cad9046cf353ce36f52b31d2beb5b391bdf71616`
- Adaptadores: `f9d868dd63f8a995d1e65819496947f04bfb07a2`
- Factoría/optimizadores: `abe5baf7b8f389fda115b13cfb9f63c8874e2b7d`, `157fac9de6e3d87d2f31e5cc0f8db7793ed2a66e`, `ca12418f051d0b1ea9bea5baa684058bc4ccb116`
- Notebook: `bcbb2f35b9a8a6977b6e80b49cc26a114324b578`
- Pruebas: `55a76f1d29d3000f88db85e40e1dbb21c5ad2e59`

Próximo paso: ejecutar la notebook de auditoría segura en Colab y pegar únicamente el bloque delimitado. Después revisar el JSON, resolver los faltantes de configuración efectiva/procedencia de pesos y completar pruebas pendientes antes de solicitar autorización separada para el piloto.


### Cierre de la intervención — verificación final
- La notebook fue ajustada para declarar explícitamente `experiment_readiness=BLOCKED_PENDING_CONFIG_AND_WEIGHT_PROVENANCE`; las pruebas mecánicas pueden pasar sin que ello autorice un experimento.
- La notebook se guardó en `notebooks/colab_preflight_un_paso_real.ipynb`; JSON validado al releerlo desde GitHub.
- La PR #3 se verificó abierta, draft y sin merge. Su head debe coincidir con el último commit de esta intervención.
- No se ejecutaron pytest, Colab, entrenamiento, optimizer.step, descarga de datasets, lectura de test ni Actions. La validación ejecutada aquí fue inspección estática de archivos y estructura JSON.


## 2026-11-24 — Corrección de error de sincronización Git en Colab

El usuario reportó que la celda 1 mostraba que Drive ya estaba montado y fallaba con `CalledProcessError` en `git fetch origin urban-models-and-benchmark` (código 128). El mensaje de Drive es informativo, no causa del fallo. El traceback compartido no incluía stderr de Git, por lo que no se atribuye el código 128 a una causa remota específica.

Se corrigió la celda 1 de `notebooks/colab_preflight_un_paso_real.ipynb`:
- Detecta un Drive ya montado y omite `drive.mount()`.
- Verifica que `/content/Procesamiento-de-Im-genes-` sea realmente un repositorio Git.
- Si la ruta existe pero no es un repo, evita borrarla y clona en una ruta alternativa segura.
- Reescribe `GIT_ASKPASS` con saltos de línea reales y respuestas mediante `printf`.
- Usa el token únicamente en el entorno de los procesos Git, sin incluirlo en URLs ni imprimirlo.
- Captura stdout/stderr y entrega diagnóstico útil si fetch/clone/pull falla.
- Comprueba sincronización, rama y HEAD antes de continuar.

Commit notebook: `ff4706f8cbe1cbde7768425c18a0efa363932173`.

No se ejecutó la celda en Colab; el usuario debe volver a ejecutar únicamente la celda 1. Si vuelve a fallar, copiar el mensaje completo que ahora incluye el detalle stderr de Git, ocultando cualquier dato sensible. No se ejecutó entrenamiento, descargas, lectura de test ni Actions. `RUN_TRAINING=False`.


## 2026-11-24 — Sincronización Colab confirmada y corrección preventiva de notebook

- El usuario ejecutó la celda 1 de `notebooks/colab_preflight_un_paso_real.ipynb`: Drive ya montado; sincronización correcta; rama `urban-models-and-benchmark`; HEAD sincronizado `93d0c905ba7eef26c53292d586888d03382ec3d4`; `RUN_TRAINING=False`.
- Al inspeccionar la notebook antes de autorizar la siguiente celda, se detectó que el código de la celda de auditoría contenía secuencias `\\n` literales entre entradas del diccionario Python, lo que provocaría un error de sintaxis. Se corrigieron a saltos de línea reales.
- Commit de la corrección: `8e5e53cbf1f02bcb0edbfab6b040e1d521a7014c`. Notebook releída desde GitHub: JSON válido, 9 celdas y campos de estado presentes. La notebook corregida aún no ha sido ejecutada en Colab.
- No se ejecutó entrenamiento, optimizer.step, backward, descarga de datasets, lectura de test ni GitHub Actions. `RUN_TRAINING=False` permanece.
- Próximo paso: volver a ejecutar únicamente la celda 1 para traer el commit nuevo; después ejecutar la celda 2 (pruebas sintéticas) y revisar su salida antes de continuar. No ejecutar las demás celdas todavía.


## 2026-11-24 — Resultado de pruebas sintéticas en Colab

- El usuario ejecutó la celda de pruebas sintéticas de la notebook después de sincronizar la corrección: las nueve comprobaciones reportaron `true` y el resumen fue `PASS: 9 / 9`.
- Se verificaron los tipos de optimizador y scheduler para semántica/instancias, geometría letterbox, tamaño y padding de imagen, padding semántico, coherencia de máscara/caja de instancia y ausencia de gradientes/actualización del modelo toy.
- Pillow emitió un `DeprecationWarning` por el argumento `mode='RGB'` en `Image.fromarray`. No afectó el resultado ni provocó fallo; es un aviso de API obsoleta, no evidencia de error funcional.
- Estas pruebas son sintéticas y no prueban loaders con datos reales, entrenamiento, calidad ni generalización. No se ejecutaron optimizer steps, backward, epochs, descargas ni lectura de test. `RUN_TRAINING=False`.
- Próximo paso seguro: ejecutar únicamente la celda de la sección 3, que calcula hashes de código/ontología y archivos TRAIN/VAL presentes, resume soporte por clase y guarda el reporte JSON en Drive. Compartir su salida completa; no ejecutar todavía la celda final del bloque de continuidad.


## 2026-11-24 — Auditoría segura de datos y reproducibilidad: PASS

El usuario ejecutó en Colab la celda de auditoría de la sección 3 de `notebooks/colab_preflight_un_paso_real.ipynb` y reportó:
- Archivo JSON generado: `/content/drive/MyDrive/ProcesamientoImagenes/auditoria_correcciones_segura/urban_corrections_audit.json`.
- Estado: `PASS`.
- Archivos de datos con hash: 8.
- Archivos faltantes: 0.

Interpretación: los ocho archivos contemplados por la auditoría pudieron verificarse mediante hash y no se detectaron faltantes entre los archivos esperados de TRAIN/VAL. Este resultado, junto con las pruebas sintéticas 9/9, valida las comprobaciones mecánicas ejecutadas en la notebook; no equivale a congelar una configuración experimental ni acredita procedencia de pesos, convergencia, generalización o calidad.

No se ha recibido todavía el contenido completo del JSON ni el bloque final de continuidad; por tanto, no se atribuyen valores concretos a hashes individuales, soporte por clase o versiones de entorno. No se ha ejecutado la celda final todavía según el estado conocido. Próximo paso seguro: ejecutar únicamente la última celda, que imprime el bloque único de continuidad a partir del reporte guardado, y compartirlo para revisar el estado consolidado.

No se inició entrenamiento, no se ejecutó backward/optimizer.step/epochs, no se descargaron datos, no se tocó test, no se escribieron checkpoints y no se lanzaron GitHub Actions. `RUN_TRAINING=False` se mantiene. PR #3 debe seguir abierta y draft, sin merge.


## 2026-11-24 — Auditoría segura de datos y reproducibilidad: PASS

El usuario ejecutó en Colab la celda de auditoría de la sección 3 de `notebooks/colab_preflight_un_paso_real.ipynb` y reportó:
- Archivo generado: `/content/drive/MyDrive/ProcesamientoImagenes/auditoria_correcciones_segura/urban_corrections_audit.json`.
- Estado: `PASS`.
- Archivos de datos con hash: 8.
- Archivos faltantes: 0.

Interpretación: la auditoría encontró presentes todos los archivos esperados que comprobó y pudo calcular ocho hashes. Este resultado no equivale a validación visual de muestras, prueba end-to-end de loaders, congelación de configuración experimental ni verificación de procedencia de pesos. La notebook mantiene `experiment_readiness=BLOCKED_PENDING_CONFIG_AND_WEIGHT_PROVENANCE`; no autoriza entrenamiento.

No se ejecutó entrenamiento, optimizer.step, backward, epochs, validación experimental, descarga de datos, lectura de test ni GitHub Actions en esta intervención. `RUN_TRAINING=False` permanece. Próximo paso: ejecutar únicamente la última celda de la notebook para producir el bloque único de continuidad; revisar ese bloque antes de decidir las siguientes comprobaciones seguras.


## 2026-11-24 — Bloque final de continuidad de auditoría segura recibido

El usuario ejecutó la última celda de `notebooks/colab_preflight_un_paso_real.ipynb` y compartió el bloque completo. Datos reportados:
- `status=PASS`; `RUN_TRAINING=false`; `optimizer_steps=0`; `test_split_touched=false`; `missing_expected_files=[]`.
- `experiment_readiness=BLOCKED_PENDING_CONFIG_AND_WEIGHT_PROVENANCE`; `effective_experiment_config_frozen=false`; `model_weight_provenance_frozen=false`.
- HEAD de Colab al auditar: `5ac2e82581c88a0a4bbaecf48d43756dd8839ff8`.
- Índices: 10 filas en cada uno de `a2d2_train`, `a2d2_val`, `urbansyn_train`, `urbansyn_val`; son muestras de preflight, no datos representativos para entrenamiento.
- Los cuatro splits reportan `annotation_status_not_ok=0`.
- Hashes SHA-256 de fuentes: ontología `a65a3c6735c146b59fc361e29e595adc2f6b00d3e3d10d10923feaf56786ab64`; protocolo `00fecbc66763b9d12ccf0426ce6a22bbb87320c6390d431ee92a5eff703cf99b`; factoría `a137b07b98f4d0a8db38ce5472bdc252aa736c584a5f6af24d51e218d2b369d9`; adaptadores `0f6b44b4174b5bb7dd1630438fc9e6ad71f0e7250f97db1e5fbc8a9c8a1bf4ea`; geometría `fc2977dd6cbc11b4e362405365fc148b24f79beecdd6301fe9678bbc428a2adf`; optimizador `d497d0a13aa08ab7eb3e25741f1f01c73baa38766aea64947042113201a00202`. También se calcularon hashes de los cuatro manifests y cuatro índices TRAIN/VAL; los valores exactos están en el bloque compartido en esta conversación.
- JSON persistido en Drive: `/content/drive/MyDrive/ProcesamientoImagenes/auditoria_correcciones_segura/urban_corrections_audit.json`.

Soporte observado en las 10 filas por split (no representa frecuencias del dataset completo): A2D2 train instancias bicycle 5, car 86, person 7, truck 32; A2D2 val car 54 y truck 45 (bicycle/person no aparecen en esta muestra val). UrbanSyn train bicycle 3, bus 5, car 61, motorcycle 11, person 137, rider 12, truck 4; val bicycle 18, bus 5, car 62, motorcycle 10, person 129, rider 15, truck 6. Los cuatro splits tienen cero anotaciones con estado distinto de OK. Los conteos semánticos por clase también están en el bloque original; no interpretarlos como balance definitivo.

Interpretación: PASS valida las comprobaciones implementadas y la presencia/integridad por hash de los archivos esperados. Diez filas por split no son suficientes para entrenar ni inferir cobertura representativa. La falta de bicycle/person en las instancias de A2D2 val de esta muestra es una alerta que debe comprobarse sobre los manifiestos completos, no una afirmación de ausencia en el dataset. Persisten pendientes configuración efectiva congelada y procedencia verificable de pesos.

Próximos pasos seguros: congelar documentalmente y con hash la configuración efectiva Urban-v1 (tareas, clases, mapeos, tamaños/transformaciones, optimizadores/schedulers, hiperparámetros, seeds, versiones y política de inicialización); documentar procedencia/licencia/identidad exacta de los pesos o declarar inicialización aleatoria; auditar soporte sobre manifiestos completos TRAIN/VAL e inspeccionar visualmente muestras acotadas solo de TRAIN/VAL. Después diseñar un piloto separado y solicitar autorización expresa. No entrenar ahora.

No se ejecutaron entrenamiento, backward, optimizer.step, epochs, validación experimental, descargas, lectura de test ni GitHub Actions. PR #3 debe permanecer abierta, draft y sin merge.


## 2026-11-24 — Notebook único para cerrar los tres pendientes Urban-v1

El usuario solicitó reunir en un único Notebook de Colab los tres pendientes y generar al final un solo bloque con toda la información de continuidad.

### Artefactos creados en `urban-models-and-benchmark`
- `configs/urban_experiment_v1.json`: congela en un archivo versionado los cuatro experimentos (S-A2D2, S-UrbanSyn, I-UrbanSyn, I-A2D2), hiperparámetros de la tabla del protocolo, semilla 2026, geometría letterbox, métricas de selección y política de ejecución segura.
- `notebooks/urban_v1_cierre_tres_pendientes.ipynb`: Notebook único de 13 celdas para sincronizar repo, hashear configuración/ontología, comprobar procedencia de pesos, auditar manifiestos e índices completos TRAIN/VAL, resumir soporte por clase, comprobar assets/IDs/fuga, generar hoja visual determinista y guardar informe JSON + bloque final único.

### Decisiones explícitas congeladas
- Inicialización aleatoria, sin pesos preentrenados y sin checkpoint: la factoría declara `pretrained_backbone=False` para DeepLabV3+ y `weights=None, weights_backbone=None` para Mask R-CNN. No se inventa un artefacto de pesos inexistente.
- Configuración tomada de `docs/PROTOCOLO_ENTRENAMIENTO_EXPERIMENTAL.md`: 512×512; semántica batch 4, AdamW LR 1e-4, 20 épocas; instancias batch 1, acumulación 2, SGD LR 2.5e-3, momentum 0.9, 20 épocas; scheduler ReduceLROnPlateau mode=max, factor 0.5, patience 2; early stopping 5; clipping 1.0; seed 2026.
- Conteos de manifiestos esperados por protocolo: A2D2 1000 train/1000 val; UrbanSyn 1000 train/751 val. La notebook marca discrepancia como error; las muestras de preflight de 10 filas no se aceptan como cobertura completa.
- A2D2 instances continúa siendo aproximación por componentes conectados; UrbanSyn es baseline principal de instancias.

### Límites y estado
- `RUN_TRAINING=False`; cero optimizer steps/backward/epochs/checkpoints/descargas; no se lee ni modifica `test`; no se lanza CI; PR #3 permanece abierta, draft y sin merge.
- La T4 anterior solo comprobó un paso con batch 1; no valida batch 4 semántico ni acumulación 2 para instancias. El Notebook no prueba esos recursos ni entrena: el piloto de 10 batches requiere autorización explícita.
- La hoja visual contiene hasta 3 muestras deterministas por dataset/split (TRAIN/VAL únicamente). La revisión visual humana queda pendiente de confirmación del usuario.
- El Notebook y su JSON no han sido ejecutados por ChatGPT. El cierre de la auditoría de datos depende de que el usuario ejecute Colab con los manifiestos/índices completos ya disponibles en Drive.
- Los checks de assets contemplan alias de rutas habituales; si los archivos no están en las rutas esperadas, el reporte mostrará faltantes y no declarará PASS.

### Enlace Colab
https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_cierre_tres_pendientes.ipynb

### Próxima acción
El usuario debe abrir el enlace, ejecutar el Notebook completo en orden, revisar la hoja de contacto visual y pegar aquí únicamente el contenido entre `BLOQUE_CONTINUIDAD_INICIO` y `BLOQUE_CONTINUIDAD_FIN`. No iniciar entrenamiento.


### Alineación adicional de la configuración con el runner — 2026-11-24

Durante la inspección previa al cierre se detectó que dos parámetros de la tabla del protocolo no estaban aplicados realmente por el código: el scheduler no recibía `factor=0.5` y el runner no implementaba acumulación de gradientes para instancias. No se dejó esa discrepancia oculta:
- `src/urban_optimizer.py` ahora consume `scheduler_factor` y `scheduler_patience` desde la configuración (defaults 0.5 y 2).
- `src/urban_experiment_runner.py` implementa `gradient_accumulation_steps`, divide la loss por el tamaño efectivo del grupo, recorta gradientes y actualiza el optimizador al cerrar cada grupo; también maneja el último grupo parcial.
- `configs/urban_experiment_v1.json` usa los nombres de parámetros consumidos por factoría/runner: `image_size`, `max_epochs`, `patience`, `max_grad_norm`, `gradient_accumulation_steps`, scheduler factor/patience, etc.
- `tests/test_urban_experiment_runner.py` añade una prueba sintética de 4 batches agrupados de dos en dos (2 actualizaciones); `tests/test_urban_geometry_optimizer.py` comprueba factor 0.5.
- La notebook verifica estáticamente la presencia de acumulación/scheduler en el código, crea configuraciones listas para la factoría inyectando las rutas runtime y recoge hashes SHA-256 de factoría/runner/optimizador.

**Importante:** los tests se añadieron/actualizaron en GitHub, pero no se ejecutaron desde ChatGPT. No se afirma PASS de pytest ni de Colab. La notebook sigue sin ejecutar entrenamiento ni optimizer steps. El piloto de recursos continúa pendiente de autorización expresa.


### Validación estática final de artefactos — 2026-11-24

Se corrigió la celda de configuración de la notebook para verificar explícitamente que las cuatro configuraciones contienen los campos consumidos por factoría/runner, inyectar rutas runtime de Drive y comprobar acumulación de gradientes y factor del scheduler. El bloque final recoge hashes SHA-256 de factoría, runner y optimizador. Se validó que el archivo es JSON nbformat 4 con 13 celdas y que la última celda contiene los delimitadores de continuidad. La configuración JSON también se parseó y contiene cuatro especificaciones completas.

Esto es validación estática del contenido del repositorio, no ejecución de Python/pytest/Colab. No se ha confirmado ejecución de tests ni de la notebook.


La última revisión de la notebook endureció la auditoría: ahora un orden distinto entre IDs de manifiesto e índice se marca como error, y se exigen las claves de assets que consumen los adaptadores actuales (A2D2: `image`, `semantic`, `instance`; UrbanSyn: `rgb`, `semantic`, `panoptic`). También verifica que existan los archivos referenciados. La inspección final permanece limitada a TRAIN/VAL.


## 2026-11-24 — Corrección de SyntaxError en auditoría de Notebook Urban-v1

El usuario reportó que la celda de auditoría falló en Colab con `SyntaxError: unexpected character after line continuation character`. La causa fue que se guardaron secuencias literales `\\n` en medio de instrucciones Python, en lugar de saltos de línea reales. Se reemplazó íntegramente el código de la celda de auditoría en `notebooks/urban_v1_cierre_tres_pendientes.ipynb`.

La versión corregida declara explícitamente `expected_rows` (A2D2 1000/1000; UrbanSyn 1000/751), compara IDs y orden, agrega soporte semántico/instancias, exige campos de anotación y verifica assets, y detecta solapamiento TRAIN/VAL. Continúa sin tocar `test`, sin descargas y sin entrenamiento.

Validación realizada: JSON nbformat 4 parseado, 13 celdas presentes, cero secuencias literales `\\n` en la celda corregida, y compilación sintáctica Python de la celda corregida con resultado `Syntax OK`. No se ejecutó la auditoría sobre los datos ni se ejecutó Colab.

Commit de corrección del Notebook: `eec3d748482b8846f1a9791c496212139ff57580`.

Para continuar, el usuario debe volver a abrir/recargar el Notebook desde el enlace GitHub-Colab para cargar esta versión corregida; la copia que ya estaba abierta en Colab no se actualiza automáticamente. Después puede ejecutar el Notebook desde el principio. El bloque único final sigue siendo la última celda.


## 2026-11-24 — Corrección de resolución de assets antiguos en Drive

El usuario compartió el bloque final de la auditoría Urban-v1. Los cuatro manifiestos e índices existentes contienen 10 filas, frente a 1.000/1.000 para A2D2 y 1.000/751 para UrbanSyn. La auditoría anterior marcó assets ausentes porque los manifiestos conservaban rutas absolutas históricas bajo `/content/urban_data_capacity/`, mientras la ubicación persistente configurada es `/content/drive/MyDrive/ProcesamientoImagenes/urban_data_capacity/`. El bloque no permite afirmar si los archivos están o no en Drive; la resolución anterior no probaba la ubicación alternativa.

Se actualizó `notebooks/urban_v1_cierre_tres_pendientes.ipynb` (13 celdas) para:
- probar primero la ruta original y luego mapear el prefijo histórico `/content/urban_data_capacity/` a `DATA_DIR`, conservando registro de candidatos;
- distinguir assets encontrados en ruta original, encontrados tras remapeo y realmente no localizados;
- resumir campos comprobados y rutas físicas únicas para no confundir alias de una misma máscara (A2D2 `semantic`/`instance`) con archivos diferentes;
- usar el mismo resolvedor al construir la hoja visual;
- incluir en el bloque único los diagnósticos de resolución y las rutas candidatas de manifiestos.

La corrección es diagnóstica: no descarga archivos, no fabrica filas, no amplía automáticamente manifiestos de 10 a cobertura completa, no reescribe índices y no toca test. La auditoría seguirá INCOMPLETE hasta que existan manifiestos/índices con los conteos del protocolo y todos los assets requeridos sean accesibles. No se ha ejecutado Colab ni se ha comprobado físicamente la existencia de archivos en Drive desde ChatGPT.

Commit de notebook: `81cbd6486f6f302106ee71a245a877d054ec6b1d`.

Siguiente paso seguro: abrir la notebook actualizada en Colab, ejecutar desde el principio y compartir el bloque único. Según los diagnósticos reales, decidir si los assets ya están en Drive con rutas antiguas o si falta materializarlos. Si los manifiestos siguen en 10 filas, localizar/regenerar los manifiestos completos TRAIN/VAL y construir índices completos antes de la auditoría final. No iniciar entrenamiento; `RUN_TRAINING=False`.


## Resultado de cierre Urban-v1: assets localizados, manifiestos de preflight limitados — 2026-11-24

El usuario ejecutó `notebooks/urban_v1_cierre_tres_pendientes.ipynb` y compartió el resultado:
- Config SHA-256 `faa68c39f042c1aa8313123501fa25c280212d9f261236eb99fb4d6fd01f7e7f`; ontología SHA-256 `a65a3c6735c146b59fc361e29e595adc2f6b00d3e3d10d10923feaf56786ab64`. Las cuatro configuraciones S-A2D2, S-UrbanSyn, I-UrbanSyn e I-A2D2 se declararon completas; inicialización aleatoria, sin checkpoint, entrenamiento desactivado. Hashes reportados de factoría/runner/optimizador quedaron en el bloque del usuario.
- Resolución de assets: 120/120 campos encontrados tras remapear rutas antiguas a Drive; cero ausentes; 100 archivos físicos únicos. Esto confirma que los assets de las 40 muestras ya materializadas están accesibles mediante las rutas corregidas, no que el universo completo esté materializado.
- Los cuatro manifiestos e índices configurados contienen 10 filas cada uno. Protocolo: A2D2 train/val 1000/1000; UrbanSyn train/val 1000/751. Los IDs son únicos, coinciden en orden/conjunto, annotation_status no-OK=0, campos requeridos ausentes=0 y solapamiento train/val=0 en esas muestras. Cada split falla únicamente por discrepancia de conteo de filas.
- Hoja visual generada en Drive; 12 imágenes inspeccionadas por la notebook, con imagen y etiqueta localizadas en los 4 splits. La revisión visual humana sigue pendiente; no equivale a validar el conjunto completo.
- `RUN_TRAINING=False`, `backward_calls=0`, sin checkpoints ni acceso a test.

**Hallazgo de procedencia de manifiestos:** la notebook `notebooks/colab_auditoria_capacidad_incremental.ipynb` reconstruye en su sección 4 manifiestos completos desde el artifact de GitHub Actions `14770171764` (run `45038801547`), con `per_class_cap=null`, y sus índices de anotaciones. Pero la sección 8 materializa intencionalmente solo 10 muestras por split y persiste ese subconjunto en `MyDrive/ProcesamientoImagenes/urban_data_capacity`. Por eso la notebook de cierre ve 10 filas: no demuestra que el artifact carezca de las filas restantes. La reconstrucción completa queda en el runtime temporal `/content/cap200_input/manifests` y el índice extraído del artifact, no se ha confirmado su persistencia en Drive. El artifact puede expirar; no asumir que sigue disponible sin comprobarlo.

**Siguiente paso seguro:** recuperar/verificar el artifact completo si sigue accesible; reconstruir solo TRAIN/VAL (no leer ni materializar TEST), persistir manifiestos e índices completos en un directorio separado de Drive y comprobar conteos/IDs/hashes. Después ejecutar únicamente `--dry-run` del materializador sin límite de muestras para estimar bytes de los 3.751 registros; no descargar los assets completos hasta revisar la estimación y obtener autorización. No sobrescribir el directorio de las 40 muestras. No iniciar entrenamiento.

La ejecución reportada no demuestra que los 3.751 registros tengan assets descargados localmente; tampoco demuestra que falten. Se debe distinguir metadatos/manifiestos completos de materialización física. PR #3 permanece abierta, draft y sin merge.


## Preparación de recuperación completa y dry-run de almacenamiento — 2026-11-24

Se comprobó el artifact GitHub Actions ID `14770171764`, run `45038801547`: sigue disponible (`expired=false`), creado 2026-11-22 y con expiración indicada 2026-12-22. GitHub publica digest SHA-256 `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`. No se descargó el ZIP desde esta conversación ni se ejecutó Actions.

Se creó `notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb` para que el usuario lo ejecute en Colab. La notebook recupera el artifact y valida run, caducidad y digest; abre exclusivamente manifiestos semánticos/instancias e índices de A2D2/UrbanSyn TRAIN/VAL (no abre ni extrae miembros TEST); verifica conteos 1000/1000 A2D2 y 1000/751 UrbanSyn, IDs únicos/alineados, estadísticas, anotaciones OK, assets requeridos, revisiones UrbanSyn y ausencia de solapamiento TRAIN/VAL; reconstruye cuatro manifiestos y cuatro índices completos en una carpeta nueva `MyDrive/ProcesamientoImagenes/urban_v1_full_metadata_20261124`, sin sobrescribir las 40 muestras de `urban_data_capacity`; y ejecuta `scripts/materialize_urban_experiment_data.py --dry-run` sin límite de filas ni filtro de instancias para estimar los 3.751 registros. El script consulta tamaños remotos mediante metadatos/HEAD pero no descarga RGB/máscaras. Guarda hashes/reportes y genera un bloque único de continuidad.

La notebook quedó en GitHub con commits de creación y corrección de escapes: `6e0e350c9ceacf4c8b2b57fdfb6f4874e23f1575` y `f1bb84121a7cc47056db84e17387407b6c99e70c`. Se releyó desde GitHub y se verificó JSON nbformat 4, 13 celdas y corrección de los escapes de saltos de línea. No se ha ejecutado Colab ni se ha validado el Python contra el artifact; el resultado del dry-run está pendiente del usuario.

Enlace Colab: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb

Límites mantenidos: no descargar assets, no materializar datos completos, no tocar TEST, no entrenar, no escribir checkpoints y no lanzar Actions. El dry-run puede tardar por las consultas de tamaño remoto. Si el artifact expira antes de ejecutar la notebook, detenerse y reportarlo; no regenerar ni lanzar workflows sin autorización. PR #3 sigue abierta, draft y sin merge.


## Corrección de reejecución de celda de persistencia — 2026-11-24

El usuario informó que la celda 4 de `urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb` se detuvo porque `MyDrive/ProcesamientoImagenes/urban_v1_full_metadata_20261124` ya existía. El guard anterior impedía sobrescribir cualquier carpeta, pero también impedía reanudar una ejecución parcial o repetir la celda tras haberla completado.

Se corrigió la celda para que:
- compare los ocho JSONL existentes (cuatro manifiestos y cuatro índices) con los metadatos recién reconstruidos, incluyendo contenido y orden;
- reutilice la carpeta existente únicamente si los ocho archivos coinciden exactamente;
- si la carpeta es parcial o contiene otros datos, la conserve intacta y cree una carpeta nueva con sufijo UTC;
- verifique de nuevo los ocho archivos antes de seguir y registre `reused_existing_metadata`;
- nunca borre ni sobrescriba manifiestos/índices previos.

Commit notebook: `ff70758c679bd7c1785d316c72f5f47b85f39b14`. La notebook se modificó en GitHub; falta que el usuario recargue la versión actualizada y ejecute la celda. No se inspeccionó ni modificó Drive desde ChatGPT; no se puede afirmar si la carpeta existente está completa.

Enlace: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_recuperar_metadatos_y_dry_run_completo.ipynb

Mantener `RUN_TRAINING=False`, no descargar assets, no tocar TEST y no lanzar Actions. PR #3 continúa abierta, draft y sin merge.


## 2026-11-24 — Notebook de entrenamiento Urban-v1 autorizada por el usuario

El usuario autorizó iniciar el entrenamiento real de los cuatro experimentos. Se creó notebooks/urban_v1_entrenamiento_completo_gpu.ipynb en urban-models-and-benchmark (commit inicial a3197e7e7036ecbf5357bc3592489deaa383eca7; commit de corrección del preflight GPU 0ae5532c1a8feb1d742f61e5a6454189c2daca3e; commit de incorporación de pytest local c147bf362ecbfc67edf4eee2b2827595d77c8a28).

La notebook:
- exige GPU CUDA antes de descargar datos;
- ejecuta la suite local pytest -q sobre el HEAD sincronizado (esto no se declara como CI);
- recupera y verifica el artifact de metadatos, reconstruye y persiste solo TRAIN/VAL completos;
- ejecuta dry-run de los 3.751 registros y comprueba espacio temporal con 15% de margen;
- materializa TRAIN/VAL en /content de Colab, no en el teléfono ni en el repositorio;
- valida los 3.751 registros, rutas locales, IDs y aislamiento TRAIN/VAL;
- ejecuta piloto de 10 batches por cada una de las cuatro configuraciones; si falla cualquiera, bloquea entrenamiento completo;
- si los pilotos pasan, inicia S-A2D2, S-UrbanSyn, I-UrbanSyn e I-A2D2 con la configuración versionada, checkpoints reanudables y resultados en Drive privado;
- no lee ni evalúa TEST.

Configuración: semántica batch 4; instancias batch 1 y acumulación 2; 512 px; inicialización aleatoria; AMP desactivado; 20 épocas máximas y 5 de paciencia. Cada experimento dispone de hasta 5.400 s por sesión; si no termina, se conserva checkpoint y queda reanudable. Un OOM o error detiene el flujo para revisión.

**Estado real:** notebook creada y estructura JSON revisada desde GitHub; no se ha ejecutado en Colab, no se ha materializado el dataset completo y no existen nuevos checkpoints/entrenamientos derivados de esta notebook. La validación estática del JSON no equivale a compilar/ejecutar todas las celdas. La suite local de tests se ejecutará dentro de Colab antes de descargar datos. El usuario debe abrir la notebook, seleccionar T4 GPU y ejecutar desde el principio; después pegar el bloque único final o el traceback de la primera celda que falle.

Notebook Colab: https://colab.research.google.com/github/Leohf04/Procesamiento-de-Im-genes-/blob/urban-models-and-benchmark/notebooks/urban_v1_entrenamiento_completo_gpu.ipynb

Se mantiene PR #3 abierta, draft y sin merge. No se ha lanzado GitHub Actions.


## 2026-11-24 — Migración de la notebook de entrenamiento a Kaggle

El usuario decidió continuar el entrenamiento en Kaggle tras el bloqueo temporal de GPU de Colab y autorizó corregir errores durante la ejecución. Se consultó primero este registro y se inspeccionaron la documentación Kaggle, la notebook de diagnóstico y la notebook autorizada de entrenamiento.

### Hechos recuperados antes de migrar
- La notebook de entrenamiento existente era específica de Colab: montaba Google Drive y usaba rutas `/content`; no podía ejecutarse sin adaptación en Kaggle.
- El registro anterior documenta que Kaggle había mostrado `Permission denied` durante la verificación telefónica. El usuario ahora vuelve a elegir Kaggle, pero no se ha confirmado todavía que la cuenta permita activar GPU.
- La configuración congelada `configs/urban_experiment_v1.json` define cuatro experimentos **A2D2 + UrbanSyn**: S-A2D2, S-UrbanSyn, I-UrbanSyn e I-A2D2. No son experimentos BDD100K. El pipeline BDD100K de carriles es independiente.
- La notebook original exige recuperar el artifact GitHub Actions 14770171764 (run 45038801547, SHA-256 `b6cbcb54dfd0598e6a9011667073028be1804fc1c112d82e516a42bdbf2ba4e5`), validar TRAIN/VAL (3.751 registros), hacer dry-run, materializar datos, ejecutar pilotos de 10 batches y solo después entrenar. No accede a TEST.

### Cambio realizado
- Se creó `notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb` (24 celdas) en esta rama, commit `328564be95634df9c715dcb6b87c8751654c31dc`.
- Se sustituyó el bootstrap de Colab/Google Drive por Kaggle Secrets (`GITHUB_TOKEN`), `/kaggle/working` para repositorio/resultados y `/kaggle/temp` para artifact, dry-run y materialización temporal.
- Se conservó la verificación CUDA antes de descargas, pytest, comprobación de artifact/digest, auditoría TRAIN/VAL, aislamiento de TEST, pilotos obligatorios y política de checkpoints reanudables.
- Se actualizaron `docs/KAGGLE_NOTEBOOK.md` y sus instrucciones para la notebook de entrenamiento. La notebook de diagnóstico `notebooks/kaggle_environment_check.ipynb` se mantiene como herramienta de diagnóstico.

### Validación y límites
- La nueva notebook se serializó y releyó como JSON nbformat 4; contiene 24 celdas y no conserva referencias a `google.colab`, `drive.mount` ni rutas `/content/`.
- Se inspeccionaron celdas clave y rutas de resultados/materialización. Esto es revisión estática; **no equivale a ejecutar Python, pytest, Kaggle ni entrenamiento**.
- Kaggle documenta GPU gratuita sujeta a disponibilidad/cola, sesiones de hasta 12 horas y hasta 20 GB de salida en `/kaggle/working`; no se garantiza una GPU concreta ni cuota semanal fija. Fuente: https://www.kaggle.com/docs/notebooks
- No se ha confirmado que la cuenta del usuario supere la verificación telefónica, que pueda activar GPU/Internet, que el secreto funcione, que el artifact siga disponible desde Kaggle, que el espacio temporal sea suficiente ni que los tests/pilotos pasen.
- No se ha iniciado descarga de datos, piloto, backward, optimizer step, época ni checkpoint en Kaggle. No se afirma ningún resultado de entrenamiento.

### Siguiente paso
1. El usuario debe abrir Kaggle, crear un Notebook privado, importar `notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb` (archivo pequeño; no dataset), habilitar Internet y comprobar que puede seleccionar GPU.
2. Crear el secreto `GITHUB_TOKEN` con PAT fine-grained restringido al repositorio y permisos Contents: Read-only + Actions: Read-only.
3. Ejecutar en orden; compartir el primer traceback o el bloque final de continuidad, sin compartir el token.
4. Si el acceso GPU vuelve a mostrar `Permission denied`, detenerse: no hay forma de que ChatGPT active la GPU ni de eludir la verificación de Kaggle.

PR #3 permanece abierta, draft y sin merge. No se lanzó GitHub Actions ni se modificó TEST.

## 2026-11-24 — Investigación comparativa de GPU gratuita para entrenamiento Urban-v1

El usuario solicitó una investigación web profunda para identificar infraestructura gratuita donde ejecutar entrenamiento real de los cuatro experimentos A2D2/UrbanSyn (DeepLabV3+ semántica y Mask R-CNN instancias), con PyTorch/CUDA, acceso al repositorio privado y ejecución por etapas/checkpoints. Se prioriza no incurrir en gastos ni pedir transferencias de datasets desde el teléfono.

### Resultados verificados en fuentes públicas oficiales

**Kaggle Notebooks — mejor opción gratuita recurrente si se resuelve el bloqueo de verificación**
- La documentación oficial ofrece una NVIDIA Tesla P100 gratuita; puede haber cola/indisponibilidad. La documentación actual de notebooks especifica sesiones de hasta 12 horas y 20 GB de salida persistente en `/kaggle/working`; el espacio scratch fuera de esa carpeta no persiste al terminar la sesión.
- La página oficial de consejos de GPU publica una cuota de hasta 30 horas GPU por semana y sesiones de hasta 9 horas, lo que difiere de la ficha técnica actual de notebooks (12 horas). Por prudencia, planificar checkpoints y tratar 9 horas como límite operativo conservador; verificar el límite efectivo que muestre la cuenta.
- P100 ofrece 16 GB VRAM. La ejecución real de batch semántico 4 y Mask R-CNN batch 1/accumulation 2 debe decidirse mediante los pilotos obligatorios, no asumirse por especificación.
- La cuenta del usuario ya reportó anteriormente “Permission denied” en verificación telefónica. Por tanto, Kaggle es técnicamente la mejor opción pero no se considera disponible hasta que el usuario confirme que el selector permite activar GPU. No insistir en eludir la verificación.
- Fuentes oficiales: https://www.kaggle.com/docs/notebooks ; https://www.kaggle.com/page/GPU-tips-and-tricks

**Lightning AI Studios — viable para prueba con crédito inicial, no 80 horas garantizadas sin tarjeta**
- La documentación de Studio indica que toda cuenta recibe 5 créditos gratuitos (1 crédito = USD 1); añadir una tarjeta otorga otros 25 créditos. La página de precios anuncia hasta 30 créditos y hasta ~80 horas GPU en máquinas interruptibles, pero ese máximo depende de la máquina/tarifa y de obtener el bloque adicional de créditos; no debe presentarse como 80 horas universales sin tarjeta.
- El Studio CPU básico es gratuito. El plan Free permite un Studio activo con reinicios cada 4 horas; las GPU consumen créditos. La tabla oficial muestra GPUs T4/L4 y opciones de mayor VRAM, pero las tarifas varían; A100/H100/H200 tienen límites de sesión de 4 horas en Free según la tabla comparativa.
- Para este proyecto, 5 créditos sin tarjeta pueden servir para comprobar CUDA, ejecutar tests y pilotos parciales, pero no se puede prometer que alcancen para completar los cuatro entrenamientos. No añadir tarjeta ni habilitar pagos sin autorización expresa.
- Fuentes oficiales: https://support.lightning.ai/pricing/ ; https://lightning.ai/docs/platform/build/ai-studio/

**Google Colab Free — no es solución fiable en el estado actual**
- Google confirma que las GPUs gratuitas están fuertemente restringidas y que los límites, GPU disponible, duración máxima y tiempos de inactividad fluctúan; no garantiza recursos.
- El usuario ya recibió bloqueo por límites de uso, así que no se debe planificar el entrenamiento completo sobre Colab Free.
- Fuente oficial: https://research.google.com/colaboratory/faq.html

**Hugging Face ZeroGPU — descartar para entrenamiento**
- La cuota oficial de cuenta gratuita es de 5 minutos de GPU al día, con asignación dinámica en Spaces y límites de ejecución por función. Está pensado para inferencia/demos, no para entrenar cuatro modelos de 20 épocas.
- Fuente oficial: https://huggingface.co/docs/hub/main/spaces-zerogpu

**Paperspace Gradient Free — técnicamente débil y con problema de privacidad**
- La documentación de DigitalOcean confirma Free GPU M4000, autoapagado máximo de 6 horas, apagado por inactividad, un Notebook gratuito simultáneo y notebooks públicos en el plan Free. El M4000 dispone de 8 GB VRAM; es menos apropiado para batch 4 de segmentación y Mask R-CNN, y no debe usarse con un repositorio/datos privados si la sesión es pública.
- Fuente oficial: https://docs.digitalocean.com/products/paperspace/pricing/ ; https://docs.digitalocean.com/products/paperspace/machines/details/features/

**Amazon SageMaker Studio Lab — no disponible para nuevas cuentas**
- AWS indica que Studio Lab ya no acepta nuevos clientes; solo los usuarios existentes pueden continuar. No recomendar crear una cuenta nueva.
- Fuente oficial: https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lab-availability-change.html

**Saturn Cloud — descartar como GPU gratuita de entrenamiento**
- Aunque una página de captación anuncia horas gratuitas, la página actual de Hosted explica que Free sirve para familiarizarse con la plataforma y que el uso de recursos de cómputo GPU se desbloquea con Pro; las instancias GPU T4 se muestran con tarifa por hora. No confundir cuenta gratuita con GPU gratuita para entrenamiento.
- Fuente oficial: https://saturncloud.io/plans/hosted/

**Modal Starter — crédito recurrente, pero no opción sin método de pago**
- El plan Starter anuncia USD 30/mes de crédito de cómputo y permite entrenamiento GPU; el consumo GPU/CPU/memoria cuenta contra el crédito. Sin embargo, la documentación indica que GPU se habilita tras añadir un método de pago y que el uso fuera del crédito se factura pay-as-you-go. No recomendar para la restricción estricta de cero tarjeta/cero riesgo de cargos.
- Fuente oficial: https://modal.com/pricing

**Google Cloud Free Trial — no habilita GPUs durante la prueba gratuita**
- Aunque ofrece USD 300/90 días, la documentación oficial indica que no se pueden añadir GPUs a VMs durante el periodo de cuenta de prueba no facturable; las GPUs tampoco forman parte del Free Tier. Descartado como solución gratuita directa.
- Fuente oficial: https://docs.cloud.google.com/free/docs/free-cloud-features

### Recomendación resultante

1. **Primera opción práctica: Kaggle**, únicamente si el usuario puede activar GPU. Ya existe en el repositorio la notebook adaptada `notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb`; no requiere reescribir el flujo desde cero. Persistir resultados en `/kaggle/working` y respaldar checkpoints/logs al finalizar cada sesión. El bloqueo de verificación telefónica previo es el obstáculo pendiente.
2. **Segunda opción: Lightning AI**, para aprovechar los 5 créditos iniciales sin tarjeta como prueba técnica controlada. Antes de ejecutar, comprobar saldo, tarifa exacta de la GPU y que no haya facturación habilitada. No asumir que 5 créditos completarán el entrenamiento completo; podría requerirse una plataforma recurrente.
3. No dedicar tiempo a ZeroGPU, Studio Lab nuevo, Saturn, Paperspace M4000 ni Modal para el entrenamiento completo bajo la condición de cero gasto, por los límites documentados arriba.

### Plan de validación sin gastos
- No crear máquinas GPU ni activar facturación todavía.
- Confirmar visualmente en Lightning AI el saldo gratuito real, tipo de GPU, tarifa, límites de sesión y si la cuenta permite usar GPU sin tarjeta.
- Si solo hay 5 créditos, utilizarlos primero para validar CUDA, clonar repo privado mediante secreto de mínimo privilegio, instalar dependencias, correr pytest y ejecutar los pilotos definidos; detener el trabajo antes de agotar créditos. No iniciar épocas completas hasta tener un plan de continuidad suficiente.
- Si Kaggle permite GPU en el futuro, priorizar la notebook ya migrada y ejecutar el preflight/pilotos antes de entrenamiento.
- Mantener intactos los datos, configuración y checkpoints; no tocar TEST. No iniciar un entrenamiento real ni generar checkpoints como resultado de esta investigación.

### Estado
Investigación web completada. No se creó cuenta, no se añadió método de pago, no se habilitó GPU, no se descargaron datos ni se ejecutó entrenamiento. PR #3 continúa abierta, draft y sin merge.


## 2026-11-24 — Filtro de elegibilidad por nacionalidad/residencia cubana para GPU gratuita

El usuario pidió filtrar las alternativas gratuitas de entrenamiento teniendo en cuenta que es estudiante cubano. Se verificaron fuentes oficiales y se distinguió nacionalidad de residencia física, afiliación institucional y elegibilidad del proveedor.

### Hallazgos verificados

**Lightning AI**
- Sus términos de servicio contienen una declaración de que el cliente no está ubicado en un país sujeto a embargo estadounidense. Si el usuario está físicamente en Cuba, no debe usarse ni intentarse eludir la restricción. La nacionalidad cubana por sí sola no equivale a estar ubicado en Cuba; el proveedor aplica sus propios controles y debe confirmar elegibilidad si hay duda.
- Fuente: https://studio.lightning.ai/legal/terms-and-conditions/

**DigitalOcean / Paperspace**
- Los términos de DigitalOcean (aplicables a sus servicios) declaran que el usuario no puede estar ubicado en Cuba, Irán, Corea del Norte, Siria o Crimea. Paperspace Gradient pertenece al ecosistema DigitalOcean, por lo que no recomendarlo para alguien ubicado en Cuba.
- Fuente: https://www.digitalocean.com/legal/terms-of-service-agreement-june-2025

**Kaggle**
- La cláusula pública que excluye a residentes de Cuba localizada en los términos de Kaggle está expresamente dentro de la sección de competencias/contests. No debe extrapolarse automáticamente a todos los notebooks o al uso general de la plataforma.
- Sin embargo, este usuario ya intentó la verificación telefónica con un número cubano (+53) y recibió “Permission denied”. Por tanto, Kaggle no es una alternativa operativa confirmada para esta cuenta. No sugerir falsear país, número ni identidad.
- Fuentes: https://www.kaggle.com/terms ; https://www.kaggle.com/docs/notebooks

**Google Colab**
- La FAQ oficial describe el servicio gratuito como orientado al aprendizaje automático, ciencia de datos y educación, pero confirma que las GPU no están garantizadas y los límites son dinámicos. No se encontró en los términos de Colab consultados una prohibición general explícita por nacionalidad cubana; eso no constituye una garantía legal o de acceso desde Cuba.
- El usuario ya agotó el límite de GPU de Colab. Mantenerlo como alternativa futura, no como entorno de entrenamiento inmediato.
- Fuentes: https://research.google.com/colaboratory/faq.html ; https://research.google.com/colaboratory/tos_v6.html

**Hugging Face**
- Sus términos exigen cumplimiento de controles de exportación y sanciones estadounidenses y de otras jurisdicciones, sin que el texto consultado establezca una exclusión simple por nacionalidad cubana. ZeroGPU gratuito tiene cuota insuficiente (5 minutos/día), por lo que no sirve para entrenar los cuatro experimentos.
- Fuente: https://huggingface.co/terms-of-service

**NSF ACCESS — oportunidad académica relevante si el usuario estudia/está basado en EE. UU.**
- ACCESS proporciona recursos de cómputo y GPU sin coste, por asignación aprobada, y ofrece recursos HPC GPU (por ejemplo Anvil, Delta, Bridges-2, Jetstream2 según disponibilidad).
- La página Classroom declara elegibilidad para estudiantes basados en EE. UU. que necesiten cómputo para clases. La política de asignaciones establece que estudiantes de pregrado no pueden liderar una asignación de investigación, pero pueden usar recursos bajo la guía de un instructor/asesor elegible; estudiantes graduados basados en EE. UU. pueden liderar proyectos Explore/Discover con carta/guía del asesor. Se requiere afiliación institucional y correo organizacional coincidente.
- La política contempla usuarios internacionales como colaboradores bajo una asignación de un PI elegible, con justificación y aprobación; esto no garantiza elegibilidad de alguien ubicado en Cuba y debe consultarse con ACCESS/PI.
- Recursos oficiales: https://allocations.access-ci.org/classroom ; https://allocations.access-ci.org/allocations-policy ; https://access-ci.org/get-started/for-graduate-students/ ; https://support.access-ci.org/documentation/resources/anvil-gpu

**OFAC / nacionalidad cubana fuera de Cuba**
- OFAC FAQ 791 indica que los nacionales cubanos fuera de Cuba pueden seguir sujetos a bloqueo, con licencia general para quienes establecieron residencia permanente fuera de Cuba y cumplen 31 CFR 515.505; también autoriza a personas sujetas a jurisdicción estadounidense a proporcionar bienes/servicios a individuos cubanos ubicados fuera de Cuba, siempre que no exista exportación comercial de bienes/servicios hacia o desde Cuba. Esto no debe interpretarse como asesoría legal ni como garantía de que un proveedor acepte al usuario.
- Fuentes: https://ofac.treasury.gov/faqs/791 ; https://www.govinfo.gov/content/pkg/CFR-2025-title31-vol3/xhtml/CFR-2025-title31-vol3-subtitleB.html

### Clasificación práctica provisional

- Si el usuario reside en Cuba: descartar Lightning AI y DigitalOcean/Paperspace por sus términos basados en ubicación. Kaggle no está confirmado para su cuenta por el bloqueo de verificación +53; no intentar eludirlo. Colab/Hugging Face requieren confirmación de acceso y límites; ZeroGPU no sirve para entrenamiento. Investigar primero acceso académico supervisado (ACCESS si hay institución/PI elegible) y preguntar al proveedor por elegibilidad antes de subir datos o ejecutar.
- Si el usuario reside fuera de Cuba: no excluir por nacionalidad automáticamente. Verificar situación/ubicación y condiciones del proveedor; ACCESS puede ser especialmente atractivo si está afiliado a institución estadounidense. La elegibilidad final depende de estatus, afiliación y aprobación.
- No usar VPN, datos falsos, cuentas prestadas ni medios de pago de terceros para evadir restricciones.

### Estado / dato pendiente
No se puede cerrar la lista de plataformas elegibles hasta confirmar dónde reside/estudia físicamente el usuario y si es estudiante de pregrado o posgrado, además de si tiene correo institucional. No se han creado cuentas, agregado tarjetas, habilitado GPU, transferido datos ni iniciado entrenamiento.


## 2026-11-24 — Decisión de elegibilidad definitiva: estudiante de pregrado residente en Cuba

El usuario confirmó que reside actualmente en Cuba y cursa estudios de pregrado. Se filtraron alternativas según residencia real, condiciones contractuales y elegibilidad académica; no se infirió elegibilidad por nacionalidad únicamente.

### Conclusión operativa
No hay actualmente un proveedor de GPU gratuita de entrenamiento prolongado cuya elegibilidad y acceso estén confirmados para este usuario desde Cuba. No se debe seguir con Lightning AI ni Paperspace, ni intentar eludir restricciones geográficas.

### Proveedores
- **Lightning AI: DESCARTAR.** Sus términos exigen declarar que el usuario no está ubicado en país sujeto a embargo estadounidense o designado como patrocinador del terrorismo. Cuba está en la lista estadounidense. Fuente: https://lightning.ai/legal/terms-and-conditions/
- **DigitalOcean/Paperspace: DESCARTAR.** Los términos de DigitalOcean incluyen Cuba entre las jurisdicciones en las que el usuario no puede estar ubicado. Fuente: https://www.digitalocean.com/legal/terms-of-service-agreement-october-2025
- **Google Colab Free: MANTENER COMO PRIMERA OPCIÓN TÉCNICA CONDICIONAL.** Su FAQ pública describe GPU gratuita para educación y aprendizaje automático y límites dinámicos; no se encontró una prohibición general explícita por residencia cubana en la FAQ/TOS consultados. Esto no constituye confirmación contractual individual ni garantiza GPU. El usuario ya agotó temporalmente la cuota. Fuente: https://research.google.com/colaboratory/faq.html
- **Kaggle Notebooks: MANTENER COMO SEGUNDA OPCIÓN CONDICIONAL.** La documentación oficial ofrece Tesla P100 gratuita sujeta a disponibilidad: https://www.kaggle.com/docs/notebooks. La exclusión de residentes cubanos hallada en sus términos corresponde expresamente a competencias y no debe extrapolarse a notebooks. Kaggle Staff confirma que GPU requiere verificación telefónica; el usuario ya recibió Permission denied al verificar +53. Consultar soporte oficial por método alternativo, sin falsear país, número o identidad. Fuente: https://www.kaggle.com/terms y https://www.kaggle.com/discussions/product-feedback/751699
- **Hugging Face ZeroGPU: DESCARTAR PARA ENTRENAMIENTO.** Cuenta gratuita: 5 minutos GPU diarios; insuficiente para cuatro modelos de hasta 20 épocas. Fuente: https://huggingface.co/docs/hub/main/spaces-zerogpu
- **Modal: DESCARTAR BAJO CONDICIÓN CERO TARJETA/CERO RIESGO.** Requiere método de pago para GPU y puede facturar uso.
- **Amazon SageMaker Studio Lab: DESCARTAR PARA NUEVOS USUARIOS.** No admite nuevas cuentas (hallazgo de investigación anterior).

### NSF ACCESS — no contar como elegible por ahora
- El usuario es estudiante de pregrado, reside en Cuba y no ha informado afiliación académica estadounidense.
- La política ACCESS actual exige afiliación organizacional y correo institucional coincidente. Estudiantes de pregrado no pueden liderar asignaciones; pueden trabajar bajo asesor elegible. Usuarios basados fuera de EE.UU. no pueden solicitar ni liderar proyectos; pueden colaborar con PI estadounidense con justificación y aprobación. Además, los usuarios internacionales no deben aparecer ni estar afiliados a instituciones en las listas federales especificadas, incluida State Sponsors of Terrorism; Cuba figura en la lista del Departamento de Estado.
- Por tanto, si el usuario está afiliado a una universidad cubana, no se debe asumir que podrá ser añadido. No invertir esfuerzo en una solicitud hasta obtener confirmación escrita de ACCESS/Resource Provider sobre el caso concreto.
- Fuentes: https://allocations.access-ci.org/allocations-policy ; https://2021-2025.state.gov/state-sponsors-of-terrorism/

### Matiz normativo OFAC
31 CFR §515.578 autoriza ciertas categorías de servicios de Internet hacia Cuba, pero la autorización de cloud-based services está condicionada a apoyar servicios de intercambio de comunicaciones por Internet; no es una autorización general para cualquier cómputo de entrenamiento ML. No dar asesoría legal ni concluir que toda GPU cloud es automáticamente permitida/prohibida. El proveedor debe confirmar su propia elegibilidad y alcance. Fuentes: https://ofac.treasury.gov/faqs/785 ; https://www.govinfo.gov/content/pkg/CFR-2025-title31-vol3/xhtml/CFR-2025-title31-vol3-sec515-578.html

### Próximos pasos acordados
1. Mantener Colab como opción principal y reintentar GPU cuando se restablezca el acceso, sin múltiples cuentas ni mecanismos de evasión.
2. Contactar soporte Kaggle para preguntar si existe verificación oficial alternativa para número +53; no falsear datos.
3. Investigar recursos de cómputo propios de la universidad/facultad del usuario, laboratorios, grupos de investigación, profesores y convenios académicos. Es la vía académica más prometedora para obtener GPU local o acceso institucional.
4. No recomendar VPN, cuentas prestadas, identidad/número falsos, tarjetas de terceros ni plataformas cuyos términos excluyen expresamente a usuarios ubicados en Cuba.
5. No subir datasets/código privado a proveedores hasta confirmar elegibilidad.
6. No iniciar entrenamiento ni cambiar configuraciones; conservar intactas auditorías y checkpoints.

### Estado
Filtro de plataformas completado con la información disponible. No se ha habilitado GPU, creado cuenta, agregado método de pago ni ejecutado entrenamiento. Pendiente conocer universidad/facultad y si dispone de laboratorio GPU o profesor asesor.

## 2026-11-24 — Restricción de ejecución: solo teléfono Android

El usuario confirmó que no tiene acceso a computadora y dispone únicamente de su teléfono. Preguntó si se pueden optimizar los códigos para trabajar con recursos limitados.

### Decisión técnica y límites
- Sí se puede preparar un perfil ligero para inspección de datos, validaciones pequeñas, pruebas unitarias compatibles, visualización de métricas y eventualmente inferencia optimizada.
- No se puede prometer entrenamiento completo y científicamente comparable de los cuatro modelos (DeepLabV3+ y Mask R-CNN en A2D2/UrbanSyn) directamente en Android. La notebook actual exige CUDA y se detiene si no hay GPU NVIDIA; Android no proporciona CUDA.
- Entrenar en CPU móvil con PyTorch/torchvision sería extremadamente lento, limitado por RAM, temperatura y almacenamiento. Además, operaciones de torchvision usadas por Mask R-CNN pueden no estar disponibles o ser difíciles de instalar en Android.
- ONNX Runtime móvil podría servir para inferencia si los modelos se exportan correctamente, pero no sustituye el entrenamiento.
- No reducir resolución, muestras, épocas, clases ni cambiar optimizadores del protocolo principal sin aprobación; cualquier perfil reducido debe identificarse como piloto exploratorio y no mezclarse con resultados oficiales.
- No pedir descarga de datasets completos al teléfono. Usar muestras sintéticas/de prueba pequeñas o acceso remoto solo si vuelve a existir un entorno autorizado.

### Estado de implementación
- En esta intervención se revisaron el registro, `notebooks/urban_v1_entrenamiento_completo_kaggle.ipynb`, `configs/urban_experiment_v1.json` y `docs/PROTOCOLO_EXPERIMENTAL.md`.
- La notebook de entrenamiento está diseñada para Kaggle, exige CUDA, recupera metadatos/datos en el entorno remoto y persiste resultados en `/kaggle/working`; no es ejecutable tal cual en Android.
- La configuración principal mantiene imágenes 512×512, cuatro experimentos y hasta 20 épocas. No se modificó.
- No se modificó código, configuración, datasets ni checkpoints; no se ejecutó entrenamiento ni se generaron resultados.

### Próximo paso
Solicitar el modelo exacto del teléfono y su RAM/espacio libre para determinar qué pruebas locales son realistas. Después, diseñar un perfil Android separado y no destructivo (diagnóstico, tests ligeros e inferencia si es compatible), manteniendo intacto el protocolo experimental y dejando explícito que el entrenamiento completo queda bloqueado hasta disponer de cómputo adecuado.

## 2026-11-24 — Identificación del dispositivo Android

El usuario proporcionó captura de “Acerca del dispositivo” e identificó el teléfono como **OnePlus Nord N200 5G**, modelo **DE2118**.
- Captura: Qualcomm Snapdragon octa-core, 4.00 GB RAM, Android 12, OxygenOS; versión de software DE2118_11_C.37.
- La ficha oficial de OnePlus para Nord N200 especifica Snapdragon 480 5G, GPU Adreno 619, 4 GB LPDDR4x y almacenamiento UFS 2.1 de 64 GB. Fuente: https://www.oneplus.com/us/n200-5g/specs
- Evaluación: el dispositivo permite tareas ligeras de desarrollo, validación de muestras pequeñas y posible inferencia optimizada; no es una plataforma realista para entrenar los cuatro experimentos DeepLabV3+/Mask R-CNN completos. No dispone de CUDA NVIDIA y solo tiene 4 GB de RAM.
- No se ha instalado software, modificado código/configuración, descargado datasets ni ejecutado entrenamiento.
- Próximo paso: diseñar un entorno Android de bajo consumo y no destructivo, empezando por comprobar almacenamiento libre y compatibilidad de herramientas; mantener separado cualquier piloto móvil del protocolo experimental oficial.


## 2026-11-24 — Espacio disponible confirmado en Android

- El usuario confirmó que su OnePlus Nord N200 5G (4 GB RAM, 64 GB almacenamiento) tiene **15 GB libres**.
- Decisión: se puede proceder con una instalación mínima de Termux y herramientas básicas (Python/Git) para scripts ligeros, validación de muestras pequeñas y gestión del repositorio; no instalar PyTorch completo ni descargar datasets por ahora.
- La documentación oficial de Termux recomienda obtenerlo desde F-Droid o GitHub oficial y advierte que Android 12+ puede terminar procesos por límites de procesos/CPU. Instalación debe proceder solo desde una fuente oficial y sin mezclar firmas de distribución. Fuente: https://github.com/termux/termux-app
- El APK/entorno base indicado por los mantenedores ocupa aproximadamente 120–180 MB, según distribución/arquitectura; paquetes adicionales requerirán espacio extra. No se ha instalado todavía.
- Próximo paso: guiar al usuario para instalar Termux desde una fuente oficial, abrirlo y ejecutar actualizaciones básicas. Después comprobar arquitectura/entorno y añadir Python, Git y Pillow de forma gradual. Mantener intactos los experimentos principales; no entrenar los cuatro modelos en el teléfono.


## 2026-11-24 — Instalación de Termux en Android

- El usuario confirmó que ya tiene Termux instalado en su OnePlus Nord N200 5G.
- Próximo paso guiado: actualizar los índices y paquetes base con `pkg update && pkg upgrade`, aceptando la confirmación si aparece.
- Aún no se han instalado Python, Git, Pillow ni bibliotecas de aprendizaje profundo; tampoco se han descargado datasets.
- Se mantiene el enfoque de instalación gradual y ligera, verificando la salida de cada paso antes de continuar.


## 2026-11-24 — Error al actualizar Termux

- El usuario ejecutó `pkg install && pkg upgrade` (el comando previsto era `pkg update && pkg upgrade`). La actualización de índices se completó y detectó 153 paquetes actualizables.
- La configuración de paquetes falló en el script postinstalación de `xdg-utils`: la instalación auxiliar de Perl `File::MimeInfo` terminó con `/data/data/com.termux/files/usr/bin/sh: 0: Illegal option -d` y `make: *** No targets specified and no makefile found`.
- Quedaron sin configurar dependencias posteriores: Qt6, OpenCV y paquetes Python OpenCV. Se observan repositorios adicionales `tur.kcubeterm.com` y `hope2333.github.io`, además de los repositorios oficiales de Termux; todavía no se ha determinado si están relacionados con el fallo.
- Medida preventiva: detener instalaciones/actualizaciones y no eliminar paquetes. Próximo paso: inspeccionar el script postinstalación de `xdg-utils`, los archivos de fuentes APT y el estado de `dpkg` antes de reparar.
