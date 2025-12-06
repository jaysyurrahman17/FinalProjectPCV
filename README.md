## 🎥 2D Real-time VTuber System with MediaPipe

Project ini adalah implementasi sistem Virtual YouTuber (VTuber) 2D sederhana menggunakan Python. Sistem ini menangkap gerakan tubuh dan ekspresi wajah pengguna melalui webcam secara real-time tanpa memerlukan peralatan motion capture mahal, hanya menggunakan Computer Vision.

#🚀 Fitur Utama

Pose Tracking (Full Body): Menggerakkan badan, tangan, dan kaki avatar mengikuti gerakan pengguna.

Face Expression Tracking:

* Deteksi Kedipan Mata (Kanan/Kiri).

Deteksi Mulut Terbuka.

Ekspresi Khusus "Melotot" (Mata terbuka lebar).

Dynamic Scaling & Rotation: Avatar dapat membesar/mengecil (Zoom) saat pengguna mendekat ke kamera, dan badan dapat miring mengikuti postur tubuh.

Gesture Detection: Deteksi gerakan spesifik (misal: Mengangkat tangan kiri di atas kepala) untuk memicu teks visual ("NEIN!!").

🛠️ Teknologi & Konsep Teknis

Project ini dibangun dengan pendekatan modular menggunakan pustaka berikut:

MediaPipe Holistic: Untuk mendeteksi 33 landmarks tubuh dan 468 landmarks wajah.

OpenCV (cv2): Untuk manipulasi citra (image processing).

NumPy: Untuk operasi matriks dan kalkulasi geometri vektor.

Alur Kerja (Workflow)

Input: Frame diambil dari Webcam.

Inference: MediaPipe memprediksi koordinat sendi (x, y).

Normalisasi: Koordinat dinormalisasi ke resolusi layar.

Geometri:

Menghitung sudut rotasi antar sendi (misal: Bahu ke Siku) menggunakan atan2.

Menghitung skala avatar berdasarkan lebar bahu pengguna.

Rendering (Painter's Algorithm):

Aset gambar (PNG transparan) ditempel (overlay) dari urutan paling belakang ke depan (Kaki -> Badan -> Kepala -> Tangan).

Menggunakan teknik Alpha Blending untuk transparansi yang halus.

📂 Struktur File

. ├── config.py       # Konfigurasi konstanta (Threshold, Path File, Warna) ├── utils.py        # Fungsi utilitas (Load gambar, Matematika Vektor, Alpha Blending) ├── main.py         # Main Loop program dan logika rendering ├── background.jpg  # Latar belakang avatar └── assets/         # Folder berisi potongan gambar tubuh (Kepala, Tangan, Badan, dll) 

🧠 Penjelasan Logika Kunci

1. Alpha Blending

Untuk menempelkan bagian tubuh (PNG) ke latar belakang tanpa kotak hitam, digunakan rumus:


$$Pixel_{result} = (\alpha \times Pixel_{FG}) + ((1 - \alpha) \times Pixel_{BG})$$


Dimana $\alpha$ adalah channel transparansi dari gambar aset.

2. Rotasi 2D (Affine Transformation)

Agar tangan dan badan bisa miring, gambar diputar menggunakan matriks rotasi sebelum ditempel:

M = cv2.getRotationMatrix2D(center, angle, scale)
rotated_img = cv2.warpAffine(img, M, (new_w, new_h))


📦 Cara Menjalankan

Install Dependensi:

pip install opencv-python mediapipe numpy


Siapkan Aset: Pastikan folder berisi gambar .png untuk bagian tubuh (wajah, badan, tangan, dll) sesuai nama di config.py.

Jalankan:

python main.py


📝 Catatan Pengembang

Sistem ini menggunakan pendekatan 2D rigging sederhana. Keterbatasan utama adalah tidak adanya informasi kedalaman (Z-axis) yang akurat, sehingga tumpukan gambar (layering) bersifat statis.


