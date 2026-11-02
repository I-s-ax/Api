from fastapi import FastAPI
import yt_dlp
from curl_cffi import requests as curl_requests

app = FastAPI()


def cabeceras_navegador():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "Referer": "https://www.tiktok.com/",
        "Origin": "https://www.tiktok.com",
    }


def resolver_tiktok(url: str):
    try:
        sesion = curl_requests.Session()
        sesion.headers.update(cabeceras_navegador())

        respuesta = sesion.get(
            "https://www.tikwm.com/api/",
            params={"url": url},
            impersonate="chrome",
            timeout=20,
        )

        if respuesta.status_code != 200:
            return {
                "estado": "error",
                "mensaje": f"TikWM respondió status {respuesta.status_code}",
            }

        try:
            datos = respuesta.json()
        except Exception:
            return {
                "estado": "error",
                "mensaje": f"TikWM devolvió un contenido no JSON. Respuesta: {respuesta.text[:250]}",
            }

        if datos.get("code") == 0:
            data = datos.get("data", {})
            return {
                "estado": "exito",
                "datos": {
                    "titulo": data.get("title", "Video de TikTok"),
                    "enlace_video_directo": data.get("play"),
                    "enlace_miniatura": data.get("cover"),
                },
            }

        return {
            "estado": "error",
            "mensaje": datos.get("msg", "TikWM rechazó la URL"),
        }

    except Exception as e:
        return {
            "estado": "error",
            "mensaje": f"Fallo al conectar con TikWM usando curl_cffi: {repr(e)}",
        }


def resolver_yt_dlp(url: str):
    opciones = {
        "format": "best",
        "quiet": True,
        "noplaylist": True,
        "skip_download": True,
        "http_headers": cabeceras_navegador(),
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "estado": "exito",
                "datos": {
                    "titulo": info.get("title", "Sin titulo"),
                    "enlace_video_directo": info.get("url"),
                    "enlace_miniatura": info.get("thumbnail"),
                },
            }
    except Exception as e:
        return {
            "estado": "error",
            "mensaje": repr(e),
        }


@app.get("/")
def inicio():
    return {"mensaje": "API de Descargas Híbrida Activa."}


@app.get("/api/extraer")
def extraer_enlaces(url: str):
    if not url:
        return {"estado": "error", "mensaje": "Debes enviar una URL válida."}

    url_limpia = url.strip()

    if "tiktok.com" in url_limpia.lower() or "vm.tiktok.com" in url_limpia.lower():
        resultado = resolver_tiktok(url_limpia)
        if resultado.get("estado") == "exito":
            return resultado

        # Fallback: si TikWM falla, intentamos yt-dlp con navegador
        fallback = resolver_yt_dlp(url_limpia)
        if fallback.get("estado") == "exito":
            return fallback

        return {
            "estado": "error",
            "mensaje": resultado.get("mensaje", "No se pudo extraer el video de TikTok."),
            "fallback": fallback.get("mensaje"),
        }

    return resolver_yt_dlp(url_limpia)
