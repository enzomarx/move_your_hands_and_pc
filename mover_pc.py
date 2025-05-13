import cv2
import mediapipe as mp
import pyautogui
import pygetwindow as gw
import win32gui
import win32con
import time

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

janela_nome = "Controle por Gestos"

def dedos_levantados(hand_landmarks):
    dedos = []
    for tip_id in [4, 8, 12, 16, 20]:
        tip_y = hand_landmarks.landmark[tip_id].y
        pip_y = hand_landmarks.landmark[tip_id - 2].y
        dedos.append(tip_y < pip_y)
    return dedos

last_click_time = 0
click_cooldown = 1.0

cv2.namedWindow(janela_nome)
cv2.setWindowProperty(janela_nome, cv2.WND_PROP_TOPMOST, 1)

def restaurar_e_fixar_janela(nome):
    try:
        janela = gw.getWindowsWithTitle(nome)[0]
        hwnd = janela._hWnd

        if janela.isMinimized:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    except Exception as e:
        print(f"[ERRO] Não foi possível manter a janela ativa: {e}")

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            dedos = dedos_levantados(hand_landmarks)
            x = int(hand_landmarks.landmark[8].x * screen_w)
            y = int(hand_landmarks.landmark[8].y * screen_h)

            if dedos == [False, False, False, False, False]:  # mão fechada
                pyautogui.moveTo(x, y, duration=0.05)

            elif dedos == [True, True, False, False, False]:  # pistola
                if time.time() - last_click_time > click_cooldown:
                    pyautogui.click()
                    last_click_time = time.time()

            elif all(dedos):  # mão aberta
                pyautogui.scroll(-20)

    cv2.imshow(janela_nome, frame)
    restaurar_e_fixar_janela(janela_nome)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
