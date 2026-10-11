# sources/ — berkas sumber yang Anda sediakan sendiri

Folder ini **kosong secara bawaan**, dan proyek ini bekerja penuh tanpa isinya.

## Mengapa folder ini ada

Modul 5 (`data/quran_msa.json`) membandingkan makna sejumlah kata dalam bahasa
Arab klasik dengan makna yang lazim dalam Bahasa Arab Baku Modern. Perbandingan
itu ditulis **tanpa satu pun kutipan ayat Al-Qur'an**, karena menulis ayat dari
ingatan berisiko salah huruf, salah harakat, atau salah rujukan.

Bila Anda ingin memakai ayat sebagai contoh, sediakan sendiri teksnya di
folder ini, dari mushaf atau sumber digital yang Anda percayai.

## Cara menambahkan

1. Letakkan berkas teks mushaf di folder ini, misalnya `quran-uthmani.txt`.
   Format yang paling mudah dipakai adalah satu ayat per baris dengan rujukan
   di depannya:

   ```
   2:255|<teks ayat>
   12:10|<teks ayat>
   ```

   Pemisah boleh `|` atau tab. Yang penting setiap baris memuat nomor surah,
   nomor ayat, dan teksnya.

2. Pada entri yang bersangkutan di `data/quran_msa.json`, isi field
   `quran_examples` dengan rujukannya:

   ```json
   "quran_examples": [
     { "ref": "12:10", "catatan": "سَيَّارَة bermakna kafilah" }
   ]
   ```

3. Jalankan pengujian:

   ```bash
   python -m pytest tests/test_sources.py
   ```

## Aturan yang ditegakkan pengujian

`tests/test_sources.py` memeriksa:

- Selama folder ini kosong, setiap field `quran_examples` **harus** kosong.
  Entri yang mengaku punya contoh ayat tanpa berkas sumber akan membuat
  pengujian gagal.
- Setiap isi `quran_examples` wajib memuat rujukan berbentuk `surah:ayat`.
- Modul 1 sampai 4 tidak boleh memuat rujukan berbentuk `surah:ayat`
  sama sekali.

## Catatan

- Berkas di folder ini tidak dibaca sebagai kode dan tidak dieksekusi; ia
  hanya menjadi penanda bahwa sumbernya tersedia, serta rujukan bagi Anda saat
  menyalin teks ayat.
- Untuk memahami makna sebuah kata **di dalam** sebuah ayat, rujuklah kitab
  tafsir atau kamus khusus Al-Qur'an. Kolom `classical` di Modul 5 hanya
  memuat makna kamus klasik secara umum.
