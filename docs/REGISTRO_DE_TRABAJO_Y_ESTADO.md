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
