"""Recorre gig.mx (y los sitios propios de cada desarrollo) para traer fotos, ubicación y datos de cada desarrollo GIG que comercializamos."""
import io, json, os, re, html, urllib.request, urllib.parse, unicodedata
from PIL import Image, ImageOps
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
NOMBRES = {"castanar": ["castanar", "castañar"], "la-arboleda": ["arboleda"], "haciendas-de-santa-cruz": ["haciendas de santa cruz", "santa-cruz", "haciendas"],
  "albazur": ["albazur"], "abie": ["abie"], "viande": ["viande"], "sant-marti": ["sant marti", "santmarti", "sant-marti"], "duo24": ["duo24", "duo 24", "dúo24", "duo-24"],
  "valle-de-las-flores": ["valle de las flores", "flores"], "nabi": ["nabi"], "senderos-de-monteverde": ["monteverde", "senderos"], "monteza": ["monteza"]}
def get(u, b=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
    return r if b else r.decode("utf-8", "ignore")
norm = lambda s: unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
os.makedirs("datos/oficial", exist_ok=True)
vistos, cola, paginas = set(), ["https://gig.mx/", "https://gig.mx/desarrollos", "https://gig.mx/proyectos"], {}
while cola and len(vistos) < 60:
    u = cola.pop(0)
    if u in vistos: continue
    vistos.add(u)
    try:
        h = get(u)
    except Exception as e:
        print("no disponible:", u, type(e).__name__); continue
    for href in re.findall(r'href="([^"]+)"', h):
        v = urllib.parse.urljoin(u, href).split("#")[0]
        n = norm(v)
        if re.search(r"\.(pdf|jpe?g|png|webp|svg|css|js)$", n) or "whatsapp" in n or "facebook" in n or "instagram" in n:
            continue
        for slug, al in NOMBRES.items():
            if slug not in paginas and any(norm(a).replace(" ", "") in n.replace("-", "").replace("_", "") for a in al):
                paginas[slug] = v
        if "gig.mx" in urllib.parse.urlparse(v).netloc and v not in vistos and len(cola) < 80 and re.search(r"desarroll|proyect|residencial|vivienda|casas|departament|terreno", n):
            cola.append(v)
print("Páginas:", json.dumps(paginas, ensure_ascii=False, indent=1))
for slug, u in paginas.items():
    try:
        h = get(u)
        dom = urllib.parse.urlparse(u).netloc
        for href in re.findall(r'href="([^"#]+)"', h)[:150]:
            v = urllib.parse.urljoin(u, href)
            if urllib.parse.urlparse(v).netloc == dom and v != u and re.search(r"galer|amenid|modelo|prototip|casa|depa|terreno|lote|ubicac", v, re.I) and not re.search(r"\.(pdf|jpe?g|png|webp)$", v, re.I):
                try: h += get(v)
                except Exception: pass
        texto = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " | ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", h, flags=re.S))))
        datos = sorted(set(m.strip(" |") for m in re.findall(r"[^|]{0,90}(?:m²|m2|rec[aá]mara|baño|cajon|estacionamiento|alberca|casa club|gimnasio|roof|terraza|amenidad|asador|parque|seguridad|acceso|lote|preventa|entrega|ubicad|minutos)[^|]{0,90}", texto, re.I) if 8 < len(m.strip(" |")) < 180))
        geo = re.search(r"(?:@|q=|ll=|!3d)(-?\d{2}\.\d+)[,!4d]+(-?\d{2,3}\.\d+)", h)
        imgs = []
        for src in re.findall(r'(?:src|data-src|href|data-bg)="([^"]+\.(?:jpe?g|png|webp)[^"]*)"', h, re.I) + re.findall(r"url\(['\"]?([^)'\"]+\.(?:jpe?g|png|webp))", h, re.I):
            s = urllib.parse.urljoin(u, src.split(" ")[0])
            if s not in imgs and not re.search(r"logo|icon|favicon|sprite", s, re.I): imgs.append(s)
        os.makedirs(f"fotos-web/{slug}", exist_ok=True)
        for f in os.listdir(f"fotos-web/{slug}"): os.remove(f"fotos-web/{slug}/{f}")
        n = 0
        for s in imgs[:45]:
            try:
                im = ImageOps.exif_transpose(Image.open(io.BytesIO(get(s, True)))).convert("RGB")
                if im.width * im.height < 300_000: continue
                im.thumbnail((1600, 1600)); n += 1; im.save(f"fotos-web/{slug}/{n:02d}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
                if n >= 14: break
            except Exception: pass
        json.dump({"url": u, "datos": datos[:90], "geo": [float(geo.group(1)), float(geo.group(2))] if geo else None, "imagenes": len(imgs), "guardadas": n}, open(f"datos/oficial/{slug}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{slug}: {n} fotos de {len(imgs)}; {len(datos)} datos; geo {'sí' if geo else 'no'}")
    except Exception as e:
        print(slug, "error", type(e).__name__, str(e)[:100])
