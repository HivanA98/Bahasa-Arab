/* ============================================================
   Latihan Bahasa Arab Fusha — app.js

   Data dimuat dari webdata.js (global ARAB_DATA), bukan lewat fetch(),
   sehingga aplikasi jalan di GitHub Pages maupun saat index.html dibuka
   langsung dari berkas (file://).

   Penjadwalan memakai lima kotak Leitner, sama seperti quiz.py. Progres
   disimpan di localStorage peramban dan tidak dikirim ke mana pun.
   ============================================================ */

"use strict";

/* ---------------------------------------------------- penyimpanan ---- */

const LS = { prog: "arab.progress.v1", prefs: "arab.prefs.v1", theme: "arab.theme" };

function lsGet(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch { return fallback; }
}
function lsSet(key, val) {
  try { localStorage.setItem(key, JSON.stringify(val)); } catch { /* mode privat */ }
}

/* Jeda ulangan per kotak, dalam hari. Sama dengan INTERVALS di
   arabdrill/leitner.py; ubah keduanya bila ingin jadwal lain. */
const BOX_DAYS = { 1: 0, 2: 1, 3: 3, 4: 7, 5: 16 };
const MAX_BOX = 5;

const progress = lsGet(LS.prog, { cards: {} });
if (!progress.cards) progress.cards = {};

const prefs = Object.assign(
  { translit: false, harakat: false, arah: false, due: false, hide: false },
  lsGet(LS.prefs, {})
);

function todayISO() {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function addDays(iso, n) {
  const d = new Date(iso + "T00:00:00");
  d.setDate(d.getDate() + n);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}
function stateOf(id) { return progress.cards[id] || null; }
function boxOf(id) { const s = stateOf(id); return s ? s.box : 0; }
function isDue(id) {
  const s = stateOf(id);
  if (!s) return true;                 // kartu baru selalu dianggap jatuh tempo
  return s.due <= todayISO();
}
function grade(id, ok) {
  const s = stateOf(id) || { box: 1, due: todayISO(), seen: 0, right: 0 };
  s.seen += 1;
  if (ok) { s.right += 1; s.box = Math.min(s.box + 1, MAX_BOX); }
  else { s.box = 1; }
  s.due = addDays(todayISO(), BOX_DAYS[s.box]);
  progress.cards[id] = s;
  lsSet(LS.prog, progress);
}

/* ---------------------------------------------------------- utilitas ---- */

const $ = (sel) => document.querySelector(sel);
const esc = (s) => String(s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

const HARAKAT = /[ً-ْٰ]/g;
const strip = (s) => s.replace(HARAKAT, "");

function ar(text, size) {
  return `<div class="ar ${size || "ar-lg"}" dir="rtl" lang="ar">${esc(text)}</div>`;
}
function tr(text) {
  return prefs.translit && text ? `<div class="tr">${esc(text)}</div>` : "";
}
/* Alih huruf hanya berguna untuk teks berharakat; teks gundul menghasilkan
   deretan konsonan yang justru membingungkan. */
function trIf(text, source) {
  return HARAKAT.test(source) ? tr(text) : "";
}

/* ----------------------------------------------------- pembuat kartu ---- */

const D = typeof ARAB_DATA !== "undefined" ? ARAB_DATA : null;

const MODES = {
  kosakata: {
    label: "Kosakata",
    toggles: ["harakat", "arah"],
    items: () => D.kosakata,
    search: (x) => [x.ar, x.bare, x.tr, x.gloss, x.root, x.detail].concat(x.alt).join(" "),
    kind: () => "flip",
    front(x) {
      if (prefs.arah) {
        return `<div class="id-xl">${esc(x.gloss)}</div>
                <div class="tr">${esc(x.pos)}</div>`;
      }
      const teks = prefs.harakat ? x.bare : x.ar;
      return ar(teks, "ar-xl") + trIf(x.tr, teks);
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        <div class="detail">${esc(x.detail)}${x.root ? " · akar: " + esc(x.root) : ""}</div>
        ${prefs.arah ? ar(x.ar, "ar-lg") + tr(x.tr) : ""}
        <hr class="sep" />
        <div class="example">${ar(x.exAr, "ar-md")}${tr(x.exTr)}
          <div class="gloss">${esc(x.exGloss)}</div></div>
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}
        ${x.rootNote ? `<div class="note">${esc(x.rootNote)}</div>` : ""}`;
    },
  },

  tatabahasa: {
    label: "Tata bahasa",
    toggles: [],
    items: () => D.tatabahasa,
    search: (x) => [x.prompt, x.promptAr, x.catLabel].concat(x.options).join(" "),
    kind: () => "mcq",
    front(x) {
      return `<div class="prompt">${esc(x.prompt)}</div>
        ${x.promptAr ? ar(x.promptAr, "ar-lg") + trIf(x.tr || "", x.promptAr) : ""}`;
    },
    back(x) {
      return `<div class="detail">${esc(x.catLabel)}</div>
        <div class="meaning">${x.optionsLang === "ar"
          ? `<span class="ar ar-md" dir="rtl" lang="ar">${esc(x.options[x.answer])}</span>`
          : esc(x.options[x.answer])}</div>
        ${x.explain ? `<div class="note">${esc(x.explain)}</div>` : ""}`;
    },
  },

  akar: {
    label: "Akar kata",
    toggles: ["harakat"],
    items: () => D.akar,
    search: (x) => [x.ar, x.bare, x.tr, x.gloss, x.root, x.pattern, x.rootMeaning].join(" "),
    kind: () => "flip",
    front(x) {
      const teks = prefs.harakat ? x.bare : x.ar;
      return ar(teks, "ar-xl") + trIf(x.tr, teks) +
        `<div class="hint" style="position:static;margin-top:10px">Apa akarnya, dan apa polanya?</div>`;
    },
    back(x) {
      return `<div class="meaning">${esc(x.gloss)}</div>
        <dl class="kv">
          <dt>Akar</dt><dd><span class="ar ar-sm" dir="rtl">${esc(x.root)}</span> — ${esc(x.rootMeaning)}</dd>
          <dt>Pola</dt><dd><span class="ar ar-sm" dir="rtl">${esc(x.pattern)}</span></dd>
        </dl>
        ${x.siblings.length ? `<div class="sibs">Sekeluarga: ${
          x.siblings.map((s) => `<span class="ar" dir="rtl">${esc(s)}</span>`).join(" · ")
        }</div>` : ""}
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },

  baca: {
    label: "Baca tanpa harakat",
    toggles: [],
    items: () => D.baca,
    search: (x) => [x.l1, x.l3, x.gloss, x.catLabel].join(" "),
    kind: (x) => (x.kind === "soal" ? "mcq" : "flip"),
    front(x) {
      if (x.kind === "soal") {
        return ar(x.shown, "ar-lg") +
          (x.targetBare
            ? `<div class="tr">kata yang ditanyakan: <span class="ar ar-sm" dir="rtl">${esc(x.targetBare)}</span></div>`
            : `<div class="tr">Apa arti kalimat ini?</div>`);
      }
      const teks = x.level === 1 ? x.l1 : x.level === 2 ? x.l2 : x.l3;
      return ar(teks, "ar-lg") +
        `<div class="hint" style="position:static;margin-top:10px">Baca dengan suara, tentukan harakatnya, lalu buka jawabannya</div>`;
    },
    back(x) {
      const glosses = (x.optionGlosses || []).length
        ? `<div class="note">Semua bacaan yang mungkin: ${x.options.map((o, i) =>
            `<span class="ar ar-sm" dir="rtl">${esc(o)}</span> = ${esc(x.optionGlosses[i])}`).join("; ")}</div>`
        : "";
      return ar(x.l1, "ar-lg") + tr(x.tr) +
        `<div class="gloss detail">${esc(x.gloss)}</div>
        ${x.explain ? `<div class="note">${esc(x.explain)}</div>` : ""}${glosses}`;
    },
  },

  quran: {
    label: "Qur'an & MSA",
    toggles: ["harakat"],
    items: () => D.quran,
    search: (x) => [x.ar, x.bare, x.tr, x.classical, x.msa, x.kind, x.root].join(" "),
    kind: () => "flip",
    front(x) {
      const teks = prefs.harakat ? x.bare : x.ar;
      return ar(teks, "ar-xl") + trIf(x.tr, teks) +
        `<div class="hint" style="position:static;margin-top:10px">Apa bedanya makna klasik dan makna MSA?</div>`;
    },
    back(x) {
      return `<dl class="kv">
          <dt>MSA</dt><dd><strong>${esc(x.msa)}</strong></dd>
          <dt>Arab klasik</dt><dd>${esc(x.classical)}</dd>
          <dt>Jenis</dt><dd>${esc(x.kind)}</dd>
          ${x.root ? `<dt>Akar</dt><dd><span class="ar ar-sm" dir="rtl">${esc(x.root)}</span></dd>` : ""}
        </dl>
        ${x.note ? `<div class="note">${esc(x.note)}</div>` : ""}`;
    },
  },
};

/* ------------------------------------------------------------ keadaan ---- */

let mode = "kosakata";
let deck = [];
let index = 0;
let activeCat = "*";
let activeStage = 0;
let query = "";
let shuffled = false;
let answered = false;

const els = {
  tabs: $("#tabs"), chips: $("#chips"), stages: $("#stages"), search: $("#search"),
  card: $("#card"), badge: $("#badge"), box: $("#box"), front: $("#front"),
  back: $("#back"), choices: $("#choices"), hint: $("#hint"),
  counter: $("#counter"), fill: $("#fill"), grade: $("#grade"),
  stats: $("#stats"), panel: $("#panel"),
};

/* ------------------------------------------------------------ susunan ---- */

function allItems() { return MODES[mode].items(); }

function buildDeck() {
  const cfg = MODES[mode];
  const q = query.trim().toLowerCase();
  deck = allItems().filter((x) => {
    if (activeCat !== "*" && x.cat !== activeCat) return false;
    if (activeStage && x.stage > activeStage) return false;
    if (prefs.due && !isDue(x.id)) return false;
    if (prefs.hide && boxOf(x.id) >= MAX_BOX) return false;
    if (q && !cfg.search(x).toLowerCase().includes(q)) return false;
    return true;
  });
  if (shuffled) {
    for (let i = deck.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
  }
  if (index >= deck.length) index = 0;
}

function renderChips() {
  const seen = new Map();
  for (const x of allItems()) {
    if (activeStage && x.stage > activeStage) continue;
    const prev = seen.get(x.cat) || { label: x.catLabel, n: 0 };
    prev.n += 1;
    seen.set(x.cat, prev);
  }
  const total = allItems().filter((x) => !activeStage || x.stage <= activeStage).length;
  let html = `<button data-cat="*" aria-pressed="${activeCat === "*"}">Semua<span class="n">${total}</span></button>`;
  for (const [cat, info] of seen) {
    html += `<button data-cat="${esc(cat)}" aria-pressed="${activeCat === cat}">${esc(info.label)}<span class="n">${info.n}</span></button>`;
  }
  els.chips.innerHTML = html;
}

function renderToggles() {
  const aktif = MODES[mode].toggles;
  $("#wrap-harakat").hidden = !aktif.includes("harakat");
  $("#wrap-arah").hidden = !aktif.includes("arah");
}

/* ------------------------------------------------------------ tampilan ---- */

function render() {
  const cfg = MODES[mode];
  els.card.classList.remove("is-flipped");
  answered = false;

  if (!deck.length) {
    els.front.innerHTML = `<p class="empty">Tidak ada kartu yang cocok dengan saringan ini.<br />
      Coba hapus pencarian, pilih "Semua tahap", atau matikan "Jatuh tempo saja".</p>`;
    els.back.innerHTML = "";
    els.choices.hidden = true;
    els.grade.hidden = true;
    els.badge.textContent = "";
    els.box.textContent = "";
    els.counter.textContent = "0 / 0";
    els.fill.style.width = "0%";
    els.hint.textContent = "";
    return;
  }

  const x = deck[index];
  const kind = cfg.kind(x);

  els.badge.textContent = `${x.catLabel || ""} · tahap ${x.stage}`;
  const b = boxOf(x.id);
  els.box.textContent = b ? `kotak ${b}${isDue(x.id) ? " · jatuh tempo" : ""}` : "belum dilatih";

  els.front.innerHTML = cfg.front(x);
  els.back.innerHTML = cfg.back(x);

  if (kind === "mcq") {
    els.choices.hidden = false;
    els.choices.innerHTML = x.options.map((o, i) => {
      const isi = x.optionsLang === "ar"
        ? `<span class="opt-ar" dir="rtl" lang="ar">${esc(o)}</span>`
        : esc(o);
      return `<button type="button" data-i="${i}"><span class="num">${i + 1}.</span>${isi}</button>`;
    }).join("");
    els.grade.hidden = true;
    els.hint.textContent = "Pilih satu jawaban (tekan 1–4)";
  } else {
    els.choices.hidden = true;
    els.choices.innerHTML = "";
    els.grade.hidden = false;
    els.hint.textContent = "Klik atau tekan Spasi untuk melihat jawaban";
  }

  els.counter.textContent = `${index + 1} / ${deck.length}`;
  els.fill.style.width = `${((index + 1) / deck.length) * 100}%`;
  renderPanel(x);
  fitCard();
}

/* Kedua sisi kartu diposisikan absolut, sehingga tingginya harus dihitung.
   Tanpa ini, kartu pilihan ganda yang panjang akan terpotong. */
function fitCard() {
  els.card.style.height = "auto";
  let h = 0;
  for (const face of els.card.querySelectorAll(".face")) {
    h = Math.max(h, face.scrollHeight);
  }
  // Sisa 4px supaya bilah gulir tidak muncul karena pembulatan.
  els.card.style.height = Math.max(300, h + 4) + "px";
}

function flip() {
  if (!deck.length) return;
  if (MODES[mode].kind(deck[index]) === "mcq" && !answered) return;
  els.card.classList.toggle("is-flipped");
}

function answer(i) {
  if (answered || !deck.length) return;
  const x = deck[index];
  if (MODES[mode].kind(x) !== "mcq") return;
  answered = true;
  const benar = i === x.answer;
  grade(x.id, benar);
  for (const btn of els.choices.querySelectorAll("button")) {
    const bi = Number(btn.dataset.i);
    btn.disabled = true;
    if (bi === x.answer) btn.classList.add("is-right");
    else if (bi === i) btn.classList.add("is-wrong");
  }
  els.hint.textContent = benar ? "Benar. Spasi untuk penjelasan." : "Belum tepat. Spasi untuk penjelasan.";
  const b = boxOf(x.id);
  els.box.textContent = `kotak ${b}`;
  renderStats();
}

function gradeFlip(ok) {
  if (!deck.length) return;
  grade(deck[index].id, ok);
  renderStats();
  next();
}

function next() { if (deck.length) { index = (index + 1) % deck.length; render(); } }
function prev() { if (deck.length) { index = (index - 1 + deck.length) % deck.length; render(); } }

/* -------------------------------------------------------------- panel ---- */

function renderPanel(x) {
  let html = "";
  if (mode === "tatabahasa") {
    const t = D.topik.find((t) => t.id === x.cat);
    if (t) {
      html = `<details open><summary>${esc(t.title)}</summary><div class="body">
        <p>${esc(t.explanation)}</p>
        ${t.examples.map((e) => `<div class="ar ar-sm" dir="rtl">${esc(e.ar)}</div>
          <p style="margin-top:-6px">${esc(e.gloss)}</p>`).join("")}
        <p><strong>Pengecualian dan catatan:</strong></p>
        ${t.caveats.map((c) => `<div class="caveat">${esc(c)}</div>`).join("")}
      </div></details>`;
    }
  } else if (mode === "akar") {
    html = `<details><summary>Daftar pola (wazan)</summary><div class="body">
      ${D.pola.map((p) => `<p><span class="ar ar-sm" dir="rtl">${esc(p.pattern)}</span>
        — <strong>${esc(p.function)}</strong><br />
        ${p.examples.map((e) => `<span class="ar ar-sm" dir="rtl">${esc(e.ar)}</span> ${esc(e.gloss)}`).join(" · ")}
        ${p.note ? `<br /><span style="opacity:.75">${esc(p.note)}</span>` : ""}</p>`).join("")}
    </div></details>`;
  } else if (mode === "baca") {
    html = `<details><summary>Tiga level membaca</summary><div class="body">
      <ul>
        <li><strong>Level 1</strong> — harakat penuh. Latihannya membaca lancar dan mengenali i'rab.</li>
        <li><strong>Level 2</strong> — harakat hanya pada kata yang menentukan. Syaddah tetap ditulis karena ia mengubah identitas huruf, bukan sekadar vokal.</li>
        <li><strong>Level 3</strong> — tanpa harakat, seperti teks Arab sehari-hari. Bacaan ditentukan oleh kedudukan kata dalam kalimat dan oleh maknanya.</li>
      </ul>
    </div></details>`;
  } else if (mode === "quran") {
    html = `<details><summary>Yang perlu diingat tentang modul ini</summary><div class="body">
      ${D.catatan.penting.map((c) => `<p>${esc(c)}</p>`).join("")}
      ${D.catatan.pemakaian.map((u) => `<p><strong>${esc(u.title)}.</strong> ${esc(u.text)}</p>`).join("")}
    </div></details>`;
  }
  els.panel.innerHTML = html;
}

function renderStats() {
  const ids = allItems().map((x) => x.id);
  const kotak = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  let baru = 0, jatuhTempo = 0, dilihat = 0, benar = 0;
  for (const id of ids) {
    const s = stateOf(id);
    if (!s) { baru += 1; continue; }
    kotak[s.box] += 1;
    dilihat += s.seen || 0;
    benar += s.right || 0;
    if (isDue(id)) jatuhTempo += 1;
  }
  const maxN = Math.max(1, ...Object.values(kotak));
  const baris = [1, 2, 3, 4, 5].map((b) =>
    `<tr><td>Kotak ${b}</td><td><span class="bar" style="width:${(kotak[b] / maxN) * 160}px"></span>
      &nbsp;${kotak[b]}</td></tr>`).join("");
  const pct = dilihat ? Math.round((benar / dilihat) * 100) : 0;
  els.stats.innerHTML = `<h3>Kemajuan pada modul ${esc(MODES[mode].label)}</h3>
    <table>
      <tr><td>Total kartu</td><td>${ids.length}</td></tr>
      <tr><td>Belum dilatih</td><td>${baru}</td></tr>
      <tr><td>Jatuh tempo</td><td>${jatuhTempo}</td></tr>
      ${baris}
    </table>
    <p>${dilihat ? `Jawaban tercatat: ${dilihat}, benar ${benar} (${pct}%).` : "Belum ada jawaban tercatat."}
    Jeda ulangan per kotak: 0, 1, 3, 7, dan 16 hari.</p>`;
}

/* ------------------------------------------------------------- kendali ---- */

function setMode(m) {
  mode = m;
  activeCat = "*";
  index = 0;
  answered = false;
  for (const b of els.tabs.querySelectorAll("button")) {
    b.setAttribute("aria-pressed", String(b.dataset.mode === m));
  }
  renderToggles();
  renderChips();
  buildDeck();
  render();
  renderStats();
}

function refresh() {
  renderChips();
  buildDeck();
  render();
}

/* Nama tema yang dikenal. Dipakai juga untuk membuang kelas tema lama secara
   tepat sasaran. */
const THEMES = ["qirtas", "lail", "zaytun"];
const THEME_BAWAAN = "qirtas";

function setTheme(name) {
  // Nilai dari localStorage bisa saja rusak atau berasal dari versi lama.
  // Tanpa penyaringan ini, body pernah berakhir dengan kelas
  // "theme-[object Object]": tidak ada tema yang sah, tidak ada tombol tema
  // yang tampak aktif, dan nilai rusaknya ditulis balik sehingga menetap.
  if (!THEMES.includes(name)) name = THEME_BAWAAN;

  // classList, bukan className: menimpa className akan menghapus kelas lain
  // yang mungkin ada pada <body>.
  for (const t of THEMES) document.body.classList.remove("theme-" + t);
  document.body.classList.add("theme-" + name);

  for (const b of document.querySelectorAll(".theme-dot")) {
    b.setAttribute("aria-pressed", String(b.dataset.theme === name));
  }
  lsSet(LS.theme, name);
}

function bindToggle(id, key) {
  const el = $(id);
  el.checked = prefs[key];
  el.addEventListener("change", () => {
    prefs[key] = el.checked;
    lsSet(LS.prefs, prefs);
    index = 0;
    refresh();
  });
}

function init() {
  if (!D) {
    document.body.innerHTML = '<p class="empty">webdata.js gagal dimuat. ' +
      'Jalankan <code>python tools/build_web.py</code> lalu muat ulang halaman.</p>';
    return;
  }

  setTheme(lsGet(LS.theme, THEME_BAWAAN));

  els.tabs.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) setMode(b.dataset.mode);
  });
  els.chips.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeCat = b.dataset.cat;
    index = 0;
    refresh();
  });
  els.stages.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b) return;
    activeStage = Number(b.dataset.stage);
    for (const s of els.stages.querySelectorAll("button")) {
      s.setAttribute("aria-pressed", String(Number(s.dataset.stage) === activeStage));
    }
    activeCat = "*";
    index = 0;
    refresh();
  });
  els.search.addEventListener("input", () => {
    query = els.search.value;
    index = 0;
    buildDeck();
    render();
  });
  els.choices.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) answer(Number(b.dataset.i));
  });
  els.card.addEventListener("click", (e) => {
    if (!e.target.closest(".choices")) flip();
  });

  $("#btn-flip").addEventListener("click", (e) => { e.stopPropagation(); flip(); });
  $("#btn-next").addEventListener("click", next);
  $("#btn-prev").addEventListener("click", prev);
  $("#btn-right").addEventListener("click", () => gradeFlip(true));
  $("#btn-wrong").addEventListener("click", () => gradeFlip(false));
  $("#btn-shuffle").addEventListener("click", (e) => {
    shuffled = !shuffled;
    e.currentTarget.setAttribute("aria-pressed", String(shuffled));
    index = 0;
    buildDeck();
    render();
  });
  $("#btn-stats").addEventListener("click", (e) => {
    const buka = els.stats.hidden;
    els.stats.hidden = !buka;
    e.currentTarget.setAttribute("aria-expanded", String(buka));
    if (buka) renderStats();
  });
  $("#btn-reset").addEventListener("click", () => {
    if (!confirm("Hapus seluruh progres di peramban ini? Tindakan ini tidak bisa dibatalkan.")) return;
    progress.cards = {};
    lsSet(LS.prog, progress);
    refresh();
    renderStats();
  });

  for (const b of document.querySelectorAll(".theme-dot")) {
    b.addEventListener("click", () => setTheme(b.dataset.theme));
  }

  bindToggle("#tg-translit", "translit");
  bindToggle("#tg-harakat", "harakat");
  bindToggle("#tg-arah", "arah");
  bindToggle("#tg-due", "due");
  bindToggle("#tg-hide", "hide");

  document.addEventListener("keydown", (e) => {
    if (e.target === els.search) {
      if (e.key === "Escape") { els.search.value = ""; query = ""; index = 0; refresh(); els.search.blur(); }
      return;
    }
    if (e.ctrlKey || e.metaKey || e.altKey) return;
    switch (e.key) {
      case " ": case "Enter": e.preventDefault(); flip(); break;
      case "ArrowRight": e.preventDefault(); next(); break;
      case "ArrowLeft": e.preventDefault(); prev(); break;
      case "h": case "H": gradeFlip(true); break;
      case "b": case "B": gradeFlip(false); break;
      case "s": case "S": $("#btn-shuffle").click(); break;
      case "t": case "T": $("#tg-translit").click(); break;
      case "/": e.preventDefault(); els.search.focus(); break;
      default:
        if (/^[1-9]$/.test(e.key)) answer(Number(e.key) - 1);
    }
  });

  window.addEventListener("resize", fitCard);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitCard);

  setMode("kosakata");

  // Jumlah kartu pada tab diambil dari data, bukan ditulis tangan.
  for (const b of els.tabs.querySelectorAll("button")) {
    const n = MODES[b.dataset.mode].items().length;
    b.querySelector("span").textContent = String(n);
  }
}

document.addEventListener("DOMContentLoaded", init);
