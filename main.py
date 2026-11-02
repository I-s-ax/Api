from fastapi import FastAPI
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de Descargas Híbrida Activa."}

@app.get("/api/extraer")
def extraer_enlaces(url: str):
    # Disfraz para engañar a los bloqueos (Cabeceras de Chrome)
    cabeceras_falsas = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }

    # --- SISTEMA 1: RUTA PARA TIKTOK ---
    if "tiktok.com" in url.lower():
        try:
            # Hacemos la petición pero le pegamos el disfraz de Chrome
            peticion = requests.get(f"https://www.tikwm.com/api/?url={url}", headers=cabeceras_falsas)
            
            # Intentamos convertir la respuesta a JSON
            try:
                respuesta = peticion.json()
            except Exception:
                # Si falla (ej. Cloudflare nos bloqueó), mostramos el texto real de la página
                return {"estado": "error", "mensaje": f"TikWM bloqueó la conexión. Código {peticion.status_code}. Respuesta: {peticion.text[:200]}"}
            
            if respuesta.get("code") == 0:
                datos = respuesta.get("data", {})
                return {
                    "estado": "exito",
                    "datos": {
                        "titulo": datos.get("title", "Video de TikTok"),
                        "enlace_video_directo": datos.get("play"),
                        "enlace_miniatura": datos.get("cover")
                    }
                }
            else:
                return {"estado": "error", "mensaje": f"TikWM rechazó el video. Motivo: {respuesta.get('msg')}"}
        except Exception as e:
            return {"estado": "error", "mensaje": f"Fallo al conectar con TikWM: {repr(e)}"}

    # --- SISTEMA 2: RUTA PARA FACEBOOK, IG, X, YOUTUBE ---
    opciones = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'impersonate': 'chrome',
        'http_headers': cabeceras_falsas
    }
    
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "estado": "exito",
                "datos": {
                    "titulo": info.get('title', 'Sin titulo'),
                    "enlace_video_directo": info.get('url'),
                    "enlace_miniatura": info.get('thumbnail')
                }
            }
    except Exception as e:
        return {"estado": "error", "mensaje": repr(e)}
