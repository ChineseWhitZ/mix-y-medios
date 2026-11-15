# Mix & Medios

Blog del curso **Comunicaciones de Marketing** (Universidad ESAN, 2026-2, sección S-006). Reúne las 15 semanas del curso en 26 entradas, un glosario de 139 términos y un quiz por entrada. Todo está aplicado al caso integrador **IronBites**.

Es un sitio estático hecho solo con **HTML, CSS y JavaScript** y se publica con GitHub Pages desde la carpeta `docs/`.

## Estructura

- `docs/`: el sitio publicado.
  - `index.html`: inicio.
  - `blog.html`: buscador y filtros en JS.
  - `categorias.html` y `categoria/`.
  - `entradas/`: una página por entrada.
  - `producto.html`: el caso IronBites.
  - `nosotros.html`, `faq.html` y `glosario.html`.
  - `css/estilos.css`: diseño, con modo claro y oscuro.
  - `js/main.js`: tema, menú móvil, barra de lectura, índice, quiz, buscador del blog y del glosario.
- `contenido/`: los textos fuente.
  - `posts/SNN-x.html`: entradas con metadatos SEO en JSON.
  - `glosario/SNN.json`: términos del glosario.
- `build.py`: arma las páginas de `docs/` a partir de `contenido/`. Usa solo Python estándar.

## Editar una entrada

1. Edita el archivo en `contenido/posts/`. La guía de redacción está en `contenido/GUIA_REDACCION.md`.
2. Ejecuta `python3 build.py`.
3. Haz commit y push. GitHub Pages actualiza el sitio en uno o dos minutos.

## Equipo

Carassa Vente Stefano Alessandro · Francia Melendez Daniela Ross · Rojas Campos Amanda Marypaz · Ruiz Paredes Flavia Luana · Salinas Costti Mia Zore

Prof. Mario Alonso Gallo Medina.

Proyecto académico. IronBites es un producto ficticio y las imágenes de portada se generaron con IA.
