---
name: photo-restoration
description: Gunakan ketika pengguna meminta restorasi, deblur, perbaikan kerusakan, retouch, peningkatan kualitas, atau penyempurnaan potret/foto lama.
---

# Master Photo Restoration

## Tujuan

Menghasilkan edit foto yang realistis dan profesional. Perlakukan foto yang diberikan sebagai sumber kebenaran visual. Prioritas utama adalah menjaga identitas subjek dan ciri khas sumber, bukan mengubahnya menjadi wajah generik yang dianggap cantik oleh model.

## Cara kerja

1. **Jika foto sudah dilampirkan dan pengguna meminta edit**, kerjakan pengeditan gambar secara langsung dengan kemampuan edit gambar yang tersedia. Jangan hanya membalas dengan prompt atau tutorial. Jika tidak ada foto, minta pengguna mengunggah foto yang akan dipulihkan.
2. Tentukan jenis pekerjaan dari instruksi pengguna:
   - **Restorasi konservatif**: foto lama/rusak; pulihkan kerusakan sambil mempertahankan pose, ekspresi, pakaian, komposisi, dan latar.
   - **Peningkatan potret profesional**: lakukan restorasi ditambah koreksi cahaya, warna, framing, serta retouch ringan yang tetap natural.
   - **Perubahan pose atau arah tatapan**: lakukan hanya jika diminta secara eksplisit. Ini merupakan rekonstruksi generatif, bukan restorasi dokumenter murni. Perubahan harus minimal dan tetap menjaga identitas.
3. Terapkan prioritas ketika instruksi berkonflik: (a) identitas dan ciri wajah asli, (b) permintaan eksplisit pengguna, (c) pelestarian pakaian/latar/komposisi, (d) estetika tambahan. Jangan mengubah bentuk mata, hidung, bibir, alis, rahang, garis rambut, usia tampak, atau proporsi wajah demi simetri kosmetik.
4. Kerjakan hanya sejauh detail sumber mendukung. Jika detail hilang total atau tertutup kerusakan, rekonstruksi secara konservatif dan masuk akal; jangan mengklaim hasilnya sebagai detail asli yang pasti.
5. Keluarkan hasil gambar. Jelaskan keterbatasan resolusi atau rekonstruksi hanya bila relevan; jangan membanjiri pengguna dengan catatan teknis yang tidak diminta.

## Preset restorasi v3.0

Gunakan spesifikasi berikut sebagai arah kualitas, bukan klaim teknis yang tidak bisa diverifikasi:

### Restorasi dan kejernihan
- Hilangkan debu, noda, goresan, jamur, artefak kompresi, banding, serta noise yang terlihat.
- Kurangi blur dan tingkatkan kejernihan tepi secara terukur. Jangan menciptakan detail mata, gigi, tekstur kulit, rambut, atau kain yang hiper-detail tanpa dukungan visual.
- Pulihkan piksel rusak dan tepi objek dengan rekonstruksi yang konsisten terhadap foto.
- Pertahankan tekstur kulit dan pori halus; hindari kulit plastik, penghalusan berlebihan, sharpening halo, serta tampilan HDR artifisial.

### Wajah dan identitas
- Pertahankan identitas dengan prioritas sangat tinggi: bentuk wajah, mata, hidung, bibir, alis, rahang, jarak antarfitur, dan ekspresi asli.
- Buat mata lebih terbaca secara alami tanpa mengubah warna iris secara spekulatif, memperbesar mata, atau memutihkan bagian putih mata secara berlebihan.
- Kurangi noda sementara secara ringan. Jangan menghapus ciri permanen seperti tahi lalat atau bekas luka khas kecuali pengguna meminta secara spesifik.
- Jangan menambahkan riasan tebal, mengubah usia, mengubah jenis kelamin, atau membuat wajah menjadi simetris sempurna.
- **Arah wajah/tatapan:** default-nya pertahankan pose dan arah mata asli. Jika pengguna secara khusus meminta wajah dan tatapan lurus ke depan, buat penyesuaian sekecil mungkin. Jangan memaksakan rotasi yang memerlukan penciptaan banyak bagian wajah yang tidak terlihat; bila perlu, prioritaskan identitas dan hasilkan perubahan yang konservatif.

### Cahaya dan warna
- Seimbangkan exposure, white balance, kontras, dan rentang tonal; pertahankan detail highlight dan bayangan.
- Untuk potret studio, arahkan ke cahaya frontal yang lembut dan merata, fill light halus, highlight terkendali, serta bayangan wajah/leher yang lebih ringan tanpa menghapus seluruh bentuk alami wajah.
- Pertahankan warna kulit asli dan warna objek yang masuk akal. Gunakan warna netral, sedikit hangat bila cocok dengan sumber, vibrance sedang, dan saturasi realistis.
- Hindari clipping, warna kulit oranye/abu-abu, hitam keruh, kontras berlebihan, serta grading sinematik yang mengubah suasana asli tanpa diminta.

### Pakaian, hijab, rambut, dan latar
- Pertahankan gaya, potongan, warna, pola, kancing, saku, serta detail pakaian. Jika pakaian berwarna hitam, pertahankan hitam yang kaya tetapi tetap bertekstur.
- Rapikan kerutan dan tepi kain secukupnya. Pertahankan tekstur tenunan dan jangan menggambar ulang detail pakaian secara spekulatif.
- Rapikan rambut atau jilbab seperlunya. Koreksi ketidakteraturan kecil dan simetri hanya jika tidak mengubah bentuk atau gaya aslinya.
- Pertahankan latar asli secara default. Bersihkan noda atau banding yang mengganggu dan perluas latar hanya bila diminta atau diperlukan untuk framing. Jangan mengganti latar secara diam-diam.

### Framing dan karakter kamera
- Orientasi potret dan zoom-out ringan hanya jika komposisi sumber memungkinkan tanpa menciptakan tubuh atau lingkungan baru yang tidak didukung.
- Tampilan setara potret studio profesional: detail jelas, microcontrast alami, warna netral, dan perspektif yang tidak berlebihan.
- Referensi estetika Canon EOS R5 dengan lensa prime 50 mm f/1.8 hanya sebagai inspirasi visual. Jangan menyatakan bahwa foto benar-benar diambil dengan kamera/lensa tersebut atau menambahkan bokeh yang tidak sesuai sumber.

## Spesifikasi keluaran dan kejujuran teknis

- Target ideal pengguna dapat mencakup PNG, sRGB, 16-bit bila didukung, dan resolusi tinggi hingga 8K. Namun **jangan menjanjikan ukuran 8K, 6000×4000, DPI 762, 16-bit, atau metadata kamera** kecuali alat keluaran benar-benar mendukung dan memverifikasinya.
- Resolusi piksel dan DPI adalah hal berbeda. Jangan mengubah angka DPI seolah-olah menambah detail gambar. Jika editor hanya mengeluarkan resolusi tertentu, gunakan hasil terbaik yang tersedia dan jangan mengklaim telah melakukan upscaling bila tidak dilakukan.
- Bila alat memungkinkan pemilihan format, utamakan PNG dan sRGB untuk hasil akhir. Jangan mengklaim bit depth atau profil warna tersemat kecuali telah dipastikan.
- Jangan menambahkan transparansi; latar tetap buram/opaque kecuali pengguna meminta sebaliknya.

## Negative constraints

Hindari: wajah berubah, identitas meleset, ekspresi baru, kulit plastik, mata/gigi terlalu putih, tekstur palsu, bayangan keras, wajah terlalu rata, pergeseran warna, oversaturation, sharpening halo, detail kain yang berulang, latar berubah tanpa izin, artefak generatif, dan klaim resolusi atau spesifikasi ekspor yang tidak terverifikasi.

## Pemeriksaan akhir

Sebelum menyerahkan hasil, periksa secara visual:
- Identitas, ekspresi, dan proporsi wajah tetap konsisten.
- Tidak ada noda/kerusakan yang terlewat jelas, artefak baru, atau tepi halo.
- Kulit, mata, rambut, jilbab, kain, dan latar masih memiliki tekstur alami.
- Cahaya dan warna konsisten serta tidak ada bagian penting yang clipping.
- Pakaian dan latar tidak berubah di luar permintaan.
- Klaim resolusi, format, bit depth, dan DPI sesuai kemampuan nyata alat.
