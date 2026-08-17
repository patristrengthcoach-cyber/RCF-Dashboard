# Readaptación de Lesiones · Racing Club Ferrol

**Área de Rendimiento y Salud Integral del Deportista · Cantera RCF**

Panel web para diseñar sesiones de readaptación (gimnasio y, si procede, bloque de campo) y para llevar el seguimiento global de los jugadores de baja de la cantera, con el mismo lenguaje visual que el **Protocolo Preventivo**, y con los parámetros de carga que ya se usaban en los libros Excel (`Diseño de Sesión de Readaptación` y `Seguimiento Individual de Readaptación`) y en el informe semanal de seguimiento.

No sustituye el criterio médico ni fisioterapéutico. Es una herramienta de apoyo para el diseño y registro de sesiones y para la trazabilidad de fases; las decisiones clínicas son siempre del cuerpo médico.

## Qué incluye

### Diseño de sesión
- **Filtro global de jugador**: en la parte superior de la página (visible en todas las pestañas) hay un selector con los jugadores de baja actuales (nombre + ID + categoría, tomados de la pestaña de seguimiento). Elegir uno filtra automáticamente el diseño de sesión, la ficha, el registro de carga y el seguimiento por ese jugador; no hace falta volver a escribir su ID en cada pestaña.
- **Banco de ejercicios** (pestaña **Diseño de sesión**) organizado en 4 bloques — Calentamiento/activación, Bloque principal · Gimnasio, Bloque principal · Campo, Vuelta a la calma — filtrado automáticamente por la **fase RTP** seleccionada (Fase 1 Aproximación → Fase 7 Optimización individual). Cada ejercicio es una tarjeta editable con material, series, repeticiones, carga/intensidad, RPE, descanso, notas/precauciones, y **vídeo (YouTube) y/o imagen/GIF propios** (se puede subir una foto del ejercicio igual que en el Excel). Se pueden añadir ejercicios propios.
- **Selector de ubicación**: Solo gimnasio / Gimnasio + campo / Solo campo.
- **Títulos de cada bloque editables**: los encabezados de la ficha (Calentamiento, Gimnasio, Campo, Vuelta a la calma, Test) se pueden renombrar directamente sobre la propia ficha.
- **Imagen de la tarea de campo**: cuando la sesión incluye bloque de campo, se puede subir una imagen/diagrama de la tarea (aparece también en la ficha impresa).
- **Ficha de sesión** en formato tabla (ID · Ejercicio · Series · Repeticiones · Carga/Intensidad · RPE · Descanso · Notas), editable en línea, reordenable, con minutos por bloque, número de sesión junto a la fecha, e imprimible.
- **Bloque de TEST** al final de la sesión (Test · Lado · Resultado · Referencia basal/contralateral · % diferencia · Interpretación · Notas), con % de diferencia y alerta de asimetría (≥15%) calculados en vivo, igual que la hoja de valoraciones periódicas del Excel.
- **Resumen y carga de la sesión**: duración total, RPE de la sesión y carga (session-RPE = duración × RPE) en vivo, dolor EVA post-sesión, cumplimiento y observaciones.

### Registro y carga
- Guarda cada sesión ejecutada por jugador (incluye nº de sesión, objetivo, tests) y calcula **carga aguda (7 días)**, **carga crónica (media semanal de 4 semanas)**, **ACWR**, **monotonía** y **strain**, con el mismo criterio del Excel (ACWR 0.8–1.3 óptimo, >1.5 riesgo alto), más un mini-gráfico de carga diaria.
- El jugador se elige desde el **filtro global** de arriba; dentro de la pestaña se puede elegir además una **sesión concreta** por su número para ver su detalle completo (objetivo, observaciones, tests) sin perder la vista agregada.

### Seguimiento de lesionados (informe descargable)
- Roster de jugadores de baja con los mismos campos que el formulario **"Informe de lesiones - RCF"** (ID, nombre, categoría/equipo, fecha de lesión, diagnóstico, localización, lateralidad, tipología, mecanismo, reincidencia, contexto, severidad, pronóstico, posición, superficie, cómo se produjo). El panel viene precargado con las últimas respuestas de ese formulario (Google Sheets) como punto de partida; en cuanto se guarda cualquier cambio desde la interfaz, esos datos de ejemplo dejan de usarse y prevalece lo guardado.
- **Sincronización automática con Google Sheets, sin tocar el documento**: el roster viene ya conectado a la hoja de respuestas del formulario y se actualiza solo cada pocos minutos, sin necesidad de publicar nada ni añadir scripts. Ver *Actualización automática desde Google Sheets* más abajo.
- **Selección múltiple para el informe**: una lista de casillas permite marcar uno, varios o todos los jugadores que se quieren incluir en el informe (con botones "Todos" / "Ninguno"), independiente del filtro global de arriba. Al dar de alta un jugador nuevo (a mano o por sincronización) se marca automáticamente.
- **Fase actualizada sola**: se toma de la fase de la última sesión registrada para ese jugador (si no hay sesiones, se usa la fase inicial indicada al darlo de alta en el seguimiento).
- **Días de baja en vivo**, calculados siempre respecto a hoy.
- Tabla con el mismo formato que el informe en papel (Cat. · Jugador · Lesión · Días de baja · Fase I–V · RTP · Optimización individual), coloreada por categoría, con nota editable de objetivo/estado bajo la fase actual (con botón para traerla directamente de la última sesión registrada).
- Botón **Descargar informe** (imprime/exporta a PDF en A4 apaisado) para repartir al staff; jugadores dados de alta se pueden archivar sin perder el histórico.

### Calendario semanal de citas
- Pestaña con una vista semanal (lunes a domingo) para anotar la **hora a la que se cita a cada jugador** a su sesión de readaptación — como una agenda semanal de readaptación.
- Cada cita tiene fecha, hora, jugador (elegido del seguimiento), lugar (gimnasio / campo / gimnasio + campo / clínica-fisio), nº de sesión opcional y notas.
- Navegación semana anterior / siguiente / hoy, botón "+ cita" tanto general como por día concreto, y **Descargar semana** para imprimir/exportar la agenda en A4 apaisado.

### Memoria de sesiones
- Pestaña con un filtro **De baja / De alta** y, dentro de cada uno, una tarjeta por jugador (con el nº de sesiones que tiene guardadas) para elegir con quién trabajar.
- Al elegir un jugador, se listan **todas sus sesiones guardadas** en una tabla totalmente editable: fecha, nº de sesión, fase, objetivo, duración, RPE, dolor EVA, cumplimiento y observaciones. La carga (duración × RPE) se recalcula sola al editar duración o RPE.
- Pensada para corregir después del hecho — por ejemplo, si al guardar la sesión se apuntó mal el RPE o se te olvidó marcar "Parcial" en vez de "Completo". Cada cambio se guarda directamente sobre esa sesión.
- También permite eliminar una sesión guardada por error.

## Cómo abrirlo

No necesita instalación ni servidor: es un único archivo HTML autocontenido.

- **Directo**: descarga `index.html` y ábrelo con cualquier navegador.
- **GitHub Pages** (recomendado para uso compartido por todo el cuerpo técnico): sigue la sección *Publicar en GitHub Pages* más abajo.

## Guardado de datos: nube vs. navegador

El panel detecta automáticamente dónde se está ejecutando:

- **Dentro de Claude** (como artefacto): usa el almacenamiento compartido de Claude — todo el cuerpo técnico que abra el panel en Claude ve el mismo banco de ejercicios, el mismo roster de lesionados y el mismo registro de carga.
- **Como archivo independiente / GitHub Pages**: usa `localStorage` del navegador. Los datos (incluidas las imágenes subidas) quedan guardados **solo en ese dispositivo/navegador**, no se comparten automáticamente entre coordinadores. Si necesitáis un registro compartido de verdad en producción, hay que conectar un backend (por ejemplo, una hoja de Google Sheets vía Apps Script, Firebase, o una pequeña API) — el código está organizado para que sustituir las funciones `stGet`/`stSet` por llamadas a ese backend sea el único cambio necesario.
- Las imágenes se comprimen y redimensionan en el navegador antes de guardarse (máx. ~900–1100px, JPEG) para no exceder los límites de almacenamiento.

## Actualización automática desde Google Sheets

El panel **ya viene conectado por defecto** a la hoja de respuestas del formulario "Informe de lesiones - RCF" (la de `1oEmE3Gn91_LIJgVH3BEDBZai2Ss61g13Qrarqd6iewU`). No hace falta tocar nada en el Sheets — ni scripts, ni "Publicar en la web", ni ningún cambio en el documento: el panel simplemente lee la pestaña de respuestas aprovechando que ya está compartida como "Cualquiera con el enlace", igual que cuando se abre para consultarla a mano.

- Al abrir el panel, sincroniza automáticamente. Después, sigue comprobando cada 2 minutos mientras esté abierto, y cada vez que vuelves a esa pestaña del navegador.
- El botón 🔄 (pestaña **Seguimiento de lesionados** → "Lectura automática de Informe de lesiones - RCF") fuerza una comprobación inmediata.
- Cada jugador se identifica por su **ID (RCF_000)**: si ya existe en el seguimiento se actualiza con los últimos datos del formulario, y si es nuevo se añade automáticamente (y se marca para el informe). Los campos que gestiona el propio panel (fase, nota, si está dado de alta) no se tocan al sincronizar — solo se actualizan los que vienen del formulario.
- Internamente prueba dos enlaces de lectura de Google (uno principal y uno de respaldo) antes de avisar de un error, así que es tolerante a que uno de los dos falle puntualmente.
- Si en algún momento queréis apuntar a otra hoja (por ejemplo una copia, o el año que viene), pegad su enlace CSV en el mismo campo y pulsad Guardar — solo necesita que la hoja esté compartida como "Cualquiera con el enlace (Lector)"; si alguna vez ese enlace deja de funcionar, la alternativa sin ambigüedad es publicarla en la web (**Archivo → Compartir → Publicar en la web** → esa pestaña → CSV), que tampoco modifica el documento, solo cambia cómo se puede leer desde fuera.

Esta configuración es compartida: todo el cuerpo técnico que abra el panel (dentro de Claude, o el archivo desplegado en GitHub Pages) lee la misma hoja, sin que nadie tenga que configurar nada la primera vez.

### Opcional y avanzado: tiempo real con Firebase

Si en el futuro queréis que los cambios aparezcan al instante en lugar de cada 2 minutos, el panel incluye también (pestaña Seguimiento → "Opcional: tiempo real con Firebase") una conexión en tiempo real vía Firebase. A diferencia de todo lo anterior, **esto sí requiere añadir un pequeño script dentro del Google Sheets** (Apps Script, con un disparador "al enviar formulario") que empuje cada respuesta nueva a una base de datos Firebase, que el panel escucha en directo. Como esto modifica el documento de Sheets, se ha dejado como algo puramente opcional y desactivado por defecto — la sincronización automática de arriba no lo necesita para nada. Si en algún momento os interesa, preguntad y os paso la guía paso a paso con el script ya escrito.

## Crear el repositorio en GitHub

```bash
cd rcf-readaptacion-dashboard
git init
git add .
git commit -m "Panel de readaptación de lesiones RCF"
git branch -M main
git remote add origin https://github.com/<tu-usuario-u-organizacion>/rcf-readaptacion-dashboard.git
git push -u origin main
```

Este repositorio va a contener datos sensibles de jugadores (lesiones, seguimiento clínico) si se conecta un backend compartido — **creadlo como repositorio privado** en GitHub.

## Publicar en GitHub Pages

1. En GitHub → **Settings → Pages → Build and deployment → Source**, elegid **GitHub Actions**.
2. Hay un workflow ya incluido en `.github/workflows/deploy.yml` que publica el sitio automáticamente en cada `push` a `main`.
3. Tras el primer despliegue, la URL aparece en **Settings → Pages** (algo como `https://<usuario>.github.io/rcf-readaptacion-dashboard/`).

Alternativa manual sin Actions: **Settings → Pages → Source → Deploy from a branch → main / (root)**.

## Estructura del repositorio

```
rcf-readaptacion-dashboard/
├── index.html                    # Aplicación completa (HTML + CSS + JS, sin dependencias de build)
├── README.md
├── .gitignore
└── .github/
    └── workflows/
        └── deploy.yml             # Despliegue automático a GitHub Pages
```

## Personalizar el banco de ejercicios

El banco inicial (unos 30 ejercicios) está pensado como punto de partida, con la misma estructura que la pestaña *Banco de Ejercicios* del Excel. Para editarlo en bloque en vez de uno a uno desde la interfaz, abre `index.html` y busca el objeto `BANK` dentro del `<script>` (sección `DATOS: BANCO DE EJERCICIOS`); cada ejercicio es un objeto con:

```js
{id:'g1', n:'Nombre del ejercicio', mat:'Material', minFase:3,
 series:'3', reps:'4-6', carga:'Descripción de la carga/intensidad',
 rpe:'5', descanso:'90"', note:'Precaución opcional', ev:'Nota de criterio opcional'}
```

`minFase` (1–7) controla a partir de qué fase RTP aparece el ejercicio en el banco. Las imágenes subidas desde la interfaz se guardan como overrides (`img`, en base64) y no hace falta tocarlas aquí.

## Fórmulas utilizadas

Las mismas que en el libro Excel `Diseño de Sesión de Readaptación` (hoja *Instrucciones*) y en el protocolo de valoraciones periódicas:

- Carga de sesión (session-RPE) = Duración (min) × RPE (escala CR-10, 0–10).
- Carga aguda = suma de la carga de los últimos 7 días. Carga crónica = media semanal de las últimas 4 semanas.
- ACWR = carga aguda / carga crónica. Zona orientativa 0.8–1.3; > 1.5 asociado a mayor riesgo.
- Monotonía = carga media diaria de la semana / desviación estándar diaria. Strain = carga semanal × monotonía.
- % diferencia en tests = (resultado − referencia) / referencia. Asimetría relevante orientativa ≥ 15% (criterio de alta RTP del Excel).
- Días de baja = fecha actual − fecha de la lesión.

Es una herramienta orientativa de tendencia de carga y de seguimiento, no un predictor exacto de lesión individual ni un sustituto del criterio médico.

## Compatibilidad

Sin dependencias de build ni frameworks: HTML + CSS + JavaScript vanilla, con Google Fonts (Oswald, Inter, IBM Plex Mono) cargadas por CDN. Funciona en cualquier navegador moderno, escritorio o móvil.

