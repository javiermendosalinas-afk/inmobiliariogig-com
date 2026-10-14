"""Genera inmobiliariogig.com: portada y una página por desarrollo, con datos oficiales de GIG (precios de septiembre 2026)."""
import json, os, html, urllib.parse
E = lambda s: html.escape(str(s), quote=True)
WA = "523333777337"
VIGENCIA = "Precios de lista de GIG de septiembre de 2026, sujetos a confirmación y disponibilidad."
DES = [  # (slug, nombre, tipo, desde, hasta, preventa, foto_slug)
    ("castanar", "Castañar", "Casas", 1674000, 1870000, True, "castanar"),
    ("la-arboleda", "La Arboleda", "Casas", 1921000, 2336000, False, None),
    ("haciendas-de-santa-cruz", "Haciendas de Santa Cruz", "Casas", 1905000, 2387000, True, None),
    ("albazur-casas", "Albazur", "Casas", 3074000, 3431000, True, "albazur"),
    ("abie", "ABIE", "Casas", 3643000, 4338000, False, "abie"),
    ("viande", "Viande", "Departamentos", 1735000, 2304000, True, None),
    ("sant-marti", "Sant Martí", "Departamentos", 3470000, 4462000, False, None),
    ("duo24", "DÚO24", "Departamentos", 4157000, 9263000, False, None),
    ("valle-de-las-flores", "Valle de las Flores", "Terrenos", 699000, 1845000, False, None),
    ("nabi", "NABI", "Terrenos", 951000, 1220000, False, None),
    ("senderos-de-monteverde", "Senderos de Monteverde", "Terrenos", 960000, 1600000, False, "senderos-de-monteverde"),
    ("albazur-terrenos", "Albazur", "Terrenos", 1150000, 2700000, True, "albazur"),
    ("monteza", "Monteza", "Terrenos", 1450000, 3176000, False, "monteza"),
]
GANCHO = {
 "castanar": "Tu primera casa propia, en preventa y a un precio que sí está a tu alcance.",
 "la-arboleda": "Una casa para empezar a escribir la historia de tu familia.",
 "haciendas-de-santa-cruz": "Estrena casa en preventa y asegura hoy el precio de mañana.",
 "albazur-casas": "Casas amplias en preventa para la familia que está creciendo.",
 "abie": "Más espacio para todo lo que importa: casas de GIG para vivir en grande.",
 "viande": "Tu departamento en preventa: el primer paso hacia tu independencia.",
 "sant-marti": "Departamentos para quien busca estilo, ubicación y una buena inversión.",
 "duo24": "Departamentos de 3 recámaras y más de 100 m² para vivir sin acomodarte a medias.",
 "valle-de-las-flores": "El terreno más accesible de GIG para empezar tu patrimonio.",
 "nabi": "Tu terreno propio, listo para construir cuando tú lo decidas.",
 "senderos-de-monteverde": "Construye tu casa rodeado de naturaleza, con alberca y áreas verdes.",
 "albazur-terrenos": "Terrenos en preventa: compra hoy y deja que tu patrimonio crezca.",
 "monteza": "Terrenos para construir la casa que imaginas, en un desarrollo con visión.",
}
NOTAS = {"duo24": "Departamentos de 3 recámaras con más de 100 m² desde $5,700,000 (información de GIG, agosto de 2026).",
         "monteza": "Evento especial el 22 de octubre de 2026, 7:00 pm, en Tangente Dúo: beneficio extra para el cliente solo ese día.",
         "senderos-de-monteverde": "Evento especial el 22 de octubre de 2026, 7:00 pm, en Tangente Dúo: beneficio extra para el cliente solo ese día."}
FOTOS = json.load(open("assets/desarrollos/fotos.json", encoding="utf-8")) if os.path.exists("assets/desarrollos/fotos.json") else {}
din = lambda v: "$" + f"{v:,.0f}"
def wa(txt): return f"https://wa.me/{WA}?text=" + urllib.parse.quote(txt)
def fotos_de(fs): return [f["archivo"] for f in FOTOS.get(fs, {}).get("fotos", [])] if fs else []

CSS = """:root{--azul:#0b1f3a;--rojo:#d62828;--oro:#f4b942;--papel:#f6f4ef;--gris:#5b6575;--verde:#25D366}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;background:var(--papel);color:#16202e}a{color:inherit}
.cab{background:var(--azul);color:#fff}.cab div{max-width:1150px;margin:0 auto;padding:12px 18px;display:flex;justify-content:space-between;align-items:center;gap:10px}
.cab b{font-size:20px}.cab b span{color:var(--oro)}.wa{background:var(--verde);color:#fff;font-weight:800;border-radius:999px;padding:10px 16px;text-decoration:none;white-space:nowrap}
.sello{display:inline-block;background:var(--oro);color:var(--azul);font-weight:800;border-radius:999px;padding:6px 14px;font-size:13px}
.hero{background:linear-gradient(180deg,var(--azul),#16305a);color:#fff;padding:34px 18px 44px;text-align:center}.hero h1{font-size:clamp(1.8rem,5vw,2.8rem);margin:14px 0 8px}.hero p{color:#d5deec;max-width:720px;margin:0 auto;line-height:1.6}
.ben{max-width:1150px;margin:-24px auto 0;padding:0 18px;display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.ben div{background:#fff;border-radius:16px;padding:14px;box-shadow:0 6px 18px rgba(11,31,58,.08);font-size:14px;line-height:1.45}.ben b{display:block;color:var(--azul);margin-bottom:4px}
.sec{max-width:1150px;margin:30px auto;padding:0 18px}.sec h2{color:var(--azul);margin:0 0 6px}.vig{color:var(--gris);font-size:13px;margin:0 0 14px}
.filtros{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}.filtros button{border:2px solid #dfe3ea;background:#fff;border-radius:999px;padding:8px 14px;font:inherit;font-weight:700;cursor:pointer}.filtros button.on{border-color:var(--rojo);background:#fff3f3}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}.card{background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 6px 18px rgba(11,31,58,.08);display:flex;flex-direction:column;text-decoration:none}
.card .img{aspect-ratio:16/10;background:#dfe5ee center/cover no-repeat;display:flex;align-items:flex-end}.card .img span{margin:10px;background:var(--rojo);color:#fff;font-size:12px;font-weight:800;border-radius:999px;padding:4px 10px}
.card .tx{padding:14px}.card h3{margin:0 0 4px;color:var(--azul)}.card .tipo{color:var(--gris);font-size:13px}.card .p{font-weight:800;font-size:1.15rem;margin-top:8px}
.aviso{background:#fff7e6;border:1.5px solid var(--oro);border-radius:14px;padding:12px 14px;margin:14px 0;font-weight:600}
.gal{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}.gal img{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:12px}
.cta{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0}.btn{border-radius:999px;padding:13px 20px;font-weight:800;text-decoration:none}.b2{background:var(--azul);color:#fff}
footer{text-align:center;color:var(--gris);font-size:13px;padding:26px 18px 40px;line-height:1.6}
@media(max-width:760px){.ben{grid-template-columns:1fr 1fr}}"""
def pag(titulo, desc, cuerpo, raiz=""):
    return f"""<!DOCTYPE html><html lang="es-MX"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(titulo)}</title><meta name="description" content="{E(desc)}"><meta name="robots" content="noindex">
<style>{CSS}</style></head><body>
<header class="cab"><div><b>Desarrollos <span>GIG</span> · Acierta Max</b><a class="wa" href="{wa('Hola, vengo de inmobiliariogig.com y quiero información')}" target="_blank" rel="noopener">WhatsApp</a></div></header>
{cuerpo}
<footer><b>Acierta Max, S.A. de C.V. · Inmobiliaria autorizada para la comercialización de desarrollos de GIG.</b> GIG es marca de su titular; cifras de trayectoria según información publicada por GIG.<br>
Mismo precio y condiciones que con el desarrollador; la asesoría no tiene costo para ti. Profesionales inmobiliarios, miembros de AMPI y NAR.<br>
{E(VIGENCIA)} Imágenes y renders proporcionados por GIG; pueden ser ilustrativos.<br>
Atención 24 h por WhatsApp · asesores todos los días de 9:00 a 19:00 · <a href="https://acierta.pro">acierta.pro</a></footer></body></html>"""

def main():
    cards = []
    for s, n, t, d, h, pre, fs in DES:
        fotos = fotos_de(fs)
        bg = f"style=\"background-image:url('{fotos[0]}')\"" if fotos else ""
        cards.append(f'<a class="card" data-t="{t}" href="desarrollos/{s}.html"><div class="img" {bg}>{"<span>Preventa</span>" if pre else ""}</div>'
                     f'<div class="tx"><h3>{E(n)}</h3><div class="tipo">{t}</div><div class="p">{din(d)} – {din(h)}</div></div></a>')
        gal = "".join(f'<img src="../{f}" alt="{E(n)}, foto oficial {i+1}" loading="lazy">' for i, f in enumerate(fotos)) or "<p class='vig'>Fotos y renders: pide la presentación completa por WhatsApp.</p>"
        cuerpo = (f'<section class="hero"><span class="sello">✅ ACIERTA MAX · INMOBILIARIA AUTORIZADA GIG</span><h1>{E(n)}</h1>'
                  f'<p style="font-size:1.25rem;color:#fff;max-width:36em;margin:10px auto 6px">{E(GANCHO.get(s, ""))}</p><p>{t} {"en preventa " if pre else ""}de GIG · desde {din(d)} hasta {din(h)}</p></section><section class="sec">'
                  + (f'<div class="aviso">📌 {E(NOTAS[s])}</div>' if s in NOTAS else "")
                  + f'<p class="vig">{E(VIGENCIA)}</p><div class="cta"><a class="wa btn" href="{wa(f"Hola, vengo de inmobiliariogig.com. Me interesa {n} ({t}). Quiero información y agendar visita")}" target="_blank" rel="noopener">Quiero información de {E(n)}</a>'
                  f'<a class="btn b2" href="{wa(f"Hola, vengo de inmobiliariogig.com. Quiero calcular mi crédito o Infonavit para {n}")}" target="_blank" rel="noopener">Calcular mi crédito</a></div>'
                  f'<h2>Galería oficial</h2><div class="gal">{gal}</div>'
                  '<div class="aviso" style="margin-top:28px;background:#fff;border-color:#dfe3ea"><b>¿Por qué comprar con GIG?</b> Según GIG, son más de 40 años desarrollando en el occidente del país, más de 100 desarrollos y más de 150,000 viviendas entregadas. '
                  'Y con Acierta Max, inmobiliaria autorizada, pagas el mismo precio que con el desarrollador y recibes asesoría, comparativo y cálculo de crédito sin costo.</div>'
                  f'<p style="margin-top:18px"><a href="../index.html">← Ver todos los desarrollos</a></p></section>')
        open(f"desarrollos/{s}.html", "w", encoding="utf-8").write(pag(f"{n} · {t} de GIG · Acierta Max", f"{n}: {t} de GIG desde {din(d)}. Acierta Max, inmobiliaria autorizada.", cuerpo))
    cuerpo = ('<section class="hero"><span class="sello">✅ ACIERTA MAX · INMOBILIARIA AUTORIZADA</span><h1>Tu próximo hogar, con quien ha entregado más de 150,000</h1>'
              '<p>Casas, departamentos y terrenos de GIG en la Zona Metropolitana de Guadalajara, desde $699,000. Elige el tuyo con información oficial y con alguien que te acompañe en cada paso.</p></section>'
              '<section class="ben"><div><b>💰 Mismo precio</b>Precios y condiciones oficiales de GIG, sin sobreprecio.</div><div><b>🏦 Crédito e Infonavit</b>Te calculamos tu crédito sin costo.</div>'
              '<div><b>⚖️ Comparativo</b>Comparamos desarrollos para que elijas con datos.</div><div><b>✅ Acierta Verifica</b>Revisión física y documental antes de firmar.</div></section>'
              '<section class="sec" id="gig"><h2>Más de 40 años construyendo patrimonio en Jalisco</h2>'
              '<p class="vig" style="font-size:1.05rem;max-width:46em">Cuando compras una casa, también eliges en quién confiar. GIG es una empresa jalisciense fundada en 1978, parte de Grupo Empresarial G. Según la propia empresa, ha desarrollado más de 100 proyectos y entregado más de 150,000 viviendas, entre ellos desarrollos que hoy son referencia en la ciudad, como Valle Real y Jardín Real.</p>'
              '<div class="ben" style="margin:18px 0 0;padding:0"><div><b>1978</b>Año de fundación, en Jalisco</div><div><b>+100</b>desarrollos, según GIG</div><div><b>+150,000</b>viviendas entregadas, según GIG</div><div><b>Valle Real</b>y Jardín Real, entre sus proyectos</div></div></section>'
              f'<section class="sec"><h2>¿Qué estás buscando?</h2><p class="vig">{E(VIGENCIA)}</p>'
              '<div class="filtros"><button class="on" data-f="">Todos</button><button data-f="Casas">Casas</button><button data-f="Departamentos">Departamentos</button><button data-f="Terrenos">Terrenos</button></div>'
              f'<div class="grid">{"".join(cards)}</div></section>'
              '<script>document.querySelectorAll(".filtros button").forEach(b=>b.onclick=()=>{document.querySelectorAll(".filtros button").forEach(x=>x.classList.toggle("on",x===b));'
              'document.querySelectorAll(".card").forEach(c=>c.style.display=(!b.dataset.f||c.dataset.t===b.dataset.f)?"":"none");});</script>')
    open("index.html", "w", encoding="utf-8").write(pag("Desarrollos GIG en Guadalajara · Acierta Max, inmobiliaria autorizada",
         "Casas, departamentos y terrenos de GIG en Guadalajara con Acierta Max, inmobiliaria autorizada: mismo precio, asesoría y crédito sin costo.", cuerpo))
    print(f"Sitio generado: portada + {len(DES)} desarrollos")


if __name__ == "__main__":
    main()
