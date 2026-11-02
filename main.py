from fastapi import FastAPI
import yt_dlp
import requests

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de Descargas Híbrida Activa."}

@app.get("/api/extraer")
def extraer_enlaces(url: str):
    # --- SISTEMA 1: RUTA PARA TIKTOK ---
    if "tiktok.com" in url.lower():
        try:
            # Consultamos una API especializada en TikTok para saltar el bloqueo de IP de Render
            respuesta = requests.get(f"https://www.tikwm.com/api/?url={url}").json()
            
            if respuesta.get("code") == 0:
                datos = respuesta.get("data", {})
                return {
                    "estado": "exito",
                    "datos": {
                        "titulo": datos.get("title", "Video de TikTok"),
                        "enlace_video_directo": datos.get("play"), # MP4 sin marca de agua
                        "enlace_miniatura": datos.get("cover")
                    }
                }
            else:
                return {"estado": "error", "mensaje": "TikWM rechazó o no encontró el video."}
        except Exception as e:
            # Usamos repr() en lugar de str() para que el error nunca quede en blanco
            return {"estado": "error", "mensaje": f"Fallo al conectar con TikWM: {repr(e)}"}

    # --- SISTEMA 2: RUTA PARA FACEBOOK, IG, X, YOUTUBE ---
    opciones = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'impersonate': 'chrome',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36'
        }
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
