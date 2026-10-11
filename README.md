# Latihan Bahasa Arab Fusha (MSA)

Bahan latihan Bahasa Arab Baku Modern (Modern Standard Arabic / *fusha*) untuk
pelajar penutur Bahasa Indonesia yang **sudah bisa membaca tulisan Arab
berharakat**.

Materi ini berangkat dari titik yang biasanya dilewatkan buku pelajaran: Anda
sudah mengenal huruf, harakat, tanwin, syaddah, mad, dan sukun dari membaca
Al-Qur'an, tetapi belum menguasai kosakata dan tata bahasanya. Sasarannya
tingkat A1 menuju A2.

| | |
|:--|:--|
| Kosakata | 188 entri, 6 tahap |
| Topik tata bahasa | 12 topik, 60 soal |
| Keluarga akar kata | 14 keluarga (85 kata), 12 pola, 18 soal |
| Latihan membaca tanpa harakat | 12 teks, 30 soal, 3 level |
| Catatan Qur'an vs MSA | 18 kata, 5 catatan pemakaian, 10 soal |
| Total kartu | 332 |
| Lembar kerja tertulis | 12 lembar + 12 kunci jawaban |
| Pengujian otomatis | 190 |

## Dua cara memakai

### 1. Aplikasi kartu di browser

**<https://hivana98.github.io/Bahasa-Arab/>** &mdash; tidak perlu memasang apa pun.

Lima modul dalam bentuk kartu bolak-balik: kosakata (dua arah), tata bahasa dan
Qur'an vs MSA (pilihan ganda), akar kata, serta membaca tanpa harakat. Sakelar
"Sembunyikan harakat" mengubah kartu kosakata mana pun menjadi latihan membaca
gundul. Progres memakai lima kotak Leitner yang sama dengan versi terminal dan
tersimpan di `localStorage` peramban Anda sendiri.

Pintasan papan ketik: `Spasi` balik kartu &middot; `&larr;` `&rarr;` navigasi
&middot; `1`&ndash;`4` pilih jawaban &middot; `H` sudah hafal &middot; `B` belum
hafal &middot; `S` acak &middot; `T` alih huruf &middot; `/` cari.

Untuk menjalankannya di komputer sendiri, cukup peladen statis apa pun:

```bash
python -m http.server 8765
```

lalu buka <http://localhost:8765>. Berkas `index.html` juga bisa dibuka langsung
(`file://`) karena datanya dimuat lewat tag `<script>`, bukan `fetch()`.

### 2. Latihan di terminal

`python quiz.py` memberi hal yang tidak ada di versi web: jawaban yang **ditulis
sendiri** (bukan pilihan ganda), sesi berbatas waktu, interleaving antar modul,
pembatasan materi baru per sesi, dan pengenalan materi menurut urutan tahap.
Rinciannya ada di bawah.

Progres kedua versi terpisah: aplikasi web memakai `localStorage`, versi terminal
memakai `progress.json`. Keduanya tidak saling tahu, jadi pilih salah satu untuk
materi yang sama.

## Yang TIDAK ada di sini

- **Tidak ada pelajaran huruf dan harakat dasar.** Materi ini mengandaikan Anda
  sudah bisa membacanya.
- **Tidak ada transliterasi Latin secara bawaan.** Alih huruf hanya muncul bila
  Anda menyalakan bendera `--translit`. Alasannya: penyangga Latin membuat mata
  berhenti membaca tulisan Arab. Teks yang memang tidak berharakat (modul
  membaca) tidak dialihhurufkan sama sekali.
- **Tidak ada dialek.** Hanya fusha.
- **Tidak ada ayat Al-Qur'an.** Tidak satu pun ayat ditulis dari ingatan. Bila
  Anda ingin memakai ayat sebagai contoh, sediakan sendiri teks mushaf di
  `sources/` — lihat `sources/README.md`.
- **Tidak ada janji hasil.** Kecepatan belajar setiap orang berbeda-beda.

## Persyaratan

Python 3.10 atau lebih baru. Tidak ada pustaka pihak ketiga yang perlu dipasang
untuk menjalankan latihannya; `pytest` hanya diperlukan untuk menjalankan
pengujian.

Terminal Anda perlu bisa menampilkan tulisan Arab. Di Windows, Windows Terminal
menampilkan huruf Arab lebih baik daripada `cmd.exe` lama.

## Mulai cepat

```bash
python quiz.py
```

Sesi bawaan: 20 menit, campuran semua mode, 8 kartu baru. Progres tersimpan di
`progress.json`.

```bash
python quiz.py --stats
```

## Bendera baris perintah

| Bendera | Arti |
|:--------|:-----|
| `--mode MODE` | Batasi mode. Boleh diulang atau dipisah koma. Bawaan: semua. |
| `--stage N` | Batasi materi sampai tahap N (1-6). |
| `--minutes M` | Lama sesi dalam menit (bawaan 20). Sesi berhenti saat waktunya habis. |
| `--limit N` | Batas jumlah soal dalam satu sesi. |
| `--new N` | Kartu baru per sesi (bawaan 8). `--new 0` berarti hanya mengulang. |
| `--translit` | Tampilkan alih huruf Latin di bawah teks berharakat. |
| `--seed N` | Nilai awal pengacak, untuk mengulang susunan sesi yang sama. |
| `--progress BERKAS` | Lokasi berkas progres selain `progress.json`. |
| `--stats` | Tampilkan ringkasan kemajuan lalu keluar. |
| `--reset` | Hapus berkas progres (meminta konfirmasi). |
| `--no-color` | Matikan warna. |

Mode yang tersedia:

| Mode | Isi |
|:-----|:----|
| `kosakata-ar` | Arab ke Indonesia. Jawaban **ditulis** (bukan pilihan ganda). |
| `kosakata-id` | Indonesia ke Arab. Pilihan ganda. |
| `tatabahasa` | Soal tata bahasa dan catatan Qur'an vs MSA. |
| `akar` | Akar kata dan pola, termasuk soal yang dibuat otomatis dari data. |
| `baca` | Membaca tanpa harakat: tentukan bacaan, pilih arti, dan baca sendiri. |

Di dalam sesi: ketik nomor untuk pilihan ganda, `l` untuk melewati, `k` untuk
keluar, `?` untuk melihat jawaban pada soal yang jawabannya ditulis (dihitung salah).

## Isi materi

### Modul 1 — Kosakata inti (`data/vocab.json`)

188 entri dalam 6 tahap: kata ganti, kata tunjuk, kata tanya, angka 1-10,
keluarga, orang, benda sehari-hari, tempat, waktu, kata kerja, kata sifat,
huruf jar dan zharf.

Setiap entri memuat: kata berharakat, arti Indonesia, kelas kata, gender (untuk
kata benda), bentuk jamak bila lazim, bentuk mudhari' (untuk kata kerja), akar
tiga huruf bila ada, satu contoh kalimat pendek berharakat penuh, dan catatan
pemakaian.

### Modul 2 — Tata bahasa dasar (`data/grammar.json`)

| Topik | Isi |
|:------|:----|
| g01 | Kalimat nominal: mubtada' dan khabar |
| g02 | Definit (ال) dan indefinit (tanwin) |
| g03 | Mudzakkar, mu'annats, dan ta' marbuthah |
| g04 | Kata ganti terpisah dan melekat |
| g05 | Idhafah (penyandaran) |
| g06 | Kata sifat dan kesesuaiannya |
| g07 | Kata tunjuk |
| g08 | Huruf jar dan isim majrur |
| g09 | Penafian: لا، ما، لم، ليس |
| g10 | Jamak: salim dan taksir (pengenalan) |
| g11 | Kalimat verbal: fi'l madhi |
| g12 | Kalimat verbal: fi'l mudhari' |

Setiap topik memiliki field `caveats` yang memuat pengecualian dan perbedaan
pendapat. Hal-hal itu sengaja ditulis sebagai catatan, bukan sebagai aturan
mutlak.

### Modul 3 — Akar kata dan pola (`data/roots.json`)

14 keluarga akar (ك ت ب، د ر س، ع ل م، ف ت ح، س ج د، ك ل م، ج م ع، ع م ل،
س م ع، ل ع ب، ق ر أ، ح س ب، ط ع م، ك ب ر) dan 12 pola: فَاعِل، مَفْعُول،
مَفْعَل، مِفْعَال، فَعِيل، أَفْعَل، serta wazan II, IV, V, VIII, X dan mashdar wazan I.

Soal "apa akar kata ini" dan "mana yang bukan sekeluarga" **dibuat otomatis**
dari data keluarga akar, sehingga kuncinya tidak mungkin menyimpang dari
sumbernya.

### Modul 4 — Membaca tanpa harakat (`data/reading.json`)

Keterampilan penghubung menuju teks Arab sehari-hari.

| Level | Tampilan |
|:------|:---------|
| 1 | Harakat penuh |
| 2 | Harakat hanya pada kata yang menentukan; syaddah tetap ditulis |
| 3 | Tanpa harakat |

Jenis latihan: menentukan bacaan yang tepat dari konteks (misalnya rangka huruf
`علم` yang bisa dibaca عِلْمٌ، عَلِمَ، عَلَمٌ، atau عُلِمَ), memilih arti kalimat tanpa
harakat, dan membaca teks pendek lalu mencocokkannya sendiri.

Semua pilihan pada soal "tentukan bacaan" memiliki **rangka huruf yang sama**,
sehingga soal tidak bisa dijawab dari bentuk tulisannya. Hal ini diuji otomatis.

### Modul 5 — Qur'an dan MSA (`data/quran_msa.json`)

Catatan pendek, bukan latihan utama. Memuat 18 kata yang makna atau
pemakaiannya berbeda antara bahasa Arab klasik dan MSA: سَيَّارَة، هَاتِف، جَرِيدَة،
صَحِيفَة، قَامُوس، قِطَار، طَائِرَة، دَوْلَة، شَرِكَة، ثَقَافَة، سِيَاسَة، ثَوْرَة، جَامِعَة، مُهَنْدِس،
بَرِيد، حَاسُوب، جُمْهُورِيَّة، مُسْتَشْفَى.

Modul ini juga menegaskan satu hal yang sering disalahpahami: **mayoritas
kosakata inti tidak bergeser maknanya.** Daftar di atas adalah pengecualian.

Untuk makna sebuah kata **di dalam** sebuah ayat, rujuklah kitab tafsir atau
kamus khusus Al-Qur'an. Kolom makna klasik di modul ini hanya ringkasan kamus
klasik secara umum.

## Cara kerja penjadwalan

Lima kotak Leitner. Jawaban benar menaikkan kartu satu kotak, jawaban salah
mengembalikannya ke kotak 1.

| Kotak | Jeda sebelum diulang |
|------:|---------------------:|
| 1 | hari itu juga |
| 2 | 1 hari |
| 3 | 3 hari |
| 4 | 7 hari |
| 5 | 16 hari |

Angka-angka itu adalah pilihan praktis yang lazim dipakai pada kartu Leitner,
**bukan hasil pengukuran**. Ubah `INTERVALS` di `arabdrill/leitner.py` bila
jadwal lain lebih cocok.

Empat hal lain yang diterapkan penjadwal:

- **Ulangan didahulukan.** Selama masih ada kartu jatuh tempo, materi baru
  dibatasi paling banyak 45% dari satu sesi. Tanpa pembatasan ini materi baru
  memakan seluruh sesi dan kartu lama tidak pernah naik kotak.
- **Interleaving.** Soal dari mode berbeda disilang bergantian, dan materi lama
  disisipkan di antara materi baru kira-kira 2 lama : 1 baru. Mencampur materi
  umumnya menghasilkan ingatan yang lebih tahan lama daripada mengerjakan satu
  blok materi sejenis berturut-turut, meski terasa lebih sulit saat dikerjakan.
- **Materi baru masuk menurut urutan tahap**, bukan acak dari seluruh materi,
  walaupun `--stage` tidak diberikan.
- **Lintasan kedua.** Pada hari-hari awal, ketika belum ada kartu jatuh tempo,
  kartu baru diulang sekali lagi di akhir sesi. Pengulangan itu tidak menaikkan
  kotak Leitner dua kali.

## Jadwal 6 minggu

Dengan pengaturan bawaan (20 menit per sesi, 8 kartu baru, 5 sesi per minggu),
penjadwal memperkenalkan **kira-kira 20 kata baru per minggu**, ditambah soal
tata bahasa, akar kata, dan latihan membaca.

| Minggu | Kosakata (kumulatif) | Tahap kosakata | Tata bahasa | Akar | Membaca |
|-------:|---------------------:|:---------------|:------------|:-----|:--------|
| 1 | 20 | tahap 1 | g01, g02 | r01, r02 | Level 1 |
| 2 | 40 | tahap 1 selesai, tahap 2 mulai | g03, g04 | r03-r05 | Level 1 |
| 3 | 60 | tahap 2 selesai | g05, g06 | r06, r07 | Level 2 |
| 4 | 80 | tahap 3 | g07, g08 | r08-r10 | Level 2 |
| 5 | 100 | tahap 3 selesai, tahap 4 mulai | g09, g10 | r11-r13 | Level 3 |
| 6 | 120 | tahap 4 selesai | g11, g12 | r14 | Level 3 |

Pada akhir minggu ke-6 dengan pengaturan bawaan, **seluruh 12 topik tata
bahasa, seluruh keluarga akar, dan seluruh latihan membaca sudah diperkenalkan**,
sedangkan kosakata mencapai sekitar 120 dari 188 kata (tahap 1 sampai 4).

Menyelesaikan seluruh 188 kata pada kecepatan yang sama memerlukan sekitar
**10 minggu** (kira-kira 50 sesi). Bila Anda ingin menyelesaikannya dalam 6
minggu, naikkan `--new` ke sekitar 14 — tetapi beban ulangannya akan ikut naik
dan sesi 20 menit menjadi tidak cukup.

### Dari mana angka-angka itu

Angka di tabel berasal dari **simulasi penjadwal**, bukan dari pengamatan
pembelajar nyata: 50 sesi berurutan, 5 sesi per minggu, dengan asumsi ketepatan
jawaban 85%. Pada simulasi itu, tunggakan soal jatuh tempo memuncak di sekitar
220 soal pada minggu ke-8, lalu menyusut setelah materi baru habis. Dengan
ketepatan 95%, puncaknya sekitar 100 soal.

Kecepatan setiap orang berbeda, dan tidak ada yang menjamin angka ini berlaku
untuk Anda.

### Bila tunggakan menumpuk

Bila `--stats` menunjukkan kartu jatuh tempo jauh lebih banyak daripada yang
bisa Anda kerjakan:

```bash
python quiz.py --new 0            # satu sesi khusus mengulang, tanpa materi baru
python quiz.py --new 4            # perlambat laju materi baru
python quiz.py --minutes 30       # sesi lebih panjang
```

Memperlambat materi baru lebih baik daripada menumpuk kartu yang tidak pernah
diulang.

## Lembar kerja

12 lembar kerja Markdown di `worksheets/`, dua lembar per tahap, dengan kunci
jawaban **terpisah** di `worksheets/answers/`. Setiap lembar memuat lima bagian:
arti kata, menulis kata Arab, tata bahasa, akar kata, dan membaca tanpa harakat.

Lembar kerja dibuat dari data oleh skrip, bukan ditulis tangan, sehingga
kuncinya selalu sejalan dengan datanya. Jangan menyuntingnya langsung.

```bash
python tools/build_worksheets.py
```

## Anki

Ekspor CSV untuk Anki ada di `anki/`, beserta pemetaan kolom ke field di
`anki/README.md`.

```bash
python tools/build_exports.py
```

Catatan: bila Anda memakai Anki, pakailah penjadwalan Anki dan jangan
menjalankan `quiz.py` untuk materi yang sama. `progress.json` dan koleksi Anki
tidak saling tahu, sehingga satu kartu akan dijadwalkan oleh dua sistem sekaligus.

## Pengujian

```bash
python -m pytest
```

190 pengujian. Yang diperiksa:

| Berkas | Isi |
|:-------|:----|
| `test_schema.py` | Id unik di seluruh modul, format id, tidak ada field kosong atau null yang tidak diizinkan, nilai kelas kata dan gender sah, kata benda bergender, kata kerja memiliki mudhari', setiap tahap dan setiap level terisi. |
| `test_arabic.py` | Hanya karakter Arab yang diizinkan, bentuk NFC, tidak ada tatwil, tidak ada huruf Latin di field Arab, kelengkapan harakat menurut aturan ortografis (dua aturan: lema dan kalimat), format akar. |
| `test_roots.py` | Huruf akar muncul berurutan pada kata turunannya, pengecualian wajib memiliki catatan, satu kata tidak diklaim dua akar, akar di `vocab.json` sejalan dengan `roots.json`. |
| `test_keys.py` | Setiap soal memiliki tepat satu jawaban benar, tidak ada pilihan ganda identik, kunci modul membaca sama dengan kata pada kalimat berharakatnya, semua pilihan berangka huruf sama, pengecoh soal buatan otomatis tidak ikut benar. |
| `test_leitner.py` | Kenaikan dan penurunan kotak, jeda sesuai tabel, jatuh tempo, simpan dan muat ulang, berkas rusak tidak merusak pemuatan, penulisan atomik. |
| `test_session.py` | Batas kartu baru, ulangan tidak tergeser habis oleh materi baru, kartu belum jatuh tempo tidak muncul, interleaving mencampur mode, satu kata dilatih dua arah, materi baru masuk menurut urutan tahap, sesi dapat diulang dengan seed sama. |
| `test_translit.py` | Kasus alih huruf yang dipatok, lam syamsiyah dileburkan, tidak ada huruf Arab yang tertinggal. |
| `test_exports.py` | Semua hasil ekspor mutakhir terhadap data (CSV, Anki, lembar kerja, dan `webdata.js`), kolom kunci sesuai, format Anki benar, kunci soal di `webdata.js` sama dengan di `data/`, dan aplikasi web tidak memakai `fetch()` sehingga tetap jalan di `file://`. |
| `test_worksheets.py` | Kunci berada di berkas terpisah, semua bagian ada, soal membaca disajikan tanpa harakat sedangkan kuncinya berharakat penuh, dan setiap butir berasal dari data. |
| `test_sources.py` | Tidak ada rujukan ayat di Modul 1-4, `quran_examples` kosong selama `sources/` kosong, setiap akar yang dikosongkan memiliki penjelasan, `NEEDS_REVIEW.md` ada dan id yang disebutnya benar-benar ada. |

### Apa yang TIDAK bisa diuji mesin

Pengujian di atas memeriksa **bentuk**, bukan **kebenaran isi bahasa**. Yang
tidak diperiksa mesin:

- Apakah arti Bahasa Indonesia sudah tepat dan wajar.
- Apakah gender dan bentuk jamak sudah benar.
- Apakah akar yang dicantumkan memang akar kata itu. Pengujian hanya memeriksa
  bahwa huruf-hurufnya muncul berurutan pada kata — akar keliru yang kebetulan
  hurufnya cocok akan tetap lolos.
- Apakah contoh kalimat benar secara nahwu, i'rabnya tepat, dan terdengar wajar
  bagi penutur.
- Apakah penjelasan tata bahasa tidak menyederhanakan secara menyesatkan.
- Apakah makna klasik di Modul 5 sesuai kamus rujukan.

**Periksalah isinya dengan kamus rujukan atau dengan pengajar** sebelum
menghafalkannya. Hal-hal yang belum diyakini sepenuhnya sudah dikosongkan atau diberi catatan,
dan didaftar di `data/NEEDS_REVIEW.md`.

## Menyunting data

`data/*.json` adalah **satu-satunya sumber data**. Berkas di `data/csv/`,
`anki/`, dan `worksheets/` adalah turunan yang dibuat ulang oleh skrip.

```bash
# 1. sunting data/vocab.json (atau modul lain)
python -m pytest                      # 2. pastikan data masih sah
python tools/build_exports.py         # 3. buat ulang CSV dan Anki
python tools/build_worksheets.py      # 4. buat ulang lembar kerja
python tools/build_web.py             # 5. buat ulang data aplikasi web
python -m pytest                      # 6. pastikan semua hasil mutakhir
```

Pengujian `test_exports.py` akan gagal bila data sudah berubah tetapi ekspornya
belum dibuat ulang.

### Aturan penulisan harakat

Validator di `arabdrill/arabic.py` menegakkan dua aturan berbeda:

| Field | Aturan |
|:------|:-------|
| Lema (`ar`, `plural`, `fem`, `mudhari`, pola, anggota keluarga akar) | Bentuk waqf: huruf **terakhir** boleh tanpa harakat, seperti penulisan kamus. |
| Kalimat (`example.ar`, contoh topik, teks baca) | Harakat penuh termasuk i'rab pada **semua** huruf semua kata. |

Validator **tidak** menjangkau field prosa (`explanation`, `caveats`, `note`,
`explain`), dan memang seharusnya begitu. Field itu sengaja memuat dua hal yang
akan ditolak validator:

- akhiran yang ditulis dengan tatwil agar terbaca sebagai akhiran, misalnya
  `ـكَ` dan `ـُونَ`;
- contoh bentuk yang sengaja **salah** untuk diperbandingkan, misalnya
  `كِتَابٌي` pada topik g04.

Isi field prosa karena itu perlu ditinjau manusia.

Perkecualian yang diizinkan validator, beserta alasannya:

| Perkecualian | Alasan |
|:-------------|:-------|
| alif (ا), alif maqshurah (ى), dan alif madda (آ) boleh tanpa tanda | Ketiganya memang tidak pernah memikul harakat. |
| waw dan ya' tanpa harakat setelah dhammah dan kasrah | Keduanya berfungsi sebagai huruf mad, bukan konsonan berharakat. |
| lam pada ال tanpa tanda bila huruf sesudahnya bersyaddah | Itulah penulisan baku untuk huruf syamsiyah (الطَّالِبُ). |
| tanwin fathatan pada huruf sebelum alif penyangga | Itulah posisi bakunya (كِتَابًا). |

## Struktur folder

```
index.html            aplikasi kartu di browser (GitHub Pages)
style.css             tiga tema: qirtas, lail, zaytun
app.js                kartu, saringan, Leitner di localStorage
webdata.js            data aplikasi web (dibuat ulang)
.nojekyll             agar GitHub Pages tidak memproses berkas lewat Jekyll
data/                 sumber data JSON + NEEDS_REVIEW.md
  csv/                ekspor CSV (dibuat ulang)
arabdrill/            paket inti
  arabic.py           normalisasi, pelepasan harakat, validator harakat
  translit.py         alih huruf opsional
  leitner.py          lima kotak + jadwal + berkas progres
  dataio.py           pemuat data
  questions.py        pembuat soal per mode
  session.py          penyusun sesi (jatuh tempo, materi baru, interleaving)
quiz.py               antarmuka baris perintah
tools/                build_exports.py, build_worksheets.py, build_web.py
anki/                 ekspor Anki (dibuat ulang) + pemetaan field
worksheets/           lembar kerja (dibuat ulang)
  answers/            kunci jawaban
sources/              tempat Anda menaruh teks mushaf; kosong secara bawaan
tests/                pengujian otomatis
progress.json         progres Anda (dibuat saat latihan pertama)
```

## Catatan keterbatasan

- Materi ini disusun oleh model bahasa dan diperiksa secara otomatis hanya pada
  hal-hal yang bisa diperiksa mesin. Isi bahasanya belum ditinjau penutur asli
  atau pengajar.
- Tingkat A1-A2 berarti kalimat pendek dan kosakata sehari-hari. Membaca surat
  kabar Arab dengan lancar memerlukan kosakata yang jauh lebih banyak daripada
  yang ada di sini.
- Modul membaca tanpa harakat melatih penentuan bacaan pada kalimat pendek yang
  kosakatanya sudah Anda kenal. Teks nyata lebih sulit karena memuat kata yang
  belum dikenal.
- Tidak ada latihan menyimak dan berbicara di proyek ini.
