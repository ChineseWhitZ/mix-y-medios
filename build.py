#!/usr/bin/env python3
"""Genera el sitio estático «Mix & Medios» en docs/ a partir de contenido/.

Uso:  python3 build.py
Variables opcionales: BASE_URL (URL pública del sitio, termina en /).
Solo usa la biblioteca estándar de Python.
"""
import hashlib
import html
import json
import os
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CONTENIDO = RAIZ / "contenido"
SALIDA = RAIZ / "docs"
BASE_URL = os.environ.get("BASE_URL", "https://chinesewhitz.github.io/mix-y-medios/")

SITIO = "Mix & Medios"
LEMA = "El blog de Comunicaciones de Marketing"
WHATSAPP = "https://wa.me/51966454742?text=Hola%2C%20quiero%20saber%20m%C3%A1s%20de%20IronBites"
WEB_IRONBITES = "https://sites.google.com/view/ironbites/full-page-embed"

EQUIPO = [
    ("Stefano Alessandro", "Carassa Vente"),
    ("Daniela Ross", "Francia Melendez"),
    ("Amanda Marypaz", "Rojas Campos"),
    ("Flavia Luana", "Ruiz Paredes"),
    ("Mia Zore", "Salinas Costti"),
]

CATS = {
    "fundamentos": ("Fundamentos de las CM", "Qué es comunicar, el ruido, las CIM y el mix promocional.", [1]),
    "marca": ("Gestión de marca", "Valor, identidad y posicionamiento de marca.", [2]),
    "creatividad": ("Propuesta creativa", "KPI, brief, agencias y la Big Idea.", [3]),
    "planificacion": ("Planificación CIM", "Objetivos, presupuesto, buyer persona y diferenciación.", [4]),
    "consumidor": ("Viaje del consumidor", "Necesidades, momentos de la verdad y customer journey.", [5]),
    "medios-masivos": ("Medios masivos", "Televisión, radio, prensa, revistas y publicidad exterior.", [8, 9]),
    "relaciones-publicas": ("Relaciones públicas", "Reputación, stakeholders, PENCILS e influencers.", [10]),
    "medios-alternativos": ("Medios alternativos", "Marketing directo, trade, guerrilla, promociones y CRM.", [11]),
    "digital": ("Marketing digital", "Web de marca, SEO, SEM y redes sociales.", [12, 13, 14]),
    "repaso": ("Repaso y caso", "Repasos del ciclo y el caso integrador IronBites.", [6, 15]),
}
IMG_CAT = {k: f"img/cat-{k}.jpg" for k in CATS}
IMG_CAT["repaso"] = "img/equipo.jpg"

SEMANAS = [
    (1, "Introducción a las comunicaciones de marketing"),
    (2, "Gestión de marca"),
    (3, "Propuesta creativa"),
    (4, "Planificación de las CIM"),
    (5, "Viaje del consumidor"),
    (6, "Repaso y evaluación parcial"),
    (7, "Repaso y evaluación parcial"),
    (8, "Medios masivos audiovisuales"),
    (9, "Medios masivos estáticos"),
    (10, "Relaciones públicas"),
    (11, "Medios alternativos"),
    (12, "Marketing digital y la web"),
    (13, "Motores de búsqueda: SEO y SEM"),
    (14, "Redes sociales"),
    (15, "Exposición final del trabajo integrador"),
]

e = lambda s: html.escape(str(s), quote=True)
VERSION = hashlib.md5((SALIDA / "css/estilos.css").read_bytes() + (SALIDA / "js/main.js").read_bytes()).hexdigest()[:8]


def slugify(texto):
    t = unicodedata.normalize("NFD", texto.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t[:60] or "seccion"


def sin_tildes(texto):
    t = unicodedata.normalize("NFD", texto)
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------------ contenido
def cargar_posts():
    posts = []
    for f in sorted((CONTENIDO / "posts").glob("S*.html")):
        crudo = f.read_text(encoding="utf-8")
        m = re.match(r"\s*<!--meta\s*(\{.*?\})\s*-->\s*(.*)\Z", crudo, re.S)
        if not m:
            raise SystemExit(f"{f.name}: falta el bloque <!--meta-->")
        meta = json.loads(m.group(1))
        cuerpo = m.group(2).strip()
        assert meta["categoria"] in CATS, f"{f.name}: categoría desconocida {meta['categoria']}"
        # ids en los h2 para el índice
        indice, usados = [], set()

        def poner_id(mh):
            attrs, texto = mh.group(1), mh.group(2)
            limpio = re.sub(r"<[^>]+>", "", texto)
            base = slugify(limpio)
            ident, n = base, 2
            while ident in usados:
                ident, n = f"{base}-{n}", n + 1
            usados.add(ident)
            indice.append((ident, limpio))
            return f'<h2{attrs} id="{ident}">{texto}</h2>'

        cuerpo = re.sub(r"<h2([^>]*)>(.*?)</h2>", poner_id, cuerpo, flags=re.S)
        cuerpo = re.sub(r"<table\b.*?</table>", lambda m: f'<div class="tabla">{m.group(0)}</div>', cuerpo, flags=re.S)
        palabras = len(re.sub(r"<[^>]+>", " ", cuerpo).split())
        meta.update(
            archivo=f.stem,
            cuerpo=cuerpo,
            indice=indice,
            palabras=palabras,
            minutos=max(1, round(palabras / 200)),
        )
        posts.append(meta)
    posts.sort(key=lambda p: (p["semana"], p["archivo"]))
    slugs = [p["slug"] for p in posts]
    assert len(slugs) == len(set(slugs)), "slugs repetidos"
    return posts


def cargar_glosario():
    terminos = []
    for f in sorted((CONTENIDO / "glosario").glob("S*.json")):
        terminos += json.loads(f.read_text(encoding="utf-8"))
    vistos, unicos = set(), []
    for t in terminos:
        clave = sin_tildes(t["t"].lower())
        if clave not in vistos:
            vistos.add(clave)
            unicos.append(t)
    unicos.sort(key=lambda t: sin_tildes(t["t"].lower()))
    return unicos



# ------------------------------------------------------------------ plantilla
TONO = {
    "fundamentos": "azul", "marca": "morado", "creatividad": "naranja", "planificacion": "verde",
    "consumidor": "pizarra", "medios-masivos": "azul", "relaciones-publicas": "morado",
    "medios-alternativos": "naranja", "digital": "verde", "repaso": "pizarra",
}
ABREV = {
    "fundamentos": "CM", "marca": "Ma", "creatividad": "Cr", "planificacion": "Pl", "consumidor": "Co",
    "medios-masivos": "MM", "relaciones-publicas": "RP", "medios-alternativos": "MA", "digital": "D", "repaso": "R",
}
CORTO = {
    "fundamentos": "Fundamentos", "marca": "Marca", "creatividad": "Creatividad", "planificacion": "Planificación",
    "consumidor": "Consumidor", "medios-masivos": "Medios masivos", "relaciones-publicas": "RR. PP.",
    "medios-alternativos": "Alternativos", "digital": "Digital", "repaso": "Repaso",
}

ICONO_SOL = '<svg class="sol" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
ICONO_LUNA = '<svg class="luna" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>'
ICONO_MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
ICONO_LUPA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICONO_WA = '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M16 3C9 3 3.3 8.6 3.3 15.6c0 2.2.6 4.4 1.7 6.3L3 29l7.3-1.9c1.8 1 3.8 1.5 5.8 1.5 7 0 12.7-5.6 12.7-12.6S23 3 16 3zm0 23.1c-1.9 0-3.7-.5-5.3-1.4l-.4-.2-4.3 1.1 1.2-4.2-.3-.4a10.4 10.4 0 0 1-1.6-5.5C5.3 9.8 10.1 5.1 16 5.1s10.6 4.7 10.6 10.5S21.9 26.1 16 26.1zm5.8-7.8c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2l-1 1.2c-.2.2-.4.2-.7.1a8.6 8.6 0 0 1-4.3-3.7c-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.5l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.3 5.2 4.6 1.9.8 2.7.9 3.6.7.6-.1 1.9-.8 2.1-1.5.3-.7.3-1.4.2-1.5-.1-.1-.3-.2-.6-.3z"/></svg>'

NAV = [
    ("index.html", "Inicio"),
    ("blog.html", "Blog"),
    ("categorias.html", "Categorías"),
    ("producto.html", "Producto"),
    ("glosario.html", "Glosario"),
    ("nosotros.html", "Nosotros"),
    ("faq.html", "FAQ"),
]


def logo(r):
    return (f'<a class="logo" href="{r}index.html" aria-label="{e(SITIO)}, ir al inicio">'
            '<span class="logo-marca" aria-hidden="true">M&amp;M</span>'
            '<span class="logo-texto">Mix&amp;Medios</span><span class="logo-sub">blog</span></a>')


def cierre(r):
    opciones = "".join(f'<option value="{k}">{e(v[0])}</option>' for k, v in CATS.items())
    return f"""
<section class="cierre" aria-labelledby="cierre-titulo">
  <div class="contenedor cierre-grid">
    <div>
      <h2 id="cierre-titulo">Repasa el curso a tu ritmo</h2>
      <p>¿Tienes examen o exposición? Busca el tema que necesitas y llega con los conceptos claros. Cada entrada termina con un quiz de tres preguntas.</p>
      <div class="cierre-datos">
        <div><small>Semanas</small><strong>15</strong></div>
        <div><small>Caso aplicado</small><strong>IronBites</strong></div>
      </div>
      <p style="margin-top:22px"><a class="enlace-claro" href="{r}glosario.html">Abrir el glosario</a> · <a class="enlace-claro" href="{r}producto.html">Ver el caso IronBites</a></p>
    </div>
    <form class="tarjeta-blanca" action="{r}blog.html" method="get">
      <h3>Encuentra tu tema.</h3>
      <p>Elige una unidad o escribe un concepto.</p>
      <label for="cierre-cat">¿Qué unidad quieres repasar?</label>
      <select id="cierre-cat" name="cat"><option value="">Todas las unidades</option>{opciones}</select>
      <label for="cierre-q">¿Qué concepto buscas?</label>
      <input id="cierre-q" name="q" type="search" placeholder="Por ejemplo: rating, Big Idea, long tail">
      <button class="btn" type="submit"><span>Buscar en el blog</span><span aria-hidden="true">→</span></button>
      <p class="nota">Se abrirá el blog con tu búsqueda aplicada.</p>
    </form>
  </div>
</section>"""


def pagina(*, ruta, titulo, descripcion, cuerpo, actual="", imagen="img/hero.jpg", tipo="website",
           jsonld=None, extra_body="", hero_oscuro=False):
    """ruta: ruta de salida relativa a docs/ (p. ej. 'entradas/x.html')."""
    nivel = ruta.count("/")
    r = "../" * nivel
    assert len(titulo) <= 60, f"título SEO largo ({len(titulo)}): {titulo}"
    assert len(descripcion) <= 160, f"descripción larga ({len(descripcion)}): {descripcion}"
    url = BASE_URL + ("" if ruta == "index.html" else ruta)
    marca = ' aria-current="page"'
    nav = "".join(f'<a href="{r}{href}"{marca if href == actual else ""}>{txt}</a>' for href, txt in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    clase_cab = "cabecera sobre-hero" if hero_oscuro else "cabecera"
    return f"""<!DOCTYPE html>
<html lang="es-PE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<link rel="canonical" href="{e(url)}">
<meta property="og:type" content="{tipo}">
<meta property="og:site_name" content="{e(SITIO)}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{e(url)}">
<meta property="og:image" content="{e(BASE_URL + imagen)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#061e50">
<link rel="icon" href="{r}img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}css/estilos.css?v={VERSION}">
<script>try{{var t=localStorage.getItem("myd-tema");if(t)document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
{ld}
</head>
<body>
<a class="saltar" href="#contenido">Saltar al contenido</a>
<div class="promo"><div class="contenedor"><strong>Trabajo final · Comunicaciones de Marketing</strong><span>ESAN 2026-2 · Sección S-006</span><a href="{r}producto.html">Ver el caso</a></div></div>
<header class="{clase_cab}" id="cabecera">
  <div class="contenedor">
    <div class="cabecera-barra">
      {logo(r)}
      <nav class="nav" id="nav" aria-label="Principal">{nav}</nav>
      <div class="acciones">
        <a class="pill pill-borde" href="{r}blog.html">{ICONO_LUPA.replace('<svg ', '<svg width="18" height="18" ')} Buscar</a>
        <a class="pill pill-azul" href="{r}producto.html">IronBites</a>
        <a class="pill pill-blanca pill-blanca-hero" href="{r}producto.html">IronBites</a>
        <button class="btn-icono" id="tema" aria-label="Cambiar tema">{ICONO_SOL}{ICONO_LUNA}</button>
        <button class="btn-icono menu-btn" id="menu" aria-label="Abrir menú" aria-expanded="false" aria-controls="nav">{ICONO_MENU}</button>
      </div>
    </div>
  </div>
</header>
<main id="contenido">
{cuerpo}
</main>
{cierre(r)}
<footer class="pie">
  <div class="contenedor">
    <div class="pie-grid">
      <div>
        {logo(r)}
        <p style="margin-top:16px;max-width:24em">{e(LEMA)}: apuntes, casos y quizzes de las 15 semanas, aplicados a IronBites.</p>
      </div>
      <div>
        <h2>Explorar</h2>
        <ul>{"".join(f'<li><a href="{r}{h}">{t}</a></li>' for h, t in NAV)}</ul>
      </div>
      <div>
        <h2>El curso</h2>
        <ul>
          <li>Comunicaciones de Marketing</li>
          <li>Universidad ESAN · 2026-2 · S-006</li>
          <li>Prof. Mario Alonso Gallo Medina</li>
          <li><a href="{WEB_IRONBITES}" target="_blank" rel="noopener">Web de marca IronBites</a></li>
        </ul>
      </div>
    </div>
    <p class="pie-legal">© <span id="anio">2026</span> Equipo Mix &amp; Medios. Proyecto académico sin fines comerciales. IronBites es una propuesta de producto ficticia creada para el curso; Pícaras y las demás marcas citadas pertenecen a sus dueños. Las imágenes son ilustrativas y se generaron con IA.</p>
  </div>
</footer>
{extra_body}
<script src="{r}js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


def tarjeta(p, r):
    k = p["categoria"]
    cat = CATS[k][0]
    texto = " ".join([p["titulo"], p["resumen"], p["keyword"], " ".join(p.get("etiquetas", [])), cat, f"semana {p['semana']}"])
    return f"""<article class="tarjeta tono-{TONO[k]}" data-cat="{e(k)}" data-texto="{e(texto)}">
  <div class="tarjeta-cuerpo">
    <span class="etiqueta-semana">Semana {p['semana']} · {e(CORTO[k])}</span>
    <h3><a href="{r}entradas/{p['slug']}.html">{e(p['titulo'])}</a></h3>
    <p>{e(p['resumen'])}</p>
    <div class="tarjeta-meta"><span>{p['minutos']} min de lectura</span></div>
  </div>
  <div class="tarjeta-img"><img src="{r}{IMG_CAT[k]}" alt="" loading="lazy" width="1200" height="671"></div>
</article>"""


def ruta_curso(posts, r):
    por_semana = {}
    for p in posts:
        por_semana.setdefault(p["semana"], []).append(p)
    items = []
    for n, tema in SEMANAS:
        ps = por_semana.get(n) or (por_semana.get(6) if n == 7 else [])
        enlaces = "<br>".join(f'<a href="{r}entradas/{p["slug"]}.html">{e(p["titulo"])}</a>' for p in ps)
        especial = ' class="especial"' if n in (6, 7, 15) else ""
        items.append(f'<li{especial}><span class="num">{n:02d}</span><strong>{e(tema)}</strong>{enlaces}</li>')
    return f'<ol class="ruta">{"".join(items)}</ol>'


# ------------------------------------------------------------------ páginas
def pag_inicio(posts, glosario):
    r = ""
    recientes = sorted(posts, key=lambda p: (p["semana"], p["archivo"]), reverse=True)[:6]
    tiles = "".join(
        f'<a class="tile tono-{TONO[k]}" href="categoria/{k}.html"><i aria-hidden="true">{ABREV[k]}</i>{e(CORTO[k])}</a>'
        for k in CATS
    )
    claves = list(CATS)
    botones = "".join(
        f'<button type="button" role="tab" id="tab-{k}" aria-controls="panel-{k}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{e(CORTO[k])}</button>'
        for i, k in enumerate(claves)
    )
    paneles = []
    for i, k in enumerate(claves):
        nombre, desc, semanas = CATS[k]
        ps = [p for p in posts if p["categoria"] == k]
        lista = "".join(f'<li><a href="entradas/{p["slug"]}.html">{e(p["titulo"])}</a></li>' for p in ps)
        paneles.append(f"""<div class="panel-grande tono-{TONO[k]}" role="tabpanel" id="panel-{k}" aria-labelledby="tab-{k}"{"" if i == 0 else " hidden"}>
  <div class="texto">
    <span class="etiqueta-semana">Semana{"s" if len(semanas) > 1 else ""} {", ".join(map(str, semanas))}</span>
    <h3>{e(nombre)}</h3>
    <p>{e(desc)}</p>
    <ul>{lista}</ul>
    <a class="enlace-raya" href="categoria/{k}.html">Ver la unidad completa</a>
  </div>
  <img src="{IMG_CAT[k]}" alt="" loading="lazy" width="1200" height="671">
</div>""")
    cuerpo = f"""
<section class="hero-foto" style="background-image:url('img/hero.jpg')">
  <div class="contenedor">
    <h1>Lo que aprendimos en 15 semanas. Explicado para que no se te olvide.</h1>
    <p class="bajada">Mix &amp; Medios reúne todo el curso de comunicaciones de marketing en un blog: {len(posts)} entradas, un glosario de {len(glosario)} términos, quizzes y un caso aplicado de principio a fin, IronBites.</p>
    <div class="hero-acciones">
      <a class="btn blanco" href="blog.html">Leer el blog</a>
      <a class="enlace-claro" href="producto.html">Ver el caso IronBites</a>
    </div>
    <nav class="hero-tiles" aria-label="Categorías">{tiles}</nav>
  </div>
</section>

<div class="hoja">
  <section class="contenedor" aria-labelledby="explora">
    <div class="intro-2col">
      <h2 id="explora">Marca, medios, RR. PP. y digital, en un solo lugar</h2>
      <p>Diez unidades del sílabo, cada una con sus entradas, ejemplos peruanos y un recuadro que muestra cómo lo aplicamos en IronBites. ¿No sabes por dónde empezar? <a href="entradas/{posts[0]['slug']}.html">Empieza por la semana 1</a>.</p>
    </div>
    <div class="explorador">
      <div class="explorador-top"><span>Desliza para descubrir</span><span id="explorador-num">01 / {len(claves):02d}</span></div>
      <div class="segmentos" role="tablist" aria-label="Unidades del curso">{botones}</div>
      {"".join(paneles)}
      <p class="nota">Las imágenes son ilustrativas.</p>
    </div>
  </section>

  <section class="seccion">
    <div class="contenedor">
      <div class="seccion-cabeza"><div><h2>Últimas entradas</h2><p>De la semana 15 hacia atrás.</p></div><a class="btn secundario" href="blog.html">Ver todas</a></div>
      <div class="rejilla">{"".join(tarjeta(p, r) for p in recientes)}</div>
    </div>
  </section>

  <section class="contenedor">
    <div class="oscura">
      <div class="oscura-grid">
        <div>
          <span class="kicker">Caso del curso</span>
          <p class="grande">Un ejemplo de principio a fin: la galleta de Pícaras con hierro. Cada tema del curso se aplica a IronBites, desde el FODA hasta el spot, las relaciones públicas y la web.</p>
          <div class="hero-acciones">
            <a class="btn blanco" href="producto.html">Conocer IronBites</a>
            <a class="enlace-claro" href="entradas/plan-de-comunicaciones-integradas-caso-ironbites.html">Leer el plan completo</a>
          </div>
        </div>
        <img src="img/ironbites.jpg" alt="Paquete de galletas IronBites con hierro y chispas de chocolate" loading="lazy" width="1168" height="880">
      </div>
    </div>
  </section>

  <section class="seccion">
    <div class="contenedor">
      <div class="intro-2col"><h2>La ruta de las 15 semanas</h2><p>Haz clic en una entrada para ir directo al tema de esa semana.</p></div>
      {ruta_curso(posts, r)}
    </div>
  </section>
</div>
"""
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": SITIO, "description": LEMA,
          "url": BASE_URL, "inLanguage": "es-PE"}
    return pagina(ruta="index.html", titulo="Mix & Medios: blog de comunicaciones de marketing",
                  descripcion="Blog con las 15 semanas del curso de comunicaciones de marketing: marca, creatividad, medios, RR. PP., SEO y redes, aplicadas al caso IronBites.",
                  cuerpo=cuerpo, actual="index.html", jsonld=ld, hero_oscuro=True)


def pag_blog(posts):
    r = ""
    chips = '<button type="button" data-cat="todas" aria-pressed="true">Todas</button>' + "".join(
        f'<button type="button" data-cat="{k}" aria-pressed="false">{e(CORTO[k])}</button>' for k in CATS
    )
    cuerpo = f"""
<div class="contenedor">
  <header class="pagina-cabeza">
    <nav class="migas" aria-label="Migas de pan"><a href="index.html">Inicio</a> / Blog</nav>
    <h1>Blog de comunicaciones de marketing</h1>
    <p>Todas las entradas del curso, semana por semana. Busca un concepto (por ejemplo «rating», «Big Idea» o «long tail») o filtra por unidad.</p>
  </header>
  <div class="filtros">
    <label class="buscador"><span class="sr-only">Buscar en el blog</span>{ICONO_LUPA}<input id="buscar" type="search" placeholder="Buscar conceptos, autores o marcas…" autocomplete="off"></label>
    <div class="chips" id="chips-cat" role="group" aria-label="Filtrar por unidad">{chips}</div>
    <p class="contador" id="contador" aria-live="polite"></p>
  </div>
  <div class="rejilla" id="lista-blog">{"".join(tarjeta(p, r) for p in posts)}</div>
  <p class="vacio oculto" id="vacio">No encontramos entradas con esa búsqueda. Prueba con otra palabra o revisa el <a href="glosario.html">glosario</a>.</p>
</div>
"""
    return pagina(ruta="blog.html", titulo="Blog de comunicaciones de marketing | Mix & Medios",
                  descripcion="Entradas de las 15 semanas del curso de comunicaciones de marketing con buscador y filtros por categoría: marca, medios, RR. PP. y digital.",
                  cuerpo=cuerpo, actual="blog.html")


def pag_categorias(posts):
    r = ""
    bloques = []
    for k, (nombre, desc, semanas) in CATS.items():
        ps = [p for p in posts if p["categoria"] == k]
        lista = "".join(f'<li><a href="entradas/{p["slug"]}.html">{e(p["titulo"])}</a></li>' for p in ps)
        sem = ", ".join(str(s) for s in semanas)
        bloques.append(f"""<div class="panel-grande tono-{TONO[k]}" style="margin-top:0">
  <div class="texto">
    <span class="etiqueta-semana">Semana{"s" if len(semanas) > 1 else ""} {sem}</span>
    <h3>{e(nombre)}</h3>
    <p>{e(desc)}</p>
    <ul>{lista}</ul>
    <a class="enlace-raya" href="categoria/{k}.html">Ver la unidad completa</a>
  </div>
  <img src="{IMG_CAT[k]}" alt="" loading="lazy" width="1200" height="671">
</div>""")
    cuerpo = f"""
<div class="contenedor">
  <header class="pagina-cabeza">
    <nav class="migas" aria-label="Migas de pan"><a href="index.html">Inicio</a> / Categorías</nav>
    <h1>Categorías del curso de comunicaciones de marketing</h1>
    <p>El sílabo ordenado en diez unidades. Cada una reúne sus entradas y termina aplicada al caso IronBites.</p>
  </header>
  <div style="display:grid;gap:18px">{"".join(bloques)}</div>
  <section class="seccion" style="padding-bottom:0">
    <div class="intro-2col"><h2>Ruta del curso semana a semana</h2><p>Las semanas 6 y 7 fueron de repaso y evaluación parcial; la 15, la exposición final.</p></div>
    {ruta_curso(posts, r)}
  </section>
</div>
"""
    return pagina(ruta="categorias.html", titulo="Categorías del curso | Mix & Medios",
                  descripcion="Las unidades del curso de comunicaciones de marketing en diez categorías: fundamentos, marca, creatividad, medios masivos, RR. PP. y digital.",
                  cuerpo=cuerpo, actual="categorias.html")


def pag_categoria(k, posts):
    r = "../"
    nombre, desc, semanas = CATS[k]
    ps = [p for p in posts if p["categoria"] == k]
    titulo = f"{nombre} | Mix & Medios"
    descripcion = f"Entradas de {nombre.lower()} del curso de comunicaciones de marketing: {desc[0].lower() + desc[1:]}"[:160]
    cuerpo = f"""
<div class="contenedor">
  <div class="cabeza-tinte tono-{TONO[k]}">
    <div>
      <nav class="migas" aria-label="Migas de pan"><a href="../index.html">Inicio</a> / <a href="../categorias.html">Categorías</a> / {e(nombre)}</nav>
      <span class="etiqueta-semana">Semana{"s" if len(semanas) > 1 else ""} {", ".join(map(str, semanas))}</span>
      <h1>{e(nombre)}</h1>
      <p style="font-size:1.15rem;color:var(--muted)">{e(desc)} {len(ps)} entrada{"s" if len(ps) != 1 else ""} en esta categoría.</p>
    </div>
    <img src="../{IMG_CAT[k]}" alt="" width="1200" height="671">
  </div>
  <div class="rejilla">{"".join(tarjeta(p, r) for p in ps)}</div>
</div>
"""
    return pagina(ruta=f"categoria/{k}.html", titulo=titulo, descripcion=descripcion, cuerpo=cuerpo,
                  actual="categorias.html", imagen=IMG_CAT[k])


def pag_post(p, posts):
    from urllib.parse import quote
    r = "../"
    k = p["categoria"]
    i = posts.index(p)
    ant = posts[i - 1] if i > 0 else None
    sig = posts[i + 1] if i < len(posts) - 1 else None
    cat = CATS[k][0]
    relacionadas = [q for q in posts if q["categoria"] == k and q is not p]
    for q in (ant, sig) + tuple(posts):
        if len(relacionadas) >= 3:
            break
        if q and q is not p and q not in relacionadas:
            relacionadas.append(q)
    relacionadas = relacionadas[:3]
    indice = "".join(f'<li><a href="#{i_}">{e(t)}</a></li>' for i_, t in p["indice"])
    quiz = ""
    if p.get("quiz"):
        fs = []
        for n, q in enumerate(p["quiz"]):
            ops = "".join(
                f'<label><input type="radio" name="q{n}" value="{j}" required> <span>{e(o)}</span></label>'
                for j, o in enumerate(q["o"])
            )
            fs.append(f'<fieldset data-c="{q["c"]}"><legend>{n + 1}. {e(q["p"])}</legend>{ops}<p class="explica oculto">{e(q["e"])}</p></fieldset>')
        quiz = f"""<form class="quiz" aria-labelledby="quiz-{p['slug']}">
  <h2 id="quiz-{p['slug']}">Pon a prueba lo aprendido</h2>
  {"".join(fs)}
  <button class="btn" type="submit">Revisar respuestas</button><span class="resultado" aria-live="polite"></span>
</form>"""
    url = BASE_URL + f"entradas/{p['slug']}.html"
    compartir = f"""<div class="compartir"><span>Compartir:</span>
  <a href="https://wa.me/?text={quote(p['titulo'] + ' ' + url)}" target="_blank" rel="noopener">WhatsApp</a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url={quote(url)}" target="_blank" rel="noopener">LinkedIn</a>
  <a href="https://twitter.com/intent/tweet?text={quote(p['titulo'])}&amp;url={quote(url)}" target="_blank" rel="noopener">X</a>
  <button type="button" data-copiar>Copiar enlace</button>
</div>"""
    nav = '<nav class="navegacion-posts" aria-label="Entradas anterior y siguiente">'
    nav += f'<a href="{ant["slug"]}.html"><small>← Anterior · Semana {ant["semana"]}</small>{e(ant["titulo"])}</a>' if ant else "<span></span>"
    nav += f'<a class="sig" href="{sig["slug"]}.html"><small>Siguiente · Semana {sig["semana"]} →</small>{e(sig["titulo"])}</a>' if sig else ""
    nav += "</nav>"
    etiquetas = " ".join(f'<span class="chip">{e(t)}</span>' for t in p.get("etiquetas", []))
    cuerpo = f"""
<div class="barra-lectura" aria-hidden="true"></div>
<article>
  <header class="articulo-cabeza">
    <div class="contenedor">
      <div class="cabeza-tinte tono-{TONO[k]}">
        <div>
          <nav class="migas" aria-label="Migas de pan"><a href="../index.html">Inicio</a> / <a href="../blog.html">Blog</a> / <a href="../categoria/{k}.html">{e(cat)}</a></nav>
          <span class="etiqueta-semana">Semana {p['semana']} · {e(cat)}</span>
          <h1>{e(p['titulo'])}</h1>
          <div class="articulo-meta"><span>Por Equipo Mix &amp; Medios</span><span>·</span><span>{p['minutos']} min de lectura</span><span>·</span><span>{p['palabras']} palabras</span></div>
        </div>
        <img src="../{IMG_CAT[k]}" alt="Imagen ilustrativa de {e(cat.lower())}" width="1200" height="671">
      </div>
    </div>
  </header>
  <div class="articulo-layout">
    <div>
      <div class="prosa">{p['cuerpo']}</div>
      <p style="display:flex;flex-wrap:wrap;gap:6px;margin-top:24px">{etiquetas}</p>
      {quiz}
      {compartir}
      {nav}
    </div>
    <aside class="indice" aria-label="Índice del artículo"><h2>En esta entrada</h2><ol>{indice}</ol></aside>
  </div>
</article>
<section class="seccion">
  <div class="contenedor">
    <div class="seccion-cabeza"><h2>Entradas relacionadas</h2></div>
    <div class="rejilla">{"".join(tarjeta(q, r) for q in relacionadas)}</div>
  </div>
</section>
"""
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["titulo"],
          "description": p["descripcion"], "inLanguage": "es-PE", "keywords": p["keyword"],
          "image": BASE_URL + IMG_CAT[k], "url": url, "wordCount": p["palabras"],
          "author": {"@type": "Organization", "name": "Equipo Mix & Medios"},
          "publisher": {"@type": "Organization", "name": SITIO}}
    return pagina(ruta=f"entradas/{p['slug']}.html", titulo=p["seo_title"], descripcion=p["descripcion"],
                  cuerpo=cuerpo, actual="blog.html", imagen=IMG_CAT[k], tipo="article", jsonld=ld)


def enlace_post(posts, semana, r=""):
    p = next((q for q in posts if q["semana"] == semana), None)
    return f'{r}entradas/{p["slug"]}.html' if p else f"{r}blog.html"


def pag_producto(posts):
    L = lambda s: enlace_post(posts, s)
    cuerpo = f"""
<div class="contenedor">
  <section class="ib-hero">
    <div>
      <span class="chip">Caso integrador del curso</span>
      <h1 style="margin-top:16px">IronBites: galletas con <span>hierro</span> y el sabor de siempre</h1>
      <p>La nueva línea de Pícaras fortificada con hierro: la misma galleta crocante bañada en chocolate, con chispas de cacao de la selva peruana y unos 7 mg de hierro por porción.</p>
      <p class="lema">«El sabor divertido de siempre, con la fuerza del hierro para ti.»</p>
      <div class="hero-acciones">
        <a class="btn" href="{WHATSAPP}" target="_blank" rel="noopener" style="background:var(--ib-r)">Escríbenos por WhatsApp</a>
        <a class="enlace-raya" href="{WEB_IRONBITES}" target="_blank" rel="noopener">Ver la web de marca</a>
      </div>
    </div>
    <img src="img/ironbites.jpg" alt="Paquete amarillo y rojo de galletas IronBites con un sello de 7 mg de hierro" width="1168" height="880">
  </section>

  <section class="seccion" style="padding-bottom:0">
    <div class="ib-datos">
      <div class="ib-dato"><strong>30 g</strong><span>por porción, formato fácil de llevar</span></div>
      <div class="ib-dato"><strong>~7 mg</strong><span>de hierro hemínico, sin sabor metálico</span></div>
      <div class="ib-dato"><strong>17–24</strong><span>años: jóvenes NSE B y C de Lima</span></div>
      <div class="ib-dato"><strong>34,9 %</strong><span>de niños de 6 a 35 meses con anemia en 2025 (INEI)</span></div>
    </div>
  </section>

  <section class="seccion">
    <div class="intro-2col"><h2>Propuesta de valor</h2><p class="cita-grande" style="font-size:clamp(1.3rem,2.4vw,1.8rem);color:var(--ink)">«Disfruta el sabor y la picardía de Pícaras, ahora con aporte de hierro, en una alternativa práctica que combina nutrición y sabor sin dejar de disfrutar.»</p></div>
    <div class="bloques">
      <div class="bloque tono-morado"><h3>Puntos de diferencia</h3><ul><li>Hierro dentro de una galleta de consumo diario.</li><li>Indulgencia y nutrición en un mismo snack.</li><li>Respaldo de una marca que el público ya conoce.</li><li>Personalidad divertida aplicada a un tema serio.</li></ul><p class="ver"><a class="enlace-raya" href="{L(2)}">Cómo se construye una marca</a></p></div>
      <div class="bloque tono-verde"><h3>Diagnóstico y estrategia</h3><p>Cinco fuerzas con intermediarios de poder alto y rivalidad alta; FODA cruzado con estrategia <strong>DO – Innovación y diversificación</strong> de la categoría.</p><p class="ver"><a class="enlace-raya" href="{L(4)}">Planificación CIM</a></p></div>
      <div class="bloque tono-azul"><h3>Objetivos a diciembre de 2026</h3><ul><li><strong>Negocio:</strong> +10 % de ventas de galletas fortificadas.</li><li><strong>Comportamiento:</strong> 15 % con intención de probar.</li><li><strong>Imagen:</strong> 25 % asocia la categoría con nutrición y sabor.</li></ul></div>
      <div class="bloque tono-pizarra"><h3>Buyer persona: Jorge</h3><p>Universitario que come snacks entre clases, estudiando o fuera de casa. Quiere rendir todo el día sin complicar su rutina.</p><p class="ver"><a class="enlace-raya" href="{L(5)}">Viaje del consumidor</a></p></div>
    </div>
  </section>

  <section class="oscura">
    <span class="kicker">Big Idea</span>
    <h2>«Tu nuevo Power-Up contra la anemia»</h2>
    <p class="grande">El día de un joven es como un videojuego: clases, trabajo, entrenamientos y redes. La anemia es el «Game Over». IronBites es la vida extra que te deja seguir en la partida.</p>
    <h3 style="color:#fff;margin:32px 0 14px">Guion del spot de TV (30 s)</h3>
    <ol class="guion">
      <li><b>0–7 s · Game over</b>«¡Tengo mil retos por delante y necesito seguir avanzando!»</li>
      <li><b>7–15 s · Power-up</b>«¡IronBites, galletas con hierro para acompañarte en tus retos diarios!»</li>
      <li><b>15–23 s · Level up</b>«¡Nuevo nivel desbloqueado! El sabor de siempre, ahora con vida extra.»</li>
      <li><b>23–30 s · Cierre</b>«¡IronBites, tu nuevo Power-Up contra la anemia!» Texto: <em>Activa tu modo hierro</em>.</li>
    </ol>
    <div class="hero-acciones"><a class="btn blanco" href="{L(3)}">Así nace una Big Idea</a></div>
  </section>

  <section class="seccion">
    <div class="intro-2col"><h2>La campaña en todos los medios</h2><p>Una sola idea, el power-up, adaptada a cada formato. Eso es lo que hace integrado al plan.</p></div>
    <div class="bloques">
      <div class="bloque tono-azul"><h3>Medios masivos</h3><ul><li>Spot de TV y cuña radial de 30 s.</li><li>Aviso en revista especializada con barra de vida.</li><li>Pantalla LED en la Vía Expresa y lightbox en el Metropolitano.</li><li>Panel frente a universidades y máquinas expendedoras estilo arcade.</li></ul><p class="ver"><a class="enlace-raya" href="{L(8)}">Medios masivos</a></p></div>
      <div class="bloque tono-morado"><h3>Relaciones públicas</h3><ul><li>Press kit «El sabor peruano que combate la anemia».</li><li>Programa social «Mordidas que Suman».</li><li>Cápsulas «Mitos vs. Verdades del Antojo» con micro-influencers.</li><li>«Cabina de Recarga IronBites» en universidades.</li></ul><p class="ver"><a class="enlace-raya" href="{L(10)}">Relaciones públicas</a></p></div>
      <div class="bloque tono-naranja"><h3>Trade y promociones</h3><ul><li>Exhibidor «Isla Power-Up» en quioscos universitarios.</li><li>Push: 6 paquetes gratis por cada 2 displays.</li><li>Pull: 2x1.5 con cupón QR en Tambo y Oxxo.</li><li>Pack post-entreno x3 a S/ 5.00 en gimnasios.</li></ul><p class="ver"><a class="enlace-raya" href="{L(11)}">Medios alternativos</a></p></div>
      <div class="bloque tono-verde"><h3>Digital</h3><ul><li>Web de marca con inicio, producto, blog y FAQ.</li><li>SEO y SEM para búsquedas sobre anemia y snacks.</li><li>Contenido y anuncios en TikTok e Instagram.</li></ul><p class="ver"><a class="enlace-raya" href="{L(12)}">Marketing digital</a></p></div>
    </div>
    <figure style="margin:32px 0 0">
      <img src="img/campana-ironbites.jpg" alt="Panel con las piezas de la campaña IronBites diseñadas por el equipo" loading="lazy" style="border-radius:var(--r);width:100%">
      <figcaption class="nota">Piezas de campaña del trabajo integrador.</figcaption>
    </figure>
  </section>
</div>
<a class="wa" href="{WHATSAPP}" target="_blank" rel="noopener" aria-label="Escribir a IronBites por WhatsApp">{ICONO_WA}</a>
"""
    return pagina(ruta="producto.html", titulo="IronBites: galletas con hierro | Mix & Medios",
                  descripcion="IronBites, la galleta de Pícaras con hierro: propuesta de valor, Big Idea «Power-Up contra la anemia», spot, RR. PP., trade y digital.",
                  cuerpo=cuerpo, actual="producto.html", imagen="img/ironbites.jpg")


def pag_nosotros():
    tonos = ["azul", "verde", "morado", "naranja", "pizarra"]
    miembros = "".join(
        f'<div class="miembro tono-{tonos[i]}"><div class="avatar" aria-hidden="true">{n[0]}{a[0]}</div>'
        f'<strong>{e(n)}<br>{e(a)}</strong><span>Redacción y caso IronBites</span></div>'
        for i, (n, a) in enumerate(EQUIPO)
    )
    cuerpo = f"""
<div class="contenedor">
  <header class="pagina-cabeza">
    <nav class="migas" aria-label="Migas de pan"><a href="index.html">Inicio</a> / Nosotros</nav>
    <h1>Nosotros: el equipo detrás de Mix &amp; Medios</h1>
    <p>Somos cinco estudiantes del curso de Comunicaciones de Marketing de la Universidad ESAN (2026-2, sección S-006). Creamos este blog para ordenar lo aprendido en las 15 semanas y explicarlo como nos hubiera gustado leerlo.</p>
  </header>
  <div class="dos-col">
    <div>
      <h2>Por qué hicimos este blog</h2>
      <p>Durante el ciclo pasamos por más de doce temas: de la teoría de la comunicación a Google Ads. Cada semana aplicamos esos conceptos a un mismo caso, <a href="producto.html">IronBites</a>, una galleta de Pícaras con hierro pensada para jóvenes.</p>
      <p>Aquí cada entrada explica un tema con nuestras palabras, lo conecta con marcas reales y termina con un recuadro que muestra cómo lo usamos en el caso. Al final hay un quiz de tres preguntas para repasar.</p>
      <ul>
        <li><strong>Curso:</strong> Comunicaciones de Marketing</li>
        <li><strong>Universidad:</strong> ESAN · Semestre 2026-2 · Sección S-006</li>
        <li><strong>Profesor:</strong> Mario Alonso Gallo Medina</li>
      </ul>
    </div>
    <img src="img/equipo.jpg" alt="Estudiantes trabajando juntos en una mesa con laptops y notas" width="1200" height="671">
  </div>
  <section class="seccion" style="padding-bottom:0">
    <h2>El equipo</h2>
    <div class="equipo">{miembros}</div>
  </section>
</div>
"""
    return pagina(ruta="nosotros.html", titulo="Nosotros | Mix & Medios",
                  descripcion="Conoce al equipo de estudiantes de ESAN que creó Mix & Medios, el blog del curso de Comunicaciones de Marketing 2026-2.",
                  cuerpo=cuerpo, actual="nosotros.html", imagen="img/equipo.jpg")


FAQ = [
    ("Sobre el blog", [
        ("¿Qué es Mix & Medios?", "Es el blog del curso de Comunicaciones de Marketing de ESAN (2026-2). Reúne en entradas cortas los temas de las 15 semanas, con ejemplos, un glosario y quizzes."),
        ("¿Cómo está organizado?", "Por semanas y por categorías. Puedes leer en orden desde el <a href=\"categorias.html\">mapa de categorías</a> o buscar un concepto en el <a href=\"blog.html\">blog</a>."),
        ("¿Qué pasa en las semanas 6, 7 y 15?", "Las semanas 6 y 7 son de repaso y evaluación parcial, por eso tienen una entrada de repaso. La semana 15 es la exposición final del trabajo integrador, resumida en la entrada de cierre."),
        ("¿Para qué sirven los quizzes?", "Cada entrada termina con tres preguntas de opción múltiple. Al revisar, ves la respuesta correcta y una explicación breve. No se guarda ningún dato."),
        ("¿Cómo busco un término rápido?", "En el <a href=\"glosario.html\">glosario</a> están todos los conceptos del curso, ordenados de la A a la Z y con buscador."),
    ]),
    ("Sobre IronBites", [
        ("¿Qué es IronBites?", "Es la propuesta de producto de nuestro trabajo integrador: una nueva línea de Pícaras fortificada con hierro, con la misma galleta crocante bañada en chocolate."),
        ("¿Cuánto hierro tiene una porción?", "La propuesta considera una porción de 30 g con unos 7 mg de hierro hemínico, una fuente que no deja sabor metálico."),
        ("¿A quién está dirigida?", "A jóvenes de 17 a 24 años de Lima, NSE B y C, que buscan un snack práctico, rico y con aporte nutricional. Las madres y los padres influyen como decisores de la lonchera."),
        ("¿IronBites existe en tiendas?", "No. Es un producto ficticio creado para el curso; Pícaras es una marca real usada solo como caso académico."),
        ("¿Cuál es la idea central de la campaña?", "«Tu nuevo Power-Up contra la anemia»: la anemia es el «Game Over» y IronBites es la vida extra. El cierre de todas las piezas es «Activa tu modo hierro»."),
    ]),
]


def pag_faq():
    secciones, ld_items = [], []
    for titulo, qs in FAQ:
        det = "".join(f"<details><summary>{e(q)}</summary><div><p>{a}</p></div></details>" for q, a in qs)
        secciones.append(f"<h2>{e(titulo)}</h2>{det}")
        ld_items += [{"@type": "Question", "name": q,
                      "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in qs]
    cuerpo = f"""
<div class="contenedor" style="max-width:960px">
  <header class="pagina-cabeza">
    <nav class="migas" aria-label="Migas de pan"><a href="index.html">Inicio</a> / Preguntas frecuentes</nav>
    <h1>Preguntas frecuentes</h1>
    <p>Sobre el blog, el curso y el caso IronBites.</p>
  </header>
  <div class="faq">{"".join(secciones)}</div>
</div>
"""
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": ld_items}
    return pagina(ruta="faq.html", titulo="Preguntas frecuentes | Mix & Medios",
                  descripcion="Respuestas sobre el blog Mix & Medios, el curso de comunicaciones de marketing y el caso IronBites, la galleta de Pícaras con hierro.",
                  cuerpo=cuerpo, actual="faq.html", jsonld=ld)


def pag_glosario(glosario, posts):
    grupos = {}
    for t in glosario:
        letra = sin_tildes(t["t"][0].upper())
        letra = letra if letra.isalpha() else "#"
        grupos.setdefault(letra, []).append(t)
    letras = "".join(f'<a href="#letra-{l}">{l}</a>' for l in grupos)
    bloques = []
    for l, ts in grupos.items():
        items = "".join(
            f'<div class="termino"><dt>{e(t["t"])}</dt><dd>{e(t["d"])} <a href="{enlace_post(posts, t["s"])}">Semana {t["s"]} →</a></dd></div>'
            for t in ts
        )
        bloques.append(f'<section class="grupo"><h2 id="letra-{l}">{l}</h2><dl>{items}</dl></section>')
    cuerpo = f"""
<div class="contenedor" style="max-width:960px">
  <header class="pagina-cabeza">
    <nav class="migas" aria-label="Migas de pan"><a href="index.html">Inicio</a> / Glosario</nav>
    <h1>Glosario de comunicaciones de marketing</h1>
    <p>{len(glosario)} conceptos del curso explicados en una o dos frases, con enlace a la semana donde se ven a fondo.</p>
  </header>
  <label class="buscador"><span class="sr-only">Buscar un término</span>{ICONO_LUPA}<input id="buscar-termino" type="search" placeholder="Buscar un término (p. ej. share, ZMOT, CPM)…" autocomplete="off"></label>
  <p class="contador" id="contador-glosario" aria-live="polite" style="margin-top:12px">{len(glosario)} términos</p>
  <nav class="letras" aria-label="Ir a la letra">{letras}</nav>
  <div class="glosario">{"".join(bloques)}</div>
</div>
"""
    return pagina(ruta="glosario.html", titulo="Glosario de comunicaciones de marketing",
                  descripcion=f"Glosario con {len(glosario)} términos del curso de comunicaciones de marketing: marca, medios, RR. PP., SEO, SEM y redes, con buscador.",
                  cuerpo=cuerpo, actual="glosario.html")


def pag_404():
    cuerpo = """
<div class="contenedor" style="text-align:center;padding:80px 20px">
  <p class="etiqueta-semana">Error 404</p>
  <h1>Esta página se quedó sin señal</h1>
  <p>Como un spot fuera de la tanda: no llegó a su audiencia. Vuelve al inicio o busca en el blog.</p>
  <div class="hero-acciones" style="justify-content:center"><a class="btn" href="/mix-y-medios/index.html">Ir al inicio</a><a class="btn secundario" href="/mix-y-medios/blog.html">Ver el blog</a></div>
</div>
"""
    return pagina(ruta="404.html", titulo="Página no encontrada | Mix & Medios",
                  descripcion="La página que buscas no existe. Vuelve al inicio de Mix & Medios.", cuerpo=cuerpo)


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#0755f5"/><text x="32" y="41" font-family="Arial, sans-serif" font-size="22" font-weight="800" text-anchor="middle" fill="#fff">M&amp;M</text></svg>"""


def escribir(ruta, texto):
    destino = SALIDA / ruta
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8")


def main():
    posts = cargar_posts()
    glosario = cargar_glosario()
    for carpeta in ("entradas", "categoria"):
        for f in (SALIDA / carpeta).glob("*.html") if (SALIDA / carpeta).exists() else []:
            f.unlink()
    escribir("index.html", pag_inicio(posts, glosario))
    escribir("blog.html", pag_blog(posts))
    escribir("categorias.html", pag_categorias(posts))
    for k in CATS:
        escribir(f"categoria/{k}.html", pag_categoria(k, posts))
    for p in posts:
        escribir(f"entradas/{p['slug']}.html", pag_post(p, posts))
    escribir("producto.html", pag_producto(posts))
    escribir("nosotros.html", pag_nosotros())
    escribir("faq.html", pag_faq())
    escribir("glosario.html", pag_glosario(glosario, posts))
    escribir("404.html", pag_404())
    escribir("img/favicon.svg", FAVICON)
    escribir(".nojekyll", "")
    urls = ["", "blog.html", "categorias.html", "producto.html", "nosotros.html", "faq.html", "glosario.html"]
    urls += [f"categoria/{k}.html" for k in CATS] + [f"entradas/{p['slug']}.html" for p in posts]
    escribir("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
             + "".join(f"  <url><loc>{BASE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    escribir("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n")
    print(f"OK: {len(posts)} entradas, {len(glosario)} términos, {len(urls)} URLs → {SALIDA}")


if __name__ == "__main__":
    main()
