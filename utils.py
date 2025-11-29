import cv2
import numpy as np
import math
import os

# FUNGSI OLAH GAMBAR & MATEMATIKA

def load_and_scale(path, scale_factor=0.5):
    """Memuat gambar dan mengubah ukurannya."""
    if not os.path.exists(path):
        # Jika file ekspresi tidak ada, return None agar tidak error
        if "tutup" in path or "buka" in path or "melotot" in path: return None
        
        # Jika aset utama hilang, buat dummy kotak warna ungu
        # print(f"❌ File tidak ditemukan: {path}") 
        dummy = np.zeros((32, 32, 4), dtype=np.uint8)
        dummy[:] = (255, 0, 255, 255) 
        return dummy

    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None: return None

    # Format BGRA (agar ada transparansi)
    if img.shape[2] == 3: 
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    h, w = img.shape[:2]
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)
    return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_NEAREST)

def overlay_image_alpha(bg, fg, x, y):
    """Menempelkan gambar foreground (fg) ke background (bg) dengan transparansi."""
    if fg is None: return bg
    h_fg, w_fg = fg.shape[:2]
    h_bg, w_bg = bg.shape[:2]
    
    if x >= w_bg or y >= h_bg: return bg
    
    x1, y1 = max(x, 0), max(y, 0)
    x2, y2 = min(x + w_fg, w_bg), min(y + h_fg, h_bg)
    
    fg_x1 = x1 - x
    fg_y1 = y1 - y
    fg_x2 = fg_x1 + (x2 - x1)
    fg_y2 = fg_y1 + (y2 - y1)
    
    if x2 <= x1 or y2 <= y1: return bg
    
    bg_slice = bg[y1:y2, x1:x2]
    fg_slice = fg[fg_y1:fg_y2, fg_x1:fg_x2]
    
    alpha_fg = fg_slice[:, :, 3] / 255.0
    alpha_bg = 1.0 - alpha_fg
    
    for c in range(0, 3):
        bg_slice[:, :, c] = (alpha_fg * fg_slice[:, :, c] + alpha_bg * bg_slice[:, :, c])
    
    bg_slice[:, :, 3] = (alpha_fg * fg_slice[:, :, 3] + alpha_bg * bg_slice[:, :, 3])
    bg[y1:y2, x1:x2] = bg_slice
    return bg

def overlay_rotated_image(canvas, img, pivot_point, angle_degrees):
    """Memutar gambar berdasarkan pivot dan menempelkannya ke canvas."""
    if img is None: return
    h, w = img.shape[:2]
    center_of_rotation = (w // 2, 0) 
    M = cv2.getRotationMatrix2D(center_of_rotation, -angle_degrees, 1.0)
    
    cos, sin = np.abs(M[0, 0]), np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))
    
    M[0, 2] += (new_w / 2) - center_of_rotation[0]
    M[1, 2] += (new_h / 2) - center_of_rotation[1]

    rotated = cv2.warpAffine(img, M, (new_w, new_h), flags=cv2.INTER_NEAREST)

    x_offset = int(pivot_point[0] - (new_w / 2))
    y_offset = int(pivot_point[1] - (new_h / 2))

    y1, y2 = y_offset, y_offset + new_h
    x1, x2 = x_offset, x_offset + new_w

    if y1 < 0: y1 = 0
    if x1 < 0: x1 = 0
    if y2 > canvas.shape[0]: y2 = canvas.shape[0]
    if x2 > canvas.shape[1]: x2 = canvas.shape[1]
    
    img_y1, img_y2 = y1 - y_offset, y1 - y_offset + (y2 - y1)
    img_x1, img_x2 = x1 - x_offset, x1 - x_offset + (x2 - x1)

    if img_y2 <= img_y1 or img_x2 <= img_x1: return

    slice_canvas = canvas[y1:y2, x1:x2]
    slice_img = rotated[img_y1:img_y2, img_x1:img_x2]

    if slice_img.shape[2] == 4:
        alpha_s = slice_img[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        for c in range(0, 3):
            slice_canvas[:, :, c] = (alpha_s * slice_img[:, :, c] + alpha_l * slice_canvas[:, :, c])
    else:
        slice_canvas[:] = slice_img 
    canvas[y1:y2, x1:x2] = slice_canvas

def rotate_offset(origin, offset_x, offset_y, angle_degrees, scale):
    """Menghitung pergeseran koordinat saat tubuh miring."""
    rad = math.radians(angle_degrees)
    ox = offset_x * scale
    oy = offset_y * scale
    shift_x = ox * math.cos(rad) - oy * math.sin(rad)
    shift_y = ox * math.sin(rad) + oy * math.cos(rad)
    return (int(origin[0] + shift_x), int(origin[1] + shift_y))

def get_blink_ratio(landmarks, idx_up, idx_down, idx_left, idx_right):
    """Menghitung rasio mata (EAR) sederhana."""
    v_dist = math.dist((landmarks[idx_up].x, landmarks[idx_up].y), (landmarks[idx_down].x, landmarks[idx_down].y))
    h_dist = math.dist((landmarks[idx_left].x, landmarks[idx_left].y), (landmarks[idx_right].x, landmarks[idx_right].y))
    return v_dist / (h_dist + 1e-6)

def get_mouth_ratio(landmarks, idx_top, idx_bottom, idx_left, idx_right):
    """Menghitung rasio mulut."""
    v_dist = math.dist((landmarks[idx_top].x, landmarks[idx_top].y), (landmarks[idx_bottom].x, landmarks[idx_bottom].y))
    h_dist = math.dist((landmarks[idx_left].x, landmarks[idx_left].y), (landmarks[idx_right].x, landmarks[idx_right].y))
    return v_dist / (h_dist + 1e-6)

def calc_angle(p1, p2):
    """Menghitung sudut antara dua titik."""
    dy, dx = p2[1] - p1[1], p2[0] - p1[0]
    return math.degrees(math.atan2(dy, dx)) - 90