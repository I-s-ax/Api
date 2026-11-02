from fastapi import FastAPI
import yt_dlp

app = FastAPI()

@app.get("/")
def inicio():
    return {"mensaje": "API de Descargas Activa. Usa la ruta /api/extraer?url=..."}

@app.get("/api/extraer")
def extraer_enlaces(url: str):
    opciones = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        # --- NUEVAS REGLAS ANTI-BLOQUEO ---
        'impersonate': 'chrome', # Imita a Google Chrome (requiere curl_cffi)
        'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'es-MX,es;q=0.9,en-US;q=0.8,en;q=0.7'
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
        return {"estado": "error", "mensaje": str(e)}
