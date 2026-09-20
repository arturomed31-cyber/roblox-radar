# Worker de Roblox Radar (modo en vivo + bot de Discord)

Un solo Cloudflare Worker (plan gratis: 100.000 peticiones/día) que:

- sirve `/live?ids=…` — lecturas en vivo de Roblox para el **modo en vivo** de la página;
- responde a los **comandos de barra** de Discord en `/discord` (`/game`, `/top`, `/rising`, `/new`, `/studio`, `/help`).

## 1. Crear el Worker (5 min)

1. Panel de Cloudflare → **Workers & Pages** → **Create** → **Create Worker**.
2. Nombre: `roblox-radar` → **Deploy** (despliega el "Hello world").
3. **Edit code** → borra todo, pega el contenido de `worker/worker.js` → **Deploy**.
4. Apunta la URL: `https://roblox-radar.<tu-subdominio>.workers.dev`.
5. Prueba: abre `https://roblox-radar.<tu-subdominio>.workers.dev/live?ids=10563114921` → debe devolver JSON con `playing`.

Pásale esa URL a Claude para que la ponga en `WORKER_URL` de `index.html` (o edítala tú).

## 2. Crear el bot de Discord (5 min)

1. https://discord.com/developers/applications → **New Application** → nombre `Roblox Radar`.
2. Pestaña **General Information**: copia **Application ID** y **Public Key**.
3. Pestaña **Bot** → **Reset Token** → copia el **token** (solo se muestra una vez).
4. Pestaña **Installation** → Install Link "Discord Provided Link"; en *Default Install Settings* → Guild Install → Scopes: `applications.commands` y `bot`; Permissions: `Send Messages`, `Embed Links`. Copia el enlace de instalación, ábrelo e instálalo en tu servidor.

## 3. Poner las claves en el Worker (nunca en el chat)

Worker → **Settings** → **Variables and Secrets** → **Add**, tipo *Secret*:

| Nombre | Valor |
|---|---|
| `DISCORD_PUBLIC_KEY` | Public Key del paso 2 |
| `DISCORD_APP_ID` | Application ID |
| `DISCORD_TOKEN` | token del bot |
| `ADMIN_KEY` | una cadena larga aleatoria que inventes (protege el registro de comandos) |
| `LANG` (texto, opcional) | `es` o `en` — idioma de las respuestas del bot |

Guardar → **Deploy**.

## 4. Conectar Discord con el Worker

1. En la aplicación de Discord → **General Information** → **Interactions Endpoint URL**:
   `https://roblox-radar.<tu-subdominio>.workers.dev/discord` → **Save Changes**.
   Discord hace una prueba de firma; si el Worker tiene la Public Key correcta, guarda sin error.
2. Registra los comandos una vez abriendo en el navegador:
   `https://roblox-radar.<tu-subdominio>.workers.dev/register?key=TU_ADMIN_KEY`
   Debe devolver un JSON con la lista de comandos.
3. En tu servidor escribe `/help` — los comandos aparecen (puede tardar un minuto).

## Notas

- El bot no necesita estar "encendido": Discord llama al Worker solo cuando alguien usa un comando.
- `/game` lee jugadores en vivo de Roblox; el resto usa la última lectura de la página (cada hora).
- Si cambias el nombre del sitio o el dominio, añade el origen a `ALLOWED_ORIGINS` en `worker.js`.
