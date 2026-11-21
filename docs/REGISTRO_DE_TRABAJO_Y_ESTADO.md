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
- Se añadieron pruebas sintéticas `tests/test_bdd100k_instance_preflight.py` para conteo de instancia, rechazo de máscaras no RGBA y emparejamiento incompleto.
- Se actualizó `scripts/train_maskrcnn_cityscapes.py` para validar también el orden/nombre de clases del checkpoint al reanudar y corregir el mensaje de dimensiones de clase (9 salidas: fondo + 8 clases). La reanudación continúa siendo por época; no promete restaurar aleatoriedad de lotes a mitad de época.
- Se actualizó el notebook Colab para mostrar la auditoría oficial y exigir un informe `ready_for_training=true` antes de permitir `MODEL="instance"` con `RUN_TRAINING=True`. La muestra GitHub parcial no pasa por esta ruta.
- Se documentó el procedimiento en `docs/PROTOCOLO_EXPERIMENTAL.md`. Evaluación BDD100K oficial se ejecuta después del entrenamiento sobre val, con el protocolo interno de AP claramente identificado; no equivale a COCOeval.
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
