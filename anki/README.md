# anki/ — ekspor untuk Anki

Berkas di folder ini **dibuat ulang** oleh `tools/build_exports.py` dari
`data/*.json`. Jangan menyuntingnya langsung; sunting datanya lalu jalankan:

```bash
python tools/build_exports.py
```

## Berkas

| Berkas | Jumlah kartu | Isi |
|:-------|-------------:|:----|
| `kosakata.csv` | 188 | Modul 1: kosakata inti |
| `tatabahasa.csv` | 60 | Modul 2: soal tata bahasa |
| `akar.csv` | 85 | Modul 3: kata-kata per keluarga akar |
| `baca.csv` | 42 | Modul 4: kalimat tanpa harakat dan bacaan penuhnya |
| `quran-msa.csv` | 18 | Modul 5: kata yang maknanya bergeser |

## Cara impor

1. Anki: **File → Import**, pilih berkasnya.
2. Pilih jenis catatan (note type) yang jumlah fieldnya cukup. Untuk
   `kosakata.csv` diperlukan **8 field**; untuk berkas lain lihat tabel di bawah.
3. Petakan setiap kolom ke field sesuai tabel. Kolom terakhir adalah **Tags**.
4. Pastikan "Allow HTML in fields" **dimatikan**, kecuali untuk
   `tatabahasa.csv` yang memakai `<br>` pada sisi depan.

Tiga baris pertama setiap berkas adalah pengarah untuk Anki 2.1.55 ke atas:

```
#separator:Comma
#html:false
#tags column:N
```

Anki versi tersebut dan yang lebih baru membaca pengarah itu, lalu langsung
memakai pemisah serta kolom tag yang benar. Bila Anki Anda lebih tua dan menolak
berkasnya, **hapus tiga baris itu** lalu atur pemisah dan kolom tag secara
manual di jendela impor.

Tidak ada baris judul (header) pada data, sesuai cara Anki membaca CSV.
Pengkodean berkas adalah UTF-8 tanpa BOM.

## Pemetaan kolom

### kosakata.csv (8 kolom)

| # | Field | Contoh |
|--:|:------|:-------|
| 1 | Kata Arab (berharakat) | كِتَاب |
| 2 | Arti | buku |
| 3 | Keterangan | ism · mudzakkar · jamak: كُتُب · akar: ك ت ب |
| 4 | Contoh kalimat | الْكِتَابُ عَلَى الْمَكْتَبِ. |
| 5 | Arti contoh | Buku itu ada di atas meja. |
| 6 | Alih huruf | kitāb |
| 7 | Catatan | (boleh kosong) |
| 8 | **Tags** | `arab::kosakata arab::asyya arab::tahap2` |

### tatabahasa.csv (5 kolom)

| # | Field |
|--:|:------|
| 1 | Pertanyaan (kadang memuat `<br>` lalu teks Arabnya) |
| 2 | Jawaban |
| 3 | Penjelasan |
| 4 | Judul topik |
| 5 | **Tags** |

### akar.csv (7 kolom)

| # | Field |
|--:|:------|
| 1 | Kata Arab |
| 2 | Arti |
| 3 | Akar |
| 4 | Makna akar |
| 5 | Pola (wazan) |
| 6 | Alih huruf |
| 7 | **Tags** |

### baca.csv (5 kolom)

| # | Field |
|--:|:------|
| 1 | Kalimat **tanpa harakat** (sisi depan) |
| 2 | Kalimat berharakat penuh (sisi belakang) |
| 3 | Arti |
| 4 | Level atau penjelasan |
| 5 | **Tags** |

### quran-msa.csv (6 kolom)

| # | Field |
|--:|:------|
| 1 | Kata Arab |
| 2 | Makna dalam MSA |
| 3 | Makna dalam bahasa Arab klasik |
| 4 | Jenis pergeseran |
| 5 | Catatan |
| 6 | **Tags** |

## Saran pemakaian

- **Kartu dua arah.** Untuk `kosakata.csv`, buat dua jenis kartu dari satu
  catatan: Arab→Indonesia (pengenalan) dan Indonesia→Arab (produksi). Keduanya
  melatih hal yang berbeda.
- **Sembunyikan alih huruf.** Field alih huruf sengaja dipisah supaya bisa
  tidak ditampilkan pada template kartu Anda. Pengguna yang sudah bisa membaca
  tulisan Arab sebaiknya tidak melihatnya secara bawaan.
- **Kartu `baca.csv`** paling baik dipakai satu arah saja: depan tanpa harakat,
  belakang berharakat penuh. Arah sebaliknya tidak melatih apa pun.
- **Jadwal Anki vs Leitner.** Anki memakai algoritme penjadwalannya sendiri.
  Bila Anda memakai Anki, pakailah penjadwalan Anki dan jangan menjalankan
  `quiz.py` untuk materi yang sama, supaya satu kartu tidak dijadwalkan dua
  sistem sekaligus. `progress.json` dan koleksi Anki tidak saling tahu.
