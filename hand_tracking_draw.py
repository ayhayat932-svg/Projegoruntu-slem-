"""
El Takibi ile Çizim Uygulaması - Komple Paket v2
--------------------------------------------------
Gerekli kütüphaneleri yüklemek için:
    pip install opencv-python mediapipe numpy

Kontroller:
    JESTLER (İki el de desteklenir):
      - 1 parmak (işaret)        : çizim
      - 2 parmak (işaret + orta) : renk seçimi (sadece üst şerit üzerinde)
      - Silmek için paletten SILGI seç
    KLAVYE:
      - s : çizimi PNG olarak kaydet
      - z : son işlemi geri al
      - c : tüm ekranı temizle
      - + : kalem kalınlığını artır
      - - : kalem kalınlığını azalt
      - q : çıkış
"""

import os
import cv2
import time
import numpy as np
import mediapipe as mp
from datetime import datetime


# ---------- El takibi sınıfı ----------
class HandTracker:
    def __init__(self, max_hands=2, detection_conf=0.7, tracking_conf=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_conf,
            min_tracking_confidence=tracking_conf,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None

    def find_hands(self, frame, draw=True):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lms, self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def hand_count(self):
        if self.results and self.results.multi_hand_landmarks:
            return len(self.results.multi_hand_landmarks)
        return 0

    def get_landmark_positions(self, frame, hand_no=0):
        landmark_list = []
        if self.results and self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                hand = self.results.multi_hand_landmarks[hand_no]
                h, w, _ = frame.shape
                for idx, lm in enumerate(hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append((idx, cx, cy))
        return landmark_list

    def fingers_up(self, landmarks):
        if not landmarks or len(landmarks) < 21:
            return [0, 0, 0, 0, 0]
        fingers = []
        fingers.append(1 if landmarks[self.tip_ids[0]][1] > landmarks[self.tip_ids[0] - 1][1] else 0)
        for i in range(1, 5):
            tip_y = landmarks[self.tip_ids[i]][2]
            pip_y = landmarks[self.tip_ids[i] - 2][2]
            fingers.append(1 if tip_y < pip_y else 0)
        return fingers


# ---------- Metalik yazı efekti ----------
def metallic_text(frame, text, pos, scale=0.7, thickness=2,
                  base=(230, 230, 230), shadow=(20, 20, 20),
                  highlight=(255, 255, 255), outline=(70, 70, 70)):
    x, y = pos
    font = cv2.FONT_HERSHEY_DUPLEX
    # gölge (aşağı-sağa kaydırılmış koyu)
    cv2.putText(frame, text, (x + 2, y + 2), font, scale, shadow, thickness + 2, cv2.LINE_AA)
    # dış hat
    cv2.putText(frame, text, (x, y), font, scale, outline, thickness + 2, cv2.LINE_AA)
    # ana metalik gövde
    cv2.putText(frame, text, (x, y), font, scale, base, thickness, cv2.LINE_AA)
    # üst ışık parıltısı
    cv2.putText(frame, text, (x, y - 1), font, scale, highlight, 1, cv2.LINE_AA)
    return frame


# ---------- Renk paleti ----------
PALETTE = [
    {"name": "MAVI",    "color": (255, 80, 40)},
    {"name": "YESIL",   "color": (60, 220, 80)},
    {"name": "KIRMIZI", "color": (60, 60, 235)},
    {"name": "SARI",    "color": (40, 220, 235)},
    {"name": "BEYAZ",   "color": (240, 240, 240)},
    {"name": "SILGI",   "color": (0, 0, 0)},
]

HEADER_HEIGHT = 95


def draw_header(frame, selected_idx, thickness):
    h, w, _ = frame.shape
    # metalik gradyan şerit (dikeyde koyudan açığa)
    for i in range(HEADER_HEIGHT):
        shade = 25 + int((i / HEADER_HEIGHT) * 50)
        cv2.line(frame, (0, i), (w, i), (shade, shade, shade), 1)
    # alt çizgi (metalik kenar)
    cv2.line(frame, (0, HEADER_HEIGHT - 1), (w, HEADER_HEIGHT - 1), (180, 180, 180), 2)

    box_w = w // (len(PALETTE) + 1)
    for i, item in enumerate(PALETTE):
        x1 = i * box_w
        x2 = x1 + box_w
        # kutunun ana renk bloğu
        cv2.rectangle(frame, (x1 + 8, 12), (x2 - 8, HEADER_HEIGHT - 14),
                      item["color"], cv2.FILLED)
        # metalik çerçeve
        cv2.rectangle(frame, (x1 + 8, 12), (x2 - 8, HEADER_HEIGHT - 14),
                      (200, 200, 200), 1)

        # yazı — silgi için açık, diğerleri için koyu zemin
        if item["name"] == "SILGI":
            metallic_text(frame, item["name"], (x1 + 14, 58), scale=0.7, thickness=2)
        else:
            # renkli zemin üstünde koyu metalik
            metallic_text(frame, item["name"], (x1 + 12, 58), scale=0.65, thickness=2,
                          base=(40, 40, 40), shadow=(255, 255, 255),
                          highlight=(10, 10, 10), outline=(240, 240, 240))

        # seçili olan kutuya altın/parlak çerçeve
        if i == selected_idx:
            cv2.rectangle(frame, (x1 + 4, 6), (x2 - 4, HEADER_HEIGHT - 8),
                          (0, 255, 255), 3)

    # kalınlık paneli
    x1 = len(PALETTE) * box_w
    x2 = w
    cv2.rectangle(frame, (x1 + 8, 12), (x2 - 8, HEADER_HEIGHT - 14),
                  (50, 50, 50), cv2.FILLED)
    cv2.rectangle(frame, (x1 + 8, 12), (x2 - 8, HEADER_HEIGHT - 14),
                  (200, 200, 200), 1)
    metallic_text(frame, f"KALINLIK {thickness}", (x1 + 12, 42), scale=0.55, thickness=1)
    cv2.circle(frame, ((x1 + x2) // 2, 72), max(2, thickness // 2),
               (220, 220, 220), cv2.FILLED)
    cv2.circle(frame, ((x1 + x2) // 2, 72), max(2, thickness // 2),
               (80, 80, 80), 1)
    return frame


def get_selected_index(x, y, frame_width):
    if y > HEADER_HEIGHT:
        return None
    box_w = frame_width // (len(PALETTE) + 1)
    idx = x // box_w
    if 0 <= idx < len(PALETTE):
        return idx
    return None


def save_canvas(canvas):
    os.makedirs("drawings", exist_ok=True)
    filename = datetime.now().strftime("drawings/drawing_%Y%m%d_%H%M%S.png")
    cv2.imwrite(filename, canvas)
    return filename


# ---------- Geometrik şekiller ----------
SHAPE_NAMES = {0: "SERBEST", 1: "CIZGI", 2: "DAIRE", 3: "DIKDORTGEN", 4: "UCGEN"}


def draw_shape(img, mode, p1, p2, color, thickness):
    if mode == 1:  # çizgi
        cv2.line(img, p1, p2, color, thickness, cv2.LINE_AA)
    elif mode == 2:  # daire
        cx, cy = (p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2
        r = int(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5 / 2)
        cv2.circle(img, (cx, cy), max(r, 1), color, thickness, cv2.LINE_AA)
    elif mode == 3:  # dikdörtgen
        cv2.rectangle(img, p1, p2, color, thickness, cv2.LINE_AA)
    elif mode == 4:  # üçgen (p1-p2 taban, tepe dikine yukarıda)
        x1, y1 = p1
        x2, y2 = p2
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        dx, dy = x2 - x1, y2 - y1
        apex = (int(mx - dy * 0.5), int(my + dx * 0.5))
        pts = np.array([p1, p2, apex], dtype=np.int32)
        cv2.polylines(img, [pts], True, color, thickness, cv2.LINE_AA)


# ---------- Ana döngü ----------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı. Başka bir uygulama kullanıyor olabilir.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    tracker = HandTracker(max_hands=2)

    canvas = None
    prev_points = {0: None, 1: None}  # her el için ayrı çizim takibi
    pending_shape_per_hand = {0: None, 1: None}  # şekil önizlemesi (el başına)
    shape_mode = 0  # 0=serbest, 1=çizgi, 2=daire, 3=dikdörtgen, 4=üçgen
    selected_idx = 2  # kırmızı
    thickness = 8
    eraser_thickness = 55
    undo_stack = []
    max_undo = 20
    toast_msg = ""
    toast_time = 0
    prev_time = 0
    finger_dot_colors = [
        (0, 255, 255),   # başparmak - sarı
        (0, 200, 255),   # işaret - turuncu
        (0, 255, 150),   # orta - yeşil
        (255, 200, 0),   # yüzük - cyan
        (255, 100, 200), # serçe - pembe
    ]

    def push_undo():
        undo_stack.append(canvas.copy())
        if len(undo_stack) > max_undo:
            undo_stack.pop(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kare alınamadı.")
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if canvas is None:
            canvas = np.zeros_like(frame)

        frame = tracker.find_hands(frame, draw=True)

        current_item = PALETTE[selected_idx]
        is_eraser = current_item["name"] == "SILGI"
        active_thickness = eraser_thickness if is_eraser else thickness
        draw_color = current_item["color"]

        num_hands = tracker.hand_count()
        active_hands = set()

        # Her eli bağımsız işle
        for hand_idx in range(num_hands):
            landmarks = tracker.get_landmark_positions(frame, hand_no=hand_idx)
            if not landmarks:
                continue
            active_hands.add(hand_idx)
            fingers = tracker.fingers_up(landmarks)
            index_tip = (landmarks[8][1], landmarks[8][2])

            # 5 parmak ucunu renkli noktalarla göster
            for i, tid in enumerate(tracker.tip_ids):
                fx, fy = landmarks[tid][1], landmarks[tid][2]
                cv2.circle(frame, (fx, fy), 9, finger_dot_colors[i], cv2.FILLED)
                cv2.circle(frame, (fx, fy), 11, (20, 20, 20), 2)

            # 2 parmak (işaret + orta) + header üzerinde -> renk seçimi
            if (fingers[1] == 1 and fingers[2] == 1
                    and index_tip[1] <= HEADER_HEIGHT):
                prev_points[hand_idx] = None
                pending_shape_per_hand[hand_idx] = None
                new_idx = get_selected_index(index_tip[0], index_tip[1], w)
                if new_idx is not None and new_idx != selected_idx:
                    selected_idx = new_idx
                    toast_msg = f"SECILDI: {PALETTE[new_idx]['name']}"
                    toast_time = time.time()

            # ŞEKIL modu (serbest değil ve silgi değilse) -> başparmak+işaret ile önizleme
            elif shape_mode != 0 and not is_eraser:
                prev_points[hand_idx] = None
                pending_shape_per_hand[hand_idx] = None
                if fingers[0] == 1 and fingers[1] == 1:
                    thumb_tip = (landmarks[4][1], landmarks[4][2])
                    if (thumb_tip[1] > HEADER_HEIGHT
                            and index_tip[1] > HEADER_HEIGHT):
                        pending_shape_per_hand[hand_idx] = (thumb_tip, index_tip)
                        # önizleme (sadece frame üzerinde, canvas'a basılmaz)
                        draw_shape(frame, shape_mode, thumb_tip, index_tip,
                                   draw_color, thickness)
                        # iki nokta arası rehber çizgi
                        cv2.line(frame, thumb_tip, index_tip,
                                 (180, 180, 180), 1, cv2.LINE_AA)

            # SILGI modu -> el konfigürasyonu fark etmez, tüm avuç ile sil
            elif is_eraser:
                palm_x, palm_y = landmarks[9][1], landmarks[9][2]
                wx, wy = landmarks[0][1], landmarks[0][2]
                mx, my = landmarks[12][1], landmarks[12][2]
                hand_size = int(((wx - mx) ** 2 + (wy - my) ** 2) ** 0.5)
                er_radius = max(45, hand_size)  # el büyüklüğüne göre yarıçap
                palm = (palm_x, palm_y)
                if palm_y > HEADER_HEIGHT:
                    if prev_points[hand_idx] is None:
                        prev_points[hand_idx] = palm
                        push_undo()
                    cv2.line(canvas, prev_points[hand_idx], palm,
                             (0, 0, 0), er_radius * 2)
                    prev_points[hand_idx] = palm
                    # görsel imleç: el hizasında büyük daire
                    cv2.circle(frame, palm, er_radius, (220, 220, 220), 2)
                    cv2.circle(frame, palm, er_radius - 6, (90, 90, 90), 1)
                else:
                    prev_points[hand_idx] = None

            # Sadece işaret parmağı -> normal çizim (sadece SERBEST modda)
            elif (shape_mode == 0 and fingers[1] == 1 and fingers[2] == 0):
                pending_shape_per_hand[hand_idx] = None
                if index_tip[1] > HEADER_HEIGHT:
                    if prev_points[hand_idx] is None:
                        prev_points[hand_idx] = index_tip
                        push_undo()
                    cv2.line(canvas, prev_points[hand_idx], index_tip,
                             draw_color, active_thickness)
                    prev_points[hand_idx] = index_tip
                    cv2.circle(frame, index_tip, active_thickness // 2 + 2,
                               draw_color, 2)
                else:
                    prev_points[hand_idx] = None
            else:
                prev_points[hand_idx] = None
                pending_shape_per_hand[hand_idx] = None

        # kaybolan eller için prev_point sıfırla
        for hid in list(prev_points.keys()):
            if hid not in active_hands:
                prev_points[hid] = None
                pending_shape_per_hand[hid] = None

        # canvas'ı ana kareyle birleştir (silginin siyahı canvas'ta "yok" demek olacağı için
        # canvas'ta her koyu piksel geçirilmez; silgi için özel maske lazım)
        # Basit yol: canvas siyahsa gösterme, değilse göster.
        # Silginin siyah çizgilerinin üstünü canvas'tan "silmek" için silgi modunda
        # canvas üstüne siyah (0,0,0) basıyoruz; bunlar görünmez olacak zaten.
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY_INV)
        inv_mask = cv2.cvtColor(inv_mask, cv2.COLOR_GRAY2BGR)
        frame = cv2.bitwise_and(frame, inv_mask)
        frame = cv2.bitwise_or(frame, canvas)

        # header
        frame = draw_header(frame, selected_idx, active_thickness)

        # FPS (metalik)
        cur_time = time.time()
        fps = 1 / (cur_time - prev_time) if prev_time else 0
        prev_time = cur_time
        metallic_text(frame, f"FPS {int(fps)}", (15, HEADER_HEIGHT + 35),
                      scale=0.7, thickness=2)

        # aktif mod göstergesi (FPS yanında)
        mode_text = f"MOD: {SHAPE_NAMES[shape_mode]}"
        if is_eraser:
            mode_text = "MOD: SILGI"
        metallic_text(frame, mode_text, (180, HEADER_HEIGHT + 35),
                      scale=0.7, thickness=2,
                      base=(0, 255, 255), highlight=(255, 255, 255))

        # şekil modunda SPACE hatırlatması
        if shape_mode != 0:
            metallic_text(frame,
                          "BAsPARMAK + ISARET = KOSE  |  SPACE = ONAYLA",
                          (15, h - 70), scale=0.55, thickness=1,
                          base=(0, 255, 200))

        # alt bilgi
        metallic_text(frame,
                      "1 PARMAK = CIZ  |  2 PARMAK (HEADER) = RENK SEC",
                      (15, h - 45), scale=0.55, thickness=1)
        metallic_text(frame,
                      "0=SERBEST 1=CIZGI 2=DAIRE 3=DIKDORTGEN 4=UCGEN | S Z C +/- Q",
                      (15, h - 18), scale=0.55, thickness=1)

        # toast
        if toast_msg and time.time() - toast_time < 1.5:
            (tw, th), _ = cv2.getTextSize(toast_msg, cv2.FONT_HERSHEY_DUPLEX, 1.2, 3)
            tx = (w - tw) // 2
            ty = h // 2
            # arka yarı şeffaf bant
            overlay = frame.copy()
            cv2.rectangle(overlay, (tx - 30, ty - th - 20),
                          (tx + tw + 30, ty + 20), (0, 0, 0), cv2.FILLED)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            metallic_text(frame, toast_msg, (tx, ty), scale=1.2, thickness=3,
                          base=(0, 255, 255), highlight=(255, 255, 255),
                          outline=(0, 80, 80), shadow=(0, 0, 0))

        cv2.imshow("El Takibi ile Cizim", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            path = save_canvas(canvas)
            toast_msg = f"KAYDEDILDI"
            toast_time = time.time()
            print(f"Kaydedildi: {path}")
        elif key == ord('z'):
            if undo_stack:
                canvas = undo_stack.pop()
                toast_msg = "GERI ALINDI"
                toast_time = time.time()
        elif key == ord('c'):
            push_undo()
            canvas = np.zeros_like(frame)
            toast_msg = "TEMIZLENDI"
            toast_time = time.time()
        elif key in (ord('+'), ord('=')):
            thickness = min(60, thickness + 2)
        elif key == ord('-'):
            thickness = max(2, thickness - 2)
        elif key in (ord('0'), ord('1'), ord('2'), ord('3'), ord('4')):
            shape_mode = key - ord('0')
            toast_msg = f"MOD: {SHAPE_NAMES[shape_mode]}"
            toast_time = time.time()
        elif key == ord(' '):
            if shape_mode != 0:
                committed = False
                for hid, ps in pending_shape_per_hand.items():
                    if ps is None:
                        continue
                    if not committed:
                        push_undo()
                        committed = True
                    p1, p2 = ps
                    draw_shape(canvas, shape_mode, p1, p2, draw_color, thickness)
                    pending_shape_per_hand[hid] = None
                if committed:
                    toast_msg = f"{SHAPE_NAMES[shape_mode]} EKLENDI"
                    toast_time = time.time()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
