import cv2
import mediapipe as mp
import numpy as np
import math
import os

# Import modul buatan sendiri
import config as cfg
import utils

# SETUP & LOAD ASSETS
print("Memuat aset...")

# Load semua aset gambar menggunakan loop dari config
assets = {}
for key, filename in cfg.ASSET_FILES.items():
    assets[key] = utils.load_and_scale(filename, cfg.SCALE_FACTOR)

# Load Background
bg_source = None
if os.path.exists(cfg.BG_PATH):
    print("✅ Background ditemukan.")
    bg_source = cv2.imread(cfg.BG_PATH)
else:
    print("⚠️ Background tidak ditemukan. Akan menggunakan layar putih.")

# MAIN LOOP
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles 

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

with mp_holistic.Holistic(model_complexity=1, refine_face_landmarks=True) as holistic:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Setup Avatar Background
        if bg_source is not None:
            avatar = cv2.resize(bg_source, (w, h))
        else:
            avatar = np.ones((h, w, 3), dtype=np.uint8) * 255 
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(frame_rgb)
        
        # Gambar skeleton di window kamera
        if results.pose_landmarks:
             mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                 landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

        # LOGIKA AVATAR
        if results.pose_landmarks:
            GESER_GLOBAL_Y = 0 

            def get_pt(idx):
                lm = results.pose_landmarks.landmark[idx]
                return (int(lm.x * w), int(lm.y * h) + GESER_GLOBAL_Y)
            
            # AMBIL KOORDINAT PENTING
            p_nose = get_pt(0)   # Hidung
            p_sh_l, p_sh_r = get_pt(11), get_pt(12) # Bahu
            p_elbow_l = get_pt(13) # Siku Kiri
            p_wrist_l, p_wrist_r = get_pt(15), get_pt(16) # Pergelangan
            p_ankle_l, p_ankle_r = get_pt(27), get_pt(28)
            p_hip_l, p_hip_r = get_pt(23), get_pt(24)

            center_sh = ((p_sh_l[0] + p_sh_r[0]) // 2, (p_sh_l[1] + p_sh_r[1]) // 2)
            center_hips = ((p_hip_l[0] + p_hip_r[0]) // 2, (p_hip_l[1] + p_hip_r[1]) // 2)
            shoulder_width = math.dist(p_sh_l, p_sh_r)
            
            # Hitung rotasi dan skala dinamis
            base_scale = shoulder_width / 150.0 
            body_tilt = utils.calc_angle(center_sh, center_hips) 

            # HITUNG POSISI BAGIAN TUBUH
            # Menggunakan konstanta dari config.py (HEAD_X, HEAD_Y, dll disesuaikan manual atau dipindah ke config)
            pos_head  = utils.rotate_offset(center_sh, 0, -119, body_tilt, base_scale)
            pos_leg_r = utils.rotate_offset(center_sh, 32, 170, body_tilt, base_scale)
            pos_leg_l = utils.rotate_offset(center_sh, -32, 170, body_tilt, base_scale)
            pos_arm_r = utils.rotate_offset(center_sh, -85, 0, body_tilt, base_scale)
            pos_arm_l = utils.rotate_offset(center_sh, 85, 0, body_tilt, base_scale)

            # Fungsi render helper lokal untuk akses variable avatar & base_scale
            def render_part(img_source, pivot, angle):
                if img_source is None: return
                cur_h, cur_w = img_source.shape[:2]
                dyn_w = max(1, int(cur_w * base_scale))
                dyn_h = max(1, int(cur_h * base_scale))
                img_zoomed = cv2.resize(img_source, (dyn_w, dyn_h), interpolation=cv2.INTER_NEAREST)
                utils.overlay_rotated_image(avatar, img_zoomed, pivot, angle)

            # RENDER BADAN & KAKI
            render_part(assets['leg_right'], pos_leg_r, utils.calc_angle(p_hip_l, p_ankle_l))
            render_part(assets['leg_left'], pos_leg_l, utils.calc_angle(p_hip_r, p_ankle_r))
            render_part(assets['body'], center_sh, body_tilt)

            # LOGIKA EKSPRESI WAJAH
            current_head_img = assets['head'].copy() 
            if results.face_landmarks:
                fl = results.face_landmarks.landmark
                l_eye = utils.get_blink_ratio(fl, 159, 145, 33, 133)
                r_eye = utils.get_blink_ratio(fl, 386, 374, 362, 263)
                mouth = utils.get_mouth_ratio(fl, 13, 14, 78, 308)
                
                is_melotot = (r_eye > cfg.THRESH_EYE_WIDE) and (l_eye > cfg.THRESH_EYE_WIDE)

                if is_melotot:
                    current_head_img = utils.overlay_image_alpha(
                        current_head_img, assets['eye_wide'], cfg.POS_MELOTOT[0], cfg.POS_MELOTOT[1])
                else:
                    if r_eye < cfg.THRESH_EYE_CLOSED:
                        current_head_img = utils.overlay_image_alpha(
                            current_head_img, assets['eye_r_close'], cfg.POS_MATA_KANAN[0], cfg.POS_MATA_KANAN[1])
                    if l_eye < cfg.THRESH_EYE_CLOSED:
                        current_head_img = utils.overlay_image_alpha(
                            current_head_img, assets['eye_l_close'], cfg.POS_MATA_KIRI[0], cfg.POS_MATA_KIRI[1])

                if mouth > cfg.THRESH_MOUTH_OPEN:
                    current_head_img = utils.overlay_image_alpha(
                        current_head_img, assets['mouth_open'], cfg.POS_MULUT[0], cfg.POS_MULUT[1])
            
            # Render Kepala
            render_part(current_head_img, pos_head, body_tilt)
            
            # Render Tangan
            render_part(assets['arm_right'], pos_arm_r, utils.calc_angle(p_sh_r, p_wrist_r))
            render_part(assets['arm_left'], pos_arm_l, utils.calc_angle(p_sh_l, p_wrist_l))

            # LOGIKA DETEKSI ANGKAT TANGAN KIRI
            hand_above_head = p_wrist_l[1] < p_nose[1]
            elbow_above_shoulder = p_elbow_l[1] < p_sh_l[1]

            if hand_above_head and elbow_above_shoulder:
                cv2.putText(avatar, "NEIN!!", (150, 300), cv2.FONT_HERSHEY_SIMPLEX, 
                            3.0, (0, 0, 255), 5, cv2.LINE_AA)

        cv2.imshow('Om Kumis di Paris Minecraft', avatar)
        cv2.imshow('Kamera', frame) 
        if cv2.waitKey(5) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()