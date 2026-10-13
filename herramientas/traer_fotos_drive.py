"""Trae fotos oficiales desde una carpeta de Google Drive (ZIP por desarrollo o imágenes sueltas),
elige las mejores, las optimiza y las guarda en assets/desarrollos/<slug>/. Escribe assets/desarrollos/fotos.json."""
import io, json, os, re, sys, unicodedata, zipfile, tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from PIL import Image, ImageOps

CARPETA = os.environ["DRIVE_CARPETA"]
MAX_FOTOS = int(os.environ.get("MAX_FOTOS", "14"))
SALIDA = "assets/desarrollos"
creds = service_account.Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_CREDENTIALS"]), scopes=["https://www.googleapis.com/auth/drive.readonly"])
drive = build("drive", "v3", credentials=creds, cache_discovery=False)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"-\d{8}t\d{6}z.*$", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def bajar(fid, destino):
    req = drive.files().get_media(fileId=fid, supportsAllDrives=True)
    with open(destino, "wb") as f:
        d = MediaIoBaseDownload(f, req, chunksize=64 * 1024 * 1024)
        hecho = False
        while not hecho:
            _, hecho = d.next_chunk()


def guardar(imagenes, carpeta):
    """imagenes: lista de (nombre, bytes). Elige las de mayor resolución, sin repetir tamaño casi igual."""
    candidatas = []
    for nombre, datos in imagenes:
        try:
            im = Image.open(io.BytesIO(datos)); im.load()
            w, h = im.size
            if w * h < 400_000 or w / h > 3.2 or h / w > 3.2:
                continue
            prioridad = 0 if re.search(r"render|fachada|exterior|amenidad|alberca|club|sala|cocina|rec[aá]mara|vista|aerea|a[eé]rea", nombre, re.I) else 1
            candidatas.append((prioridad, -w * h, nombre, im))
        except Exception:
            continue
    candidatas.sort(key=lambda x: (x[0], x[1]))
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        os.remove(os.path.join(carpeta, f))
    vistos, salida = [], []
    for _, area, nombre, im in candidatas:
        # huella del contenido (dHash 8x8): descarta solo imágenes visualmente casi iguales
        g = im.convert("L").resize((9, 8))
        px = list(g.getdata())
        huella = sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
        if any(bin(huella ^ v).count("1") <= 6 for v in vistos):
            continue
        vistos.append(huella)
        im = ImageOps.exif_transpose(im).convert("RGB"); im.thumbnail((1600, 1600))
        ruta = os.path.join(carpeta, f"{len(salida) + 1:02d}.jpg")
        im.save(ruta, "JPEG", quality=78, optimize=True, progressive=True)
        salida.append({"archivo": ruta, "origen": nombre, "ancho": im.size[0], "alto": im.size[1]})
        if len(salida) >= MAX_FOTOS:
            break
    return salida


def main():
    q = f"'{CARPETA}' in parents and trashed = false"
    archivos = drive.files().list(q=q, fields="files(id,name,mimeType,size)", pageSize=200, supportsAllDrives=True, includeItemsFromAllDrives=True).execute()["files"]
    resultado = {}
    for a in archivos:
        nombre = a["name"]
        if nombre.lower().endswith(".zip"):
            s = slug(nombre[:-4])
            with tempfile.TemporaryDirectory() as tmp:
                ruta = os.path.join(tmp, "a.zip")
                print(f"Bajando {nombre} ({int(a.get('size', 0)) / 1e6:.0f} MB)…", flush=True)
                bajar(a["id"], ruta)
                imgs = []
                with zipfile.ZipFile(ruta) as z:
                    for info in z.infolist():
                        if re.search(r"\.(jpe?g|png|webp)$", info.filename, re.I) and 150_000 < info.file_size < 40_000_000 and "__MACOSX" not in info.filename:
                            imgs.append((info.filename, z.read(info)))
                fotos = guardar(imgs, os.path.join(SALIDA, s))
                resultado[s] = {"desarrollo": nombre[:-4], "fotos": fotos, "imagenes_en_zip": len(imgs)}
                print(f"  {s}: {len(fotos)} fotos de {len(imgs)} imágenes", flush=True)
    os.makedirs(SALIDA, exist_ok=True)
    json.dump(resultado, open(os.path.join(SALIDA, "fotos.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
