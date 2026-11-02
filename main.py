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
        'noplaylist': True
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
