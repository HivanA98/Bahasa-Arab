# Perlu diperiksa (NEEDS_REVIEW)

Daftar hal yang **belum diyakini sepenuhnya** oleh penyusun dan karena itu tidak dijadikan
keterangan pasti di dalam data. Semua yang ada di sini sengaja dikosongkan,
diberi catatan berpagar, atau tidak dimasukkan sama sekali — bukan ditebak.

Periksalah dengan kamus rujukan (Lisān al-ʿArab, al-Qāmūs al-Muḥīṭ, al-Muʿjam
al-Wasīṭ, Lane's Lexicon, Hans Wehr) atau tanyakan kepada pengajar. Setelah
terkonfirmasi, isi field yang bersangkutan di `data/*.json`, lalu jalankan
`python -m pytest` dan `python tools/build_exports.py`.

---

## A. Akar kata yang dikosongkan atau diperdebatkan

| Entri | Kata | Masalah |
|:------|:-----|:--------|
| v127 | مَسَاء | Akar **tidak dicantumkan** (`root: null`). Berkaitan dengan أَمْسَى / يُمْسِي, tetapi belum dipastikan apakah akarnya dicatat sebagai م س و atau م س ي. |
| v073 | اِسْم | Akar **tidak dicantumkan** karena memang diperdebatkan: ulama Bashrah menyebut س م و, ulama Kufah menyebut و س م. Perbedaan ini ditulis di `root_note` sebagai catatan, bukan keputusan. |
| v130 | سَنَة | Akar ditulis س ن و, dengan catatan bahwa sebagian kamus mencatat س ن ه (bandingkan سُنَيْهَة). Perlu dipastikan mana yang dijadikan lema. |
| v119, v117, v090, v091 | تَحْتَ، أَمَامَ، مَعَ، عِنْدَ | Tidak diberi akar. Akar ب ي ن (v116), خ ل ف (v118), ف و ق (v120), ق ب ل (v121), dan ب ع د (v122) dicantumkan karena keluarga turunannya jelas; empat zharf ini tidak, karena keyakinannya belum cukup. Kemungkinan ت ح ت untuk تَحْتَ dan أ م م untuk أَمَامَ, belum dipastikan. |
| v134, v135 | الْآن، أَمْسِ | Tidak diberi akar; bentuknya memang beku sebagai keterangan waktu. |
| v075 | طَاوِلَة | Dinyatakan kata serapan (tanpa akar). Jalur serapannya (Italia *tavola* atau Latin *tabula*, mungkin lewat Turki) ditulis sebagai perbandingan, bukan kepastian etimologis. |
| v069 | مُهَنْدِس | Akar empat huruf ه ن د س. Asal Persia-nya disebut dengan tingkat keyakinan **sedang**; perlu rujukan etimologi. |
| q05 | قَامُوس | Dinyatakan tanpa akar karena serapan Yunani. Keyakinan **sedang** untuk jalur serapannya. |
| q15 | بَرِيد | Dinyatakan tanpa akar karena serapan. Keyakinan **sedang**. Makna klasik tambahan "satuan jarak tempuh" **tidak dimasukkan** karena belum dipastikan. |

### Pengecualian pencocokan akar

Dua entri tidak lolos pencocokan otomatis akar-ke-kata, dan keduanya sudah
diberi `root_note`. Tingkat keyakinan pada keduanya **tinggi**, tetapi tetap
dicatat di sini karena mesin tidak bisa membuktikannya:

| Entri | Kata | Akar | Keterangan |
|:------|:-----|:-----|:-----------|
| v035 | سِتَّة | س د س | Dal melebur menjadi ta' bersyaddah. Bukti pendukung: سَادِس، أَسْدَاس، سُدُس. |
| v083 | مَاء | م و ه | Huruf akar tidak tampak pada bentuk tunggalnya. Bukti pendukung: jamak مِيَاه, tashghir مُوَيْه. |

---

## B. Bentuk jamak yang sengaja tidak dicantumkan

Field `plural` dikosongkan (`null`) bila bentuk jamaknya belum dipastikan,
atau bila katanya memang jarang dijamakkan.

| Entri | Kata | Alasan |
|:------|:-----|:-------|
| v126 | صَبَاح | Jamaknya tidak dicantumkan. Kemungkinan أَصْبَاح, belum dipastikan. |
| v127 | مَسَاء | Sama: belum dipastikan. |
| v125 | لَيْل | Bentuk kolektif. Jamaknya (أَلْيَال؟) belum dipastikan. |
| v084 | خُبْز | Kata kolektif, tidak lazim dijamakkan dalam pemakaian sehari-hari. |
| v094 | قَهْوَة | Jamaknya tidak lazim dipakai. |
| v174 | جَمِيل | Jamak untuk manusia belum dipastikan. |
| v177, v178, v179, v180, v181, v182, v183, v184, v185, v186, v187, v188 | سَهْل dan kata sifat sesudahnya | Jamak manusia tidak dicantumkan. Untuk benda bukan manusia hal ini tidak diperlukan karena disifati dengan mu'annats tunggal (lihat topik g06). |

Jamak yang **dicantumkan tetapi punya varian lain** sudah ditulis di field
`note`, misalnya طُلَّاب / طَلَبَة (v065), شُهُور / أَشْهُر (v129),
سَنَوَات / سِنُون (v130), بِلَاد / بُلْدَان (v104), أَمْكِنَة / أَمَاكِن (v114).
Yang perlu dipastikan adalah mana yang paling lazim di MSA kontemporer.

### Jamak kata sifat untuk benda

| Entri | Kata | Masalah |
|:------|:-----|:--------|
| v173 | قَدِيم | Jamak قُدَمَاء dicantumkan, tetapi pemakaiannya untuk **manusia** (مُدَرِّسُونَ قُدَمَاءُ). Untuk benda, jamaknya diperlakukan sebagai mu'annats tunggal. Perlu dipastikan apakah mencantumkannya tanpa penjelasan ini bisa menyesatkan. |
| v172 | جَدِيد | Jamak جُدُد. Sebagian sumber juga menyebut جُدَد. Belum dipastikan mana yang baku. |

---

## C. Gender yang punya lebih dari satu pendapat

| Entri | Kata | Masalah |
|:------|:-----|:--------|
| v100 | سُوق | Ditandai `m/f`. Kamus yang berbeda mencatat kecenderungan yang berbeda. Perlu dipastikan mana yang lazim di MSA. |
| v104 | بَلَد | Ditandai `m` dengan catatan bahwa sebagian pemakaian memperlakukannya mu'annats. Perlu dipastikan. |
| v108 | مُسْتَشْفَى | Ditandai `m`. Perlu dipastikan apakah ada pemakaian mu'annats yang juga baku. |

---

## D. Modul 5: makna klasik yang perlu rujukan kamus

Semua entri Modul 5 adalah ringkasan makna kamus klasik secara **umum**, dan
bukan tafsir sebuah ayat. Yang berikut ini perlu diperiksa secara khusus:

| Entri | Kata | Masalah |
|:------|:-----|:--------|
| q03 | جَرِيدَة | Hubungan makna "pelepah kurma" dengan "surat kabar" ditulis sebagai **dugaan** ("diduga berkaitan dengan bentuk lembaran"). Jangan dibaca sebagai fakta etimologis. |
| q10 | ثَقَافَة | Makna klasik akar ث ق ف (ketangkasan, kecerdasan) keyakinan tinggi. Pernyataan bahwa makna modernnya dibentuk sebagai padanan "culture" adalah rekonstruksi sejarah istilah yang perlu rujukan. |
| q11 | سِيَاسَة | Makna asal "mengurus dan melatih kuda" keyakinan **sedang-tinggi**. Perlu rujukan kamus. |
| q12 | ثَوْرَة | Makna akar ث و ر (bangkit, mengangkat debu) keyakinan tinggi; jalur ke makna "revolusi" adalah rekonstruksi. |
| q08 | دَوْلَة | Makna "pergiliran kekuasaan" keyakinan tinggi. Kapan tepatnya makna "negara" mulai lazim, tidak dinyatakan di sini. |
| q05 | قَامُوس | Cerita bahwa nama kitab al-Qāmūs al-Muḥīṭ menjadi nama jenis: keyakinan tinggi, tetapi perlu rujukan. |
| q16, q17, q18 | حَاسُوب، جُمْهُورِيَّة، مُسْتَشْفَى | Disebut "kata buatan baru". Abad pembentukannya disebut secara umum (abad ke-20 untuk حَاسُوب) tanpa rujukan lembaga bahasa tertentu. |

### Sengaja TIDAK dimasukkan ke Modul 5

Karena keyakinannya belum cukup:

- **أُمَّة** dengan makna "jangka waktu" dalam pemakaian klasik, selain makna
  "umat/komunitas".
- **مَجَلَّة** dengan makna klasik (kitab atau lembaran berisi hikmah).
- **بَرِيد** dengan makna "satuan jarak tempuh".
- Semua kata yang pergeseran maknanya hanya diketahui dari ingatan samar.

---

## E. Pola (wazan) yang perlu ditinjau

| Entri | Masalah |
|:------|:--------|
| r03 | Kata عَالَم diberi pola `فَاعَل`. Secara bentuk memang begitu, tetapi penggolongan morfologis yang baku untuk kata ini perlu dipastikan. |
| r13 | Wazan I dari akar ط ع م ditulis طَعِمَ (pola فَعِلَ). Keyakinan **sedang**; perlu dipastikan harakat huruf tengahnya. |
| r12 | حَاسِب (pola فَاعِل, "penghitung") memang terbentuk secara teratur, tetapi kelaziman pemakaiannya dalam MSA perlu diperiksa. |

---

## F. Keputusan desain, bukan fakta bahasa

Hal-hal berikut adalah pilihan penyusun, dan sebaiknya diubah bila tidak cocok:

0. **Contoh kalimat untuk وَقْت (v132)** diganti pada pass kedua karena مَا الْوَقْتُ؟ kurang lazim dibanding كَمِ السَّاعَةُ؟ untuk menanyakan jam. Perlu dipastikan apakah penjelasan di `note` sudah memadai.
1. **Lema ditulis bentuk waqf** (huruf terakhir tanpa harakat, seperti kamus),
   sedangkan **contoh kalimat ditulis berharakat penuh termasuk i'rab**.
   Validator di `arabdrill/arabic.py` menegakkan dua aturan berbeda ini.
2. **Jeda Leitner 0, 1, 3, 7, 16 hari** adalah angka praktis yang lazim dipakai
   pada kartu Leitner, **bukan hasil pengukuran** pada pengguna mana pun.
   Ubah `INTERVALS` di `arabdrill/leitner.py` bila jadwal lain lebih cocok.
3. **Pembagian 6 tahap** dan isi masing-masing tahap adalah pilihan pedagogis,
   bukan standar yang berlaku umum.
4. **Angka pada jadwal 6 minggu di README** berasal dari simulasi penjadwal
   dengan asumsi ketepatan jawaban 85%, bukan dari pengamatan pembelajar nyata.
5. **Transliterasi mengikuti tulisan, bukan lafal**: هَذَا dialihhurufkan
   menjadi `hadha`, padahal dilafalkan `hadha` dengan a panjang pertama.
   Pilihan ini dibuat supaya transliterasi tidak pernah menambahkan informasi
   yang tidak ada dalam tulisan.
6. **Pengecoh pada soal pilihan ganda buatan otomatis** disaring supaya tidak
   ada dua jawaban benar, tetapi tingkat kesukarannya tidak diatur. Sebagian
   pengecoh mungkin terlalu mudah ditebak.

---

## G. Yang TIDAK bisa diperiksa mesin

Pengujian di `tests/` memeriksa hal-hal yang bisa diperiksa secara mekanis:
id unik, tidak ada field kosong, Unicode Arab sah dan ber-NFC, kelengkapan
harakat menurut aturan ortografis, huruf akar muncul pada kata turunannya,
setiap soal punya tepat satu jawaban benar, kunci jawaban sama dengan datanya,
dan hasil ekspor mutakhir.

Yang **tidak** diperiksa mesin, dan karena itu perlu ditinjau manusia:

- Apakah arti Bahasa Indonesia sudah tepat dan wajar.
- Apakah gender dan bentuk jamak sudah benar.
- Apakah akar yang dicantumkan memang akar kata itu (mesin hanya memeriksa
  bahwa huruf-hurufnya muncul berurutan — كَبِير dan ك ب ر akan lolos, dan
  begitu juga akar keliru yang kebetulan hurufnya cocok).
- Apakah contoh kalimat benar secara nahwu dan terdengar wajar bagi penutur.
- Apakah i'rab pada setiap contoh sudah tepat.
- Apakah penjelasan tata bahasa tidak menyederhanakan secara menyesatkan.
- Apakah makna klasik di Modul 5 sesuai dengan kamus rujukan.
