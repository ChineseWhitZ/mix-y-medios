/* Mix & Medios — interacciones del sitio (JavaScript propio, sin librerías) */
(function () {
  "use strict";

  var d = document, w = window, raiz = d.documentElement;
  var RAIZ = d.body.getAttribute("data-raiz") || "";
  var sinMovimiento = w.matchMedia && w.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function leer(k, almacen) { try { return (almacen || localStorage).getItem(k); } catch (e) { return null; } }
  function guardar(k, v, almacen) { try { (almacen || localStorage).setItem(k, v); } catch (e) { /* sin almacenamiento */ } }
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function dos(n) { return (n < 10 ? "0" : "") + n; }

  /* ---------- 1. Intro «sintonizando» (una vez por sesión) ---------- */
  var intro = d.getElementById("intro");
  if (intro && raiz.classList.contains("intro-on")) {
    var terminado = false;
    var terminar = function () {
      if (terminado) return;
      terminado = true;
      intro.classList.add("fuera");
      setTimeout(function () { intro.remove(); raiz.classList.remove("intro-on"); }, 380);
      ["pointerdown", "keydown", "wheel", "touchstart"].forEach(function (ev) { w.removeEventListener(ev, terminar, true); });
    };
    ["pointerdown", "keydown", "wheel", "touchstart"].forEach(function (ev) { w.addEventListener(ev, terminar, { capture: true, passive: true }); });
    setTimeout(terminar, 1300);
  } else if (intro) {
    intro.remove();
  }

  /* ---------- 2. Aviso superior que se puede cerrar ---------- */
  var aviso = d.getElementById("aviso");
  if (aviso) {
    if (leer("myd-aviso") === "cerrado") aviso.hidden = true;
    var cerrarAviso = d.getElementById("aviso-cerrar");
    if (cerrarAviso) cerrarAviso.addEventListener("click", function () { aviso.hidden = true; guardar("myd-aviso", "cerrado"); });
  }

  /* ---------- 3. Modo oscuro ---------- */
  var botonTema = d.getElementById("tema");
  function temaActual() {
    var t = raiz.getAttribute("data-theme");
    if (t) return t;
    return w.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function pintarTema() {
    if (!botonTema) return;
    var oscuro = temaActual() === "dark";
    botonTema.setAttribute("aria-label", oscuro ? "Cambiar a modo claro" : "Cambiar a modo oscuro");
    botonTema.querySelector(".sol").classList.toggle("oculto", !oscuro);
    botonTema.querySelector(".luna").classList.toggle("oculto", oscuro);
  }
  if (botonTema) {
    botonTema.addEventListener("click", function () {
      var nuevo = temaActual() === "dark" ? "light" : "dark";
      raiz.setAttribute("data-theme", nuevo);
      guardar("myd-tema", nuevo);
      pintarTema();
    });
    pintarTema();
  }

  /* ---------- 4. Menú móvil y cabecera flotante ---------- */
  var botonMenu = d.getElementById("menu"), nav = d.getElementById("nav");
  if (botonMenu && nav) {
    botonMenu.addEventListener("click", function () {
      var abierto = nav.classList.toggle("abierto");
      botonMenu.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
    d.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("abierto")) {
        nav.classList.remove("abierto"); botonMenu.setAttribute("aria-expanded", "false"); botonMenu.focus();
      }
    });
  }
  var cab = d.getElementById("cabecera");
  if (cab) {
    var marcarCab = function () { cab.classList.toggle("flotante", w.scrollY > 60); };
    w.addEventListener("scroll", marcarCab, { passive: true });
    marcarCab();
  }

  /* ---------- 5. Lectura: barra de progreso e índice activo ---------- */
  var barra = d.querySelector(".barra-lectura"), prosa = d.querySelector(".prosa");
  var enlacesIndice = Array.prototype.slice.call(d.querySelectorAll(".indice a"));
  var titulos = enlacesIndice.map(function (a) { return d.getElementById(a.getAttribute("href").slice(1)); });
  function alDesplazar() {
    if (barra && prosa) {
      var r = prosa.getBoundingClientRect(), total = r.height - w.innerHeight * 0.6;
      barra.style.width = (Math.min(1, Math.max(0, -r.top / (total > 0 ? total : 1))) * 100).toFixed(1) + "%";
    }
    if (enlacesIndice.length) {
      var actual = 0;
      titulos.forEach(function (h, i) { if (h && h.getBoundingClientRect().top < 140) actual = i; });
      enlacesIndice.forEach(function (a, i) { a.classList.toggle("activo", i === actual); });
    }
  }
  if (barra || enlacesIndice.length) { w.addEventListener("scroll", alDesplazar, { passive: true }); alDesplazar(); }

  /* ---------- 6. Quiz de cada entrada ---------- */
  d.querySelectorAll("form.quiz").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var preguntas = form.querySelectorAll("fieldset"), aciertos = 0;
      preguntas.forEach(function (fs) {
        var c = fs.getAttribute("data-c"), elegida = fs.querySelector("input:checked");
        fs.querySelectorAll("label").forEach(function (l) { l.classList.remove("ok", "mal"); });
        fs.querySelector('input[value="' + c + '"]').parentNode.classList.add("ok");
        if (elegida && elegida.value === c) aciertos++; else if (elegida) elegida.parentNode.classList.add("mal");
        fs.querySelector(".explica").classList.remove("oculto");
      });
      form.querySelector(".resultado").textContent = aciertos + " de " + preguntas.length + (aciertos === preguntas.length ? " · ¡Señal perfecta!" : " · Revisa las explicaciones");
    });
  });

  /* ---------- 7. Copiar enlace ---------- */
  d.querySelectorAll("[data-copiar]").forEach(function (b) {
    b.addEventListener("click", function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(location.href).then(function () {
        var t = b.textContent; b.textContent = "¡Copiado!"; setTimeout(function () { b.textContent = t; }, 1800);
      }, function () {});
    });
  });

  /* ---------- 8. Pestañas genéricas (guía de canales y pantalla) ---------- */
  function pestanas(lista, alCambiar) {
    var tabs = Array.prototype.slice.call(lista.querySelectorAll('[role="tab"]'));
    function activar(i, enfocar) {
      tabs.forEach(function (t, j) {
        var sel = i === j;
        t.setAttribute("aria-selected", sel ? "true" : "false");
        t.tabIndex = sel ? 0 : -1;
        d.getElementById(t.getAttribute("aria-controls")).hidden = !sel;
      });
      var cont = lista, t = tabs[i];
      if (t.offsetLeft < cont.scrollLeft || t.offsetLeft + t.offsetWidth > cont.scrollLeft + cont.clientWidth) {
        cont.scrollTo({ left: t.offsetLeft - 8, behavior: sinMovimiento ? "auto" : "smooth" });
      }
      if (enfocar) t.focus();
      if (alCambiar) alCambiar(i, tabs.length);
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { activar(i, false); });
      t.addEventListener("keydown", function (e) {
        var n = tabs.length, mapa = { ArrowRight: (i + 1) % n, ArrowLeft: (i - 1 + n) % n, Home: 0, End: n - 1 };
        if (e.key in mapa) { e.preventDefault(); activar(mapa[e.key], true); }
      });
    });
    return { activar: activar, total: tabs.length, actual: function () { return tabs.findIndex(function (t) { return t.getAttribute("aria-selected") === "true"; }); } };
  }

  var segmentos = d.querySelector(".segmentos[role='tablist']");
  if (segmentos) {
    var num = d.getElementById("explorador-num");
    pestanas(segmentos, function (i, n) { if (num) num.textContent = dos(i + 1) + " / " + dos(n); });
  }

  /* ---------- 9. Pantalla «En emisión»: rotación con progreso y pausa ---------- */
  var pantalla = d.querySelector("[data-carrusel]");
  if (pantalla) {
    var listaCanales = pantalla.querySelector(".canales");
    var botonPausa = pantalla.querySelector(".pausa");
    var DURACION = 6500, inicio = 0, acumulado = 0, pausadoUsuario = sinMovimiento, pausadoTemporal = false, rafId = 0;
    var ctl = pestanas(listaCanales, function () { acumulado = 0; inicio = performance.now(); pintarAvance(0); });
    function pintarAvance(p) {
      var sel = listaCanales.querySelector('[aria-selected="true"]');
      if (sel) sel.style.setProperty("--avance", p.toFixed(3));
    }
    function corriendo() { return !pausadoUsuario && !pausadoTemporal && !d.hidden; }
    function bucle(ahora) {
      if (corriendo()) {
        var p = (acumulado + (ahora - inicio)) / DURACION;
        if (p >= 1) { ctl.activar((ctl.actual() + 1) % ctl.total, false); }
        else pintarAvance(p);
      }
      rafId = requestAnimationFrame(bucle);
    }
    function congelar() { if (corriendo()) acumulado += performance.now() - inicio; }
    function reanudar() { inicio = performance.now(); }
    function pintarPausa() {
      botonPausa.setAttribute("aria-pressed", pausadoUsuario ? "true" : "false");
      botonPausa.setAttribute("aria-label", pausadoUsuario ? "Reanudar la rotación" : "Pausar la rotación");
    }
    botonPausa.addEventListener("click", function () {
      if (!pausadoUsuario) { congelar(); pausadoUsuario = true; } else { pausadoUsuario = false; reanudar(); }
      pintarPausa();
    });
    pantalla.addEventListener("mouseenter", function () { congelar(); pausadoTemporal = true; });
    pantalla.addEventListener("mouseleave", function () { pausadoTemporal = false; reanudar(); });
    pantalla.addEventListener("focusin", function () { congelar(); pausadoTemporal = true; });
    pantalla.addEventListener("focusout", function () { pausadoTemporal = false; reanudar(); });
    d.addEventListener("visibilitychange", function () { if (!d.hidden) reanudar(); });
    pintarPausa();
    inicio = performance.now();
    rafId = requestAnimationFrame(bucle);
  }

  /* ---------- 10. Historia: palabras que se encienden al hacer scroll ---------- */
  var historia = d.querySelector("[data-palabras]");
  if (historia) {
    var claves = ["long", "tail", "quiz", "IronBites:", "intención."];
    var palabras = historia.textContent.trim().split(/\s+/);
    historia.innerHTML = palabras.map(function (p) {
      var esClave = claves.indexOf(p.replace(/[«»,]/g, "")) !== -1 || claves.indexOf(p) !== -1;
      return '<span class="palabra' + (esClave ? " clave" : "") + '">' + esc(p) + "</span>";
    }).join(" ");
    var spans = historia.querySelectorAll(".palabra");
    var encender = function () {
      var r = historia.getBoundingClientRect(), vh = w.innerHeight;
      var p = sinMovimiento ? 1 : Math.min(1, Math.max(0, (vh * 0.85 - r.top) / (r.height + vh * 0.35)));
      var n = Math.round(p * spans.length);
      spans.forEach(function (s, i) { s.classList.toggle("on", i < n); });
    };
    w.addEventListener("scroll", encender, { passive: true });
    encender();
  }

  /* ---------- 11. Filtros del blog ---------- */
  var listaBlog = d.getElementById("lista-blog");
  if (listaBlog) {
    var tarjetas = Array.prototype.slice.call(listaBlog.querySelectorAll(".tarjeta"));
    var campo = d.getElementById("buscar");
    var botones = Array.prototype.slice.call(d.querySelectorAll("#chips-cat button"));
    var contador = d.getElementById("contador"), vacio = d.getElementById("vacio");
    var params = new URLSearchParams(location.search);
    var cat = params.get("cat") || "todas";
    if (params.get("q")) campo.value = params.get("q");
    var aplicar = function () {
      var q = norm(campo.value.trim()), n = 0;
      tarjetas.forEach(function (t) {
        var ver = (cat === "todas" || t.getAttribute("data-cat") === cat) && (!q || norm(t.getAttribute("data-texto")).indexOf(q) !== -1);
        t.classList.toggle("oculto", !ver);
        if (ver) n++;
      });
      botones.forEach(function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-cat") === cat ? "true" : "false"); });
      contador.textContent = n === 1 ? "1 entrada" : n + " entradas";
      vacio.classList.toggle("oculto", n !== 0);
      var url = new URL(location.href);
      if (cat !== "todas") url.searchParams.set("cat", cat); else url.searchParams.delete("cat");
      if (campo.value.trim()) url.searchParams.set("q", campo.value.trim()); else url.searchParams.delete("q");
      history.replaceState(null, "", url);
    };
    botones.forEach(function (b) { b.addEventListener("click", function () { cat = b.getAttribute("data-cat"); aplicar(); }); });
    campo.addEventListener("input", aplicar);
    aplicar();
  }

  /* ---------- 12. Buscador del glosario ---------- */
  var campoGlosario = d.getElementById("buscar-termino");
  if (campoGlosario) {
    var terminos = Array.prototype.slice.call(d.querySelectorAll(".termino"));
    var grupos = Array.prototype.slice.call(d.querySelectorAll(".glosario .grupo"));
    var contadorG = d.getElementById("contador-glosario");
    campoGlosario.addEventListener("input", function () {
      var q = norm(campoGlosario.value.trim()), n = 0;
      terminos.forEach(function (t) { var ver = !q || norm(t.textContent).indexOf(q) !== -1; t.classList.toggle("oculto", !ver); if (ver) n++; });
      grupos.forEach(function (g) { g.classList.toggle("oculto", !g.querySelector(".termino:not(.oculto)")); });
      contadorG.textContent = n + (n === 1 ? " término" : " términos");
    });
  }

  /* ---------- 13. Guía «¿Qué repaso?» (3 preguntas → plan de estudio) ---------- */
  var dialogo = d.getElementById("guia"), cuerpoGuia = d.getElementById("guia-cuerpo");
  var datosEl = d.getElementById("datos-sitio");
  var DATOS = null;
  try { DATOS = JSON.parse(datosEl ? datosEl.textContent : "null"); } catch (e) { DATOS = null; }

  if (dialogo && cuerpoGuia && DATOS && typeof dialogo.showModal === "function") {
    var resp = {};
    var dial = dialogo.querySelector(".guia-dial i");
    var girar = function (paso) { if (dial) dial.style.setProperty("--giro", (-60 + paso * 45) + "deg"); };

    var PREGUNTAS = [
      { id: "meta", t: "¿Para qué estás repasando?", o: [
        ["examen", "Un examen", "Conceptos clave y quizzes"],
        ["expo", "La exposición final", "El caso IronBites de principio a fin"],
        ["tema", "Entender un tema", "Ir a fondo en una unidad"],
        ["general", "Repaso general", "Un poco de todo el curso"]] },
      { id: "cat", t: "¿Qué unidad te cuesta más?", o: Object.keys(DATOS.cats).filter(function (k) { return k !== "repaso"; })
          .map(function (k) { return [k, "CH " + dos(DATOS.cats[k].ch) + " · " + DATOS.cats[k].n, ""]; }).concat([["ninguna", "No sé / todas por igual", ""]]), dos: true },
      { id: "min", t: "¿Cuánto tiempo tienes?", o: [["15", "15 minutos", "Lo esencial"], ["30", "30 minutos", "Lo esencial y un poco más"], ["60", "1 hora o más", "Repaso completo"]] }
    ];

    var pintarInicio = function () {
      girar(0);
      cuerpoGuia.innerHTML =
        '<h2 id="guia-titulo">Hola. ¿Cómo te llamas?</h2>' +
        '<p class="guia-sub">Responde tres preguntas y te armamos un plan de repaso con las entradas justas.</p>' +
        '<form class="guia-fila" id="guia-nombre-form"><label class="sr-only" for="guia-nombre">Tu nombre</label>' +
        '<input id="guia-nombre" autofocus maxlength="40" autocomplete="given-name" placeholder="Por ejemplo: Daniela" value="' + esc(resp.nombre || "") + '">' +
        '<button class="btn" type="submit">Empezar</button></form>' +
        '<p class="guia-legal">Es opcional. No lo guardamos: solo aparece en tu plan si decides enviarlo.</p>';
      var f = d.getElementById("guia-nombre-form");
      f.addEventListener("submit", function (e) { e.preventDefault(); resp.nombre = d.getElementById("guia-nombre").value.trim(); pintarPregunta(0); });
      setTimeout(function () { var i = d.getElementById("guia-nombre"); if (i) i.focus(); }, 30);
    };

    var pintarPregunta = function (n) {
      var q = PREGUNTAS[n];
      girar(n + 1);
      cuerpoGuia.innerHTML =
        '<p class="guia-paso">Pregunta ' + (n + 1) + " de " + PREGUNTAS.length + "</p>" +
        '<div class="guia-barra"><i style="width:' + ((n + 1) / PREGUNTAS.length * 100) + '%"></i></div>' +
        '<h2 id="guia-titulo">' + esc(q.t) + "</h2>" +
        '<div class="guia-opciones' + (q.dos ? " dos" : "") + '">' +
        q.o.map(function (o) { return '<button type="button" class="guia-opcion" data-v="' + esc(o[0]) + '"><span>' + esc(o[1]) + (o[2] ? "<small>" + esc(o[2]) + "</small>" : "") + "</span></button>"; }).join("") +
        "</div>" +
        '<button type="button" class="guia-volver" id="guia-atras">← Volver</button>';
      cuerpoGuia.querySelectorAll(".guia-opcion").forEach(function (b) {
        b.addEventListener("click", function () {
          resp[q.id] = b.getAttribute("data-v");
          if (n + 1 < PREGUNTAS.length) pintarPregunta(n + 1); else pintarPlan();
        });
      });
      d.getElementById("guia-atras").addEventListener("click", function () { if (n === 0) pintarInicio(); else pintarPregunta(n - 1); });
      var primero = cuerpoGuia.querySelector(".guia-opcion"); if (primero) primero.focus();
    };

    var armarPlan = function () {
      var posts = DATOS.posts.slice(), limite = parseInt(resp.min, 10) || 30;
      var elegidos = [], suma = 0;
      var agregar = function (p) { if (p && elegidos.indexOf(p) === -1 && (suma + p.m <= limite || elegidos.length === 0)) { elegidos.push(p); suma += p.m; } };
      var deCat = function (k) { return posts.filter(function (p) { return p.c === k; }); };
      var porSlug = function (s) { return posts.filter(function (p) { return p.s === s; })[0]; };
      if (resp.meta === "expo") { agregar(porSlug("plan-de-comunicaciones-integradas-caso-ironbites")); }
      if (resp.meta === "examen" || resp.meta === "general") { agregar(porSlug("repaso-comunicaciones-de-marketing-semanas-1-a-5")); }
      if (resp.cat && resp.cat !== "ninguna") deCat(resp.cat).forEach(agregar);
      if (resp.meta === "tema" && resp.cat && resp.cat !== "ninguna") {
        posts.filter(function (p) { return p.c === resp.cat; }).forEach(agregar);
      }
      // completar con una entrada por unidad (en orden del curso) hasta llenar el tiempo
      var vistas = {};
      posts.forEach(function (p) { if (!vistas[p.c]) { vistas[p.c] = true; agregar(p); } });
      posts.forEach(agregar);
      var semanas = elegidos.map(function (p) { return p.w; });
      var terms = DATOS.terms.filter(function (t) { return semanas.indexOf(t.w) !== -1; }).slice(0, 6).map(function (t) { return t.t; });
      return { posts: elegidos, minutos: suma, terms: terms };
    };

    var pintarPlan = function () {
      girar(4);
      var plan = armarPlan();
      var urlAbs = function (slug) { return new URL(RAIZ + "entradas/" + slug + ".html", location.href).href; };
      var nombre = resp.nombre ? ", " + resp.nombre : "";
      var lista = plan.posts.map(function (p, i) {
        return '<li><b>' + dos(i + 1) + '</b><a href="' + esc(RAIZ + "entradas/" + p.s + ".html") + '">' + esc(p.t) + "</a><span>" + p.m + " min</span></li>";
      }).join("");
      var texto = "Mi plan de repaso" + (resp.nombre ? " (" + resp.nombre + ")" : "") + " · Mix & Medios\n" +
        plan.posts.map(function (p, i) { return (i + 1) + ". " + p.t + " (" + p.m + " min) " + urlAbs(p.s); }).join("\n") +
        (plan.terms.length ? "\nTérminos para repasar: " + plan.terms.join(", ") : "") +
        "\nTiempo total: " + plan.minutos + " min. Al final de cada entrada hay un quiz de 3 preguntas.";
      cuerpoGuia.innerHTML =
        '<p class="guia-paso">Tu plan está listo</p>' +
        '<h2 id="guia-titulo">Tu plan de repaso' + esc(nombre) + "</h2>" +
        '<p class="guia-sub">' + plan.posts.length + " entradas · unos " + plan.minutos + " minutos de lectura, más el quiz de cada una.</p>" +
        '<ol class="guia-plan">' + lista + "</ol>" +
        (plan.terms.length ? '<p class="guia-terminos"><strong>Términos para repasar:</strong> ' + esc(plan.terms.join(", ")) + "</p>" : "") +
        '<div class="guia-acciones">' +
        '<a class="btn" href="' + esc(RAIZ + "entradas/" + plan.posts[0].s + ".html") + '">Empezar a leer</a>' +
        '<a class="btn guia-wa" target="_blank" rel="noopener" href="https://wa.me/?text=' + encodeURIComponent(texto) + '">Enviar mi plan por WhatsApp</a>' +
        "</div>" +
        '<p class="guia-legal">Se abrirá WhatsApp con tu plan preparado. Podrás revisarlo y elegir a quién enviarlo.</p>' +
        '<button type="button" class="guia-volver" id="guia-reiniciar">Volver a empezar</button>';
      d.getElementById("guia-reiniciar").addEventListener("click", function () { resp = { nombre: resp.nombre }; pintarInicio(); });
    };

    var abrirGuia = function () {
      var pista = d.getElementById("guia-pista"); if (pista) pista.hidden = true;
      if (!dialogo.open) { pintarInicio(); dialogo.showModal(); var campoNombre = d.getElementById("guia-nombre"); if (campoNombre) campoNombre.focus(); }
    };
    d.querySelectorAll("[data-abrir-guia]").forEach(function (b) { b.addEventListener("click", abrirGuia); });
    dialogo.addEventListener("click", function (e) { if (e.target === dialogo) dialogo.close(); });

    // Pista la primera vez en la sesión
    if (!leer("myd-pista", sessionStorage)) {
      var pista = d.getElementById("guia-pista"), botonGuia = d.querySelector(".guia-boton");
      setTimeout(function () {
        if (!pista || (dialogo && dialogo.open)) return;
        pista.hidden = false; if (botonGuia) botonGuia.classList.add("llamando");
        guardar("myd-pista", "1", sessionStorage);
        setTimeout(function () { pista.hidden = true; if (botonGuia) botonGuia.classList.remove("llamando"); }, 5200);
      }, raiz.classList.contains("intro-on") ? 2400 : 1200);
    }
  } else {
    // Sin <dialog>: el botón lleva al blog
    d.querySelectorAll("[data-abrir-guia]").forEach(function (b) { b.addEventListener("click", function () { location.href = RAIZ + "blog.html"; }); });
  }

  /* ---------- Año del pie ---------- */
  var anio = d.getElementById("anio");
  if (anio) anio.textContent = new Date().getFullYear();
})();
