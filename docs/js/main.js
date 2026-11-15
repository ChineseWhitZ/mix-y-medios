/* Mix & Medios — interacciones del sitio (sin librerías) */
(function () {
  "use strict";

  var raiz = document.documentElement;

  function leer(clave) { try { return localStorage.getItem(clave); } catch (e) { return null; } }
  function guardar(clave, valor) { try { localStorage.setItem(clave, valor); } catch (e) { /* sin almacenamiento */ } }

  /* ---------- Modo oscuro ---------- */
  var botonTema = document.getElementById("tema");
  function temaActual() {
    var t = raiz.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function pintarBotonTema() {
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
      pintarBotonTema();
    });
    pintarBotonTema();
  }

  /* ---------- Menú móvil ---------- */
  var botonMenu = document.getElementById("menu");
  var nav = document.getElementById("nav");
  if (botonMenu && nav) {
    botonMenu.addEventListener("click", function () {
      var abierto = nav.classList.toggle("abierto");
      botonMenu.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("abierto")) {
        nav.classList.remove("abierto");
        botonMenu.setAttribute("aria-expanded", "false");
        botonMenu.focus();
      }
    });
  }

  /* ---------- Barra de lectura e índice activo ---------- */
  var barra = document.querySelector(".barra-lectura");
  var prosa = document.querySelector(".prosa");
  var enlacesIndice = Array.prototype.slice.call(document.querySelectorAll(".indice a"));
  var titulos = enlacesIndice.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
  function alDesplazar() {
    if (barra && prosa) {
      var r = prosa.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var avance = Math.min(1, Math.max(0, -r.top / (total > 0 ? total : 1)));
      barra.style.width = (avance * 100).toFixed(1) + "%";
    }
    if (enlacesIndice.length) {
      var actual = 0;
      titulos.forEach(function (h, i) { if (h && h.getBoundingClientRect().top < 140) actual = i; });
      enlacesIndice.forEach(function (a, i) { a.classList.toggle("activo", i === actual); });
    }
  }
  if (barra || enlacesIndice.length) {
    window.addEventListener("scroll", alDesplazar, { passive: true });
    alDesplazar();
  }

  /* ---------- Quiz ---------- */
  document.querySelectorAll("form.quiz").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var preguntas = form.querySelectorAll("fieldset");
      var aciertos = 0;
      preguntas.forEach(function (fs) {
        var correcta = fs.getAttribute("data-c");
        var elegida = fs.querySelector("input:checked");
        fs.querySelectorAll("label").forEach(function (l) { l.classList.remove("ok", "mal"); });
        var labelCorrecta = fs.querySelector('input[value="' + correcta + '"]').parentNode;
        labelCorrecta.classList.add("ok");
        if (elegida && elegida.value === correcta) aciertos++;
        else if (elegida) elegida.parentNode.classList.add("mal");
        fs.querySelector(".explica").classList.remove("oculto");
      });
      var res = form.querySelector(".resultado");
      res.textContent = aciertos + " de " + preguntas.length + (aciertos === preguntas.length ? " · ¡Perfecto!" : " · Revisa las explicaciones");
    });
  });

  /* ---------- Copiar enlace ---------- */
  document.querySelectorAll("[data-copiar]").forEach(function (b) {
    b.addEventListener("click", function () {
      var hecho = function () { var t = b.textContent; b.textContent = "¡Enlace copiado!"; setTimeout(function () { b.textContent = t; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(location.href).then(hecho, function () {});
    });
  });

  /* ---------- Normalizar texto para búsquedas ---------- */
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }

  /* ---------- Filtros del blog ---------- */
  var listaBlog = document.getElementById("lista-blog");
  if (listaBlog) {
    var tarjetas = Array.prototype.slice.call(listaBlog.querySelectorAll(".tarjeta"));
    var campo = document.getElementById("buscar");
    var botones = Array.prototype.slice.call(document.querySelectorAll("#chips-cat button"));
    var contador = document.getElementById("contador");
    var vacio = document.getElementById("vacio");
    var params = new URLSearchParams(location.search);
    var cat = params.get("cat") || "todas";
    if (params.get("q")) campo.value = params.get("q");

    function aplicar() {
      var q = norm(campo.value.trim());
      var n = 0;
      tarjetas.forEach(function (t) {
        var okCat = cat === "todas" || t.getAttribute("data-cat") === cat;
        var okTxt = !q || norm(t.getAttribute("data-texto")).indexOf(q) !== -1;
        var ver = okCat && okTxt;
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
    }
    botones.forEach(function (b) { b.addEventListener("click", function () { cat = b.getAttribute("data-cat"); aplicar(); }); });
    campo.addEventListener("input", aplicar);
    aplicar();
  }

  /* ---------- Búsqueda del glosario ---------- */
  var campoGlosario = document.getElementById("buscar-termino");
  if (campoGlosario) {
    var terminos = Array.prototype.slice.call(document.querySelectorAll(".termino"));
    var grupos = Array.prototype.slice.call(document.querySelectorAll(".glosario .grupo"));
    var contadorG = document.getElementById("contador-glosario");
    campoGlosario.addEventListener("input", function () {
      var q = norm(campoGlosario.value.trim());
      var n = 0;
      terminos.forEach(function (t) {
        var ver = !q || norm(t.textContent).indexOf(q) !== -1;
        t.classList.toggle("oculto", !ver);
        if (ver) n++;
      });
      grupos.forEach(function (g) { g.classList.toggle("oculto", !g.querySelector(".termino:not(.oculto)")); });
      contadorG.textContent = n + (n === 1 ? " término" : " términos");
    });
  }

  /* ---------- Cabecera flotante sobre el hero ---------- */
  var cab = document.getElementById("cabecera");
  if (cab && cab.classList.contains("sobre-hero")) {
    var hero = document.querySelector(".hero-foto");
    var marcarCab = function () {
      var limite = hero ? hero.offsetTop + 40 : 80;
      cab.classList.toggle("flotante", window.scrollY > limite);
    };
    window.addEventListener("scroll", marcarCab, { passive: true });
    marcarCab();
  }

  /* ---------- Explorador por unidades (pestañas segmentadas) ---------- */
  var lista = document.querySelector('.segmentos[role="tablist"]');
  if (lista) {
    var tabs = Array.prototype.slice.call(lista.querySelectorAll('[role="tab"]'));
    var num = document.getElementById("explorador-num");
    var activar = function (i, enfocar) {
      tabs.forEach(function (t, j) {
        var sel = i === j;
        t.setAttribute("aria-selected", sel ? "true" : "false");
        t.tabIndex = sel ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !sel;
      });
      if (num) num.textContent = String(i + 1).padStart(2, "0") + " / " + String(tabs.length).padStart(2, "0");
      tabs[i].scrollIntoView({ block: "nearest", inline: "nearest" });
      if (enfocar) tabs[i].focus();
    };
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { activar(i, false); });
      t.addEventListener("keydown", function (e) {
        var n = tabs.length;
        if (e.key === "ArrowRight") { e.preventDefault(); activar((i + 1) % n, true); }
        if (e.key === "ArrowLeft") { e.preventDefault(); activar((i - 1 + n) % n, true); }
        if (e.key === "Home") { e.preventDefault(); activar(0, true); }
        if (e.key === "End") { e.preventDefault(); activar(n - 1, true); }
      });
    });
  }

  /* ---------- Año del pie ---------- */
  var anio = document.getElementById("anio");
  if (anio) anio.textContent = new Date().getFullYear();
})();
