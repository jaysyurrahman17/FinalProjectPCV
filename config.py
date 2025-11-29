# KONFIGURASI & KONSTANTA

# Skala Ukuran Avatar
SCALE_FACTOR = 15

# Threshold (Ambang Batas) Deteksi
THRESH_EYE_CLOSED = 0.22   
THRESH_MOUTH_OPEN = 0.40   
THRESH_EYE_WIDE = 0.50     

# Posisi Bagian Wajah (Offset Pixel)
POS_MATA_KANAN = (135, 0) 
POS_MATA_KIRI  = (75, 0)
POS_MULUT      = (75, 25)
POS_MELOTOT    = (135, 45)  

# Nama File Aset Gambar
ASSET_FILES = {
    'head':      "gambar/wajah.png",
    'body':      "gambar/badan.png",
    'arm_right': "gambar/tangankanan.png",
    'arm_left':  "gambar/tangankiri.png",
    'leg_right': "gambar/kakikanan.png",
    'leg_left':  "gambar/kakikiri.png",
    'eye_r_close': "gambar/matakanantutup.png",
    'eye_l_close': "gambar/matakiritutup.png",
    'mouth_open':  "gambar/mulutbuka.png",
    'eye_wide':    "gambar/matamelotot.png",
}

BG_PATH = "gambar/background.jpg"