# Guía de redacción — blog «Mix & Medios»

Blog del curso Comunicaciones de Marketing (ESAN 2026-2, sección S-006, prof. Mario Alonso Gallo Medina).
Lo escribe el equipo (firma: «Equipo Mix & Medios»). Estilo: blog de marketing peruano tipo 40deFiebre / Puro Marketing:
claro, cercano, con ejemplos, en español neutro-peruano, tuteo. Nada de relleno. Fiel a las diapositivas (notas por semana).

## Archivos que escribe cada redactor

### 1. Entradas: `contenido/posts/SNN-a.html` y `contenido/posts/SNN-b.html` (NN = semana con 2 dígitos)

Cada archivo empieza con un bloque de metadatos JSON dentro de un comentario, exactamente así:

```
<!--meta
{
  "slug": "que-son-las-comunicaciones-integradas-de-marketing",
  "titulo": "Título visible del post (H1, incluye la palabra clave)",
  "seo_title": "Título SEO de máximo 60 caracteres",
  "descripcion": "Meta description de 120 a 160 caracteres con la palabra clave.",
  "keyword": "comunicaciones integradas de marketing",
  "categoria": "fundamentos",
  "semana": 1,
  "etiquetas": ["CIM", "mix promocional"],
  "resumen": "Una o dos frases para la tarjeta del blog (máx. 200 caracteres).",
  "quiz": [
    {"p": "Pregunta", "o": ["opción A", "opción B", "opción C"], "c": 0, "e": "Explicación breve de la respuesta correcta."}
  ]
}
-->
```

- `slug`: minúsculas, sin tildes, guiones. Único.
- `categoria`: una de: `fundamentos` (S1), `marca` (S2), `creatividad` (S3), `planificacion` (S4), `consumidor` (S5),
  `medios-masivos` (S8, S9), `relaciones-publicas` (S10), `medios-alternativos` (S11), `digital` (S12, S13, S14).
- `quiz`: exactamente 3 preguntas de opción múltiple (3 o 4 opciones), `c` = índice de la correcta (0-based).
- JSON válido (comillas dobles, sin comas finales). Para comillas dentro de textos usa « ».

Después del comentario va el cuerpo en HTML (sin `<html>`, `<head>`, ni `<h1>`: el H1 lo pone la plantilla con `titulo`):

- `<p class="lead">` primer párrafo (2–3 frases) que incluye la palabra clave.
- 3 a 5 secciones con `<h2>` (al menos un H2 contiene la palabra clave); `<h3>` opcional.
- Usa listas, `<table>` sencillas (con `<thead>`), y `<blockquote>` para citas de autores cuando aporte.
- Recuadro de dato clave (opcional, 1 por post): `<div class="dato"><strong>Dato clave:</strong> …</div>`
- Cierra SIEMPRE con el recuadro de aplicación al caso del curso:
  ```
  <aside class="caso">
    <h2>Así lo aplicamos en IronBites</h2>
    <p>…</p>
  </aside>
  ```
  usando datos reales de `IRONBITES.md` (no inventes cifras nuevas del producto).
- Y luego una sección final `<h2>En resumen</h2>` con 3–5 viñetas.
- Largo: 700–1000 palabras de cuerpo. Nada de imágenes (`<img>`): el sitio pone las portadas.
- Puedes enlazar a fuentes externas reales y conocidas (p. ej. Google, Meta, INEI, CPI, Kantar IBOPE) con
  `<a href="…" target="_blank" rel="noopener">`. No inventes URLs: si dudas, no enlaces.
- Enlaces internos entre posts: no los pongas, el sitio arma «entradas relacionadas» solo.
- Cita autores y modelos tal como aparecen en las notas (Kotler, Keller, Aaker, Clow & Baack, etc.).
- No copies párrafos literales de las diapositivas: explica con tus palabras y con ejemplos.

### 2. Glosario: `contenido/glosario/SNN.json`

Lista JSON de 8 a 12 términos de la semana:
```
[{"t": "Share of voice", "d": "Definición en 1–2 frases.", "s": 3}]
```
`s` = número de semana.

## Reglas SEO (las del curso)
- seo_title ≤ 60 caracteres; descripcion ≤ 160 caracteres.
- Un solo H1 (lo pone la plantilla). 3–5 H2. Palabra clave en el H1, en el primer párrafo y en un H2.
