LA ESCALERA DEL LIDERAZGO — VERSIÓN ONLINE

Esta versión permite que la PC de escritorio (por cable Ethernet) muestre el tablero y que una tablet Android controle el juego desde Chrome, incluso si están en redes distintas.

IMPORTANTE
- Para publicarlo hace falta una cuenta de GitHub y una cuenta de Render (ambas tienen opciones gratuitas).
- El sitio será accesible por internet. Compartí el enlace de control únicamente con quien coordine el juego.
- La versión gratuita de Render puede dormir tras 15 minutos sin actividad. Al abrirlo por primera vez puede tardar alrededor de un minuto.
- El juego guarda la partida en memoria del servidor. Si el servicio se reinicia, se reinicia la partida; por eso conviene publicarlo y probarlo antes del día de la actividad.

PASO 1 — SUBIR LOS ARCHIVOS A GITHUB
1. Entrá a https://github.com y creá una cuenta o iniciá sesión.
2. Creá un repositorio nuevo, por ejemplo: escalera-del-liderazgo
3. Elegí que sea PUBLIC (Render necesita poder acceder al repositorio si se conecta como repo público).
4. En el repositorio, elegí Add file > Upload files.
5. Descomprimí el ZIP de este juego en tu PC.
6. Subí los archivos de la carpeta del juego (index.html, app.py, server.py, requirements.txt, render.yaml, etc.). Subí los archivos, no la carpeta ZIP.
7. Confirmá con Commit changes.

PASO 2 — PUBLICAR EN RENDER
1. Entrá a https://render.com y creá una cuenta o iniciá sesión.
2. En el panel, elegí New > Blueprint.
3. Conectá GitHub y seleccioná el repositorio escalera-del-liderazgo.
4. Render detectará render.yaml y mostrará el servicio.
5. Revisá que el plan sea Free y confirmá el despliegue.
6. Esperá que el estado figure como Live.
7. En el servicio de Render, entrá a Environment y agregá la variable CONTROL_PIN. Elegí un PIN de 6 dígitos para el control y guardalo. Render puede hacer un redeploy automático; esperá nuevamente a que figure Live.
8. Render te dará una dirección parecida a:
   https://escalera-del-liderazgo.onrender.com
   (la dirección exacta la asigna Render; no la inventes ni la uses hasta verla en el panel).

PASO 3 — ABRIR EL JUEGO
En la PC de escritorio:
- Abrí Chrome y entrá a la dirección exacta que te dio Render.
- Presioná F11 para pantalla completa.

En la tablet Android:
- Abrí Chrome y entrá a la misma dirección agregando al final:
  /?mode=controller
  Ejemplo: https://TU-SITIO.onrender.com/?mode=controller

La tablet te va a pedir el PIN que configuraste en Render. No lo compartas junto con el enlace.

La PC muestra el tablero y la pregunta. La tablet permite agregar equipos, elegir equipo, sacar preguntas y marcar la respuesta. La guía de respuesta correcta/incorrecta aparece solo en la tablet, no en la pantalla proyectada.

PRUEBA ANTES DEL EVENTO
1. Abrí primero la dirección en la PC y esperá que cargue.
2. Abrí el enlace de control en la tablet.
3. Agregá un equipo y sacá una pregunta.
4. Verificá que la pregunta aparezca en la PC y la guía en la tablet.
5. Marcá correcto y confirmá que el equipo avance.

Si Render muestra un error de despliegue, revisá la pestaña Logs del servicio. No compartas contraseñas ni claves privadas.
