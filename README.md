# Nuria Calvo · English Apps

Portal web donde se recogen, organizadas por temas y cursos, las aplicaciones
educativas de inglés que voy publicando en GitHub.

| Fichero | Para qué sirve |
|---|---|
| `landing.html` | La página del portal. No hace falta tocarla nunca. |
| `apps.json` | **El catálogo.** Aquí se decide qué apps se ven y en qué orden. |
| `index.html` | La app *Present Tenses* (la de siempre, no se ha modificado). |

Dirección del portal: `https://nuriacalvo-teacher.github.io/present-tenses/landing.html`

---

## Añadir una app nueva (sin tocar código)

Cada vez que subas una app nueva a GitHub:

1. Abre el portal y pulsa el botón **⚙️ Profesora** (arriba a la derecha).
2. Escribe la contraseña (por defecto: `nuria123`).
3. Ve a la pestaña **Repositorios de GitHub** y pulsa **Cargar mis repositorios**.
   Aparecerán *todos* tus repositorios, incluidos los que no tienen nada que ver con inglés.
4. Marca **solo** los que quieras publicar y pulsa **Añadir seleccionados al catálogo**.
5. En la pestaña **Mis apps**, pulsa el lápiz ✏️ de cada app nueva para ponerle
   título, descripción, curso, tema, color e icono.
6. Ve a **Publicar cambios** → **Descargar apps.json**.
7. Sube ese fichero a GitHub: entra en `apps.json` en el repositorio, pulsa el
   lápiz ✏️, borra todo, pega el contenido nuevo y pulsa **Commit changes**.

En un minuto la web muestra los cambios al alumnado.

> **Importante:** lo que editas en el panel se guarda solo en tu navegador hasta
> que subes el `apps.json` a GitHub. Mientras tanto verás abajo el aviso
> *«Vista previa local sin publicar»*: nadie más ve esos cambios.

## Las cosas del día a día

- **Ocultar o mostrar una app:** el interruptor de la izquierda en «Mis apps».
  Las apps ocultas siguen en el catálogo, pero no las ve nadie.
- **Cambiar el orden:** las flechas ↑ ↓. Ese es el orden que ve el alumnado con
  la opción *«Orden de la profesora»*.
- **Destacar en la portada:** la estrella ★. Las destacadas salen arriba del todo.
- **Marcar como «Próximamente»:** en el lápiz ✏️, campo *Estado*. La app aparece
  anunciada pero sin enlace, hasta que la termines.
- **Cambiar tu nombre, centro o el texto de portada:** pestaña *Portada y perfil*.

## En clase

- El botón **QR** de cada tarjeta abre un código QR grande para proyectar: el
  alumnado lo escanea con el móvil y entra directamente a la app.
- **Imprimir listado** (al final de la página) saca en papel todas las apps con
  sus direcciones.
- El portal se ve en **modo claro u oscuro** (botón ☀️/🌙); el modo claro va mejor
  en proyectores con mucha luz ambiente.
- Atajo: la tecla `/` lleva directamente al buscador.

---

## Detalles técnicos

- Una sola página, sin instalación, sin servidor y sin base de datos: el portal
  lee `apps.json` y lo pinta.
- Si `apps.json` no se puede leer (por ejemplo al abrir el fichero desde el disco
  con doble clic), la página usa una copia de seguridad del catálogo que lleva
  incrustada, así nunca se ve vacía.
- El portal **no llama a la API de GitHub cuando entra el alumnado**: eso se hace
  solo dentro del panel de profesora. Si lo hiciera en cada visita, un aula
  entera compartiendo la misma conexión agotaría el límite de peticiones de
  GitHub y la página fallaría.
- Campos de cada app en `apps.json`: `title`, `subtitle`, `description`,
  `category`, `levels`, `tags`, `icon`, `accent`, `status` (`live` / `beta` /
  `soon`), `featured`, `visible`, `url`, `repo`, `updated`.

### Cambiar la contraseña del panel

En `landing.html`, busca la línea:

```js
const TEACHER_KEY = 'nuria123';
```

y cambia el texto entre comillas. Ten en cuenta que es una contraseña de
conveniencia, no de seguridad: sirve para que nadie toque el panel sin querer,
pero cualquiera que mire el código de la página puede leerla. No pasa nada,
porque el panel solo genera un fichero que luego subes tú a GitHub: nadie puede
modificar la web desde ahí.

### Convertir el portal en la página principal

Ahora mismo la dirección del repositorio abre la app *Present Tenses*. Si algún
día quieres que abra el portal:

1. Renombra `index.html` → `present-tenses.html`.
2. Renombra `landing.html` → `index.html`.
3. En `apps.json`, cambia la dirección de la app Present Tenses a
   `https://nuriacalvo-teacher.github.io/present-tenses/present-tenses.html`.

Aviso: los enlaces antiguos que hayas repartido al alumnado dejarán de llevar
directamente a la app y llevarán al portal.

### Un portal para toda tu cuenta

Si prefieres que el portal viva en `https://nuriacalvo-teacher.github.io`
(sin `/present-tenses/` detrás), crea un repositorio nuevo llamado exactamente
`nuriacalvo-teacher.github.io` y copia ahí `landing.html` (renombrado a
`index.html`) y `apps.json`. Todo lo demás funciona igual.
