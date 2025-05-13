import cv2
import mediapipe as mp
import numpy as np
import time

# Inicialização do MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Variáveis do jogo
ammo = 1
score = 0
last_shot_time = 0
cooldown = 1.0
projectiles = []

target_pos = (np.random.randint(100, 500), np.random.randint(100, 400))
target_radius = 30

# Função para detectar o gesto de arma
def is_gun_gesture(landmarks):
    dedo_indicador = landmarks.landmark[8]
    base_indicador = landmarks.landmark[6]

    dedo_medio = landmarks.landmark[12]
    base_medio = landmarks.landmark[10]

    dedo_anelar = landmarks.landmark[16]
    base_anelar = landmarks.landmark[14]

    dedo_mindinho = landmarks.landmark[20]
    base_mindinho = landmarks.landmark[18]

    polegar = landmarks.landmark[4]
    base_polegar = landmarks.landmark[2]

    indicador_levantado = dedo_indicador.y < base_indicador.y
    medio_abaixado = dedo_medio.y > base_medio.y
    anelar_abaixado = dedo_anelar.y > base_anelar.y
    mindinho_abaixado = dedo_mindinho.y > base_mindinho.y
    polegar_para_lado = abs(polegar.x - base_polegar.x) > 0.05

    return indicador_levantado and polegar_para_lado and medio_abaixado and anelar_abaixado and mindinho_abaixado

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            if is_gun_gesture(hand):
                finger = hand.landmark[8]
                x = int(finger.x * w)
                y = int(finger.y * h)

                if time.time() - last_shot_time > cooldown and ammo > 0:
                    projectile = {"x": x, "y": y, "vx": 10, "vy": 0}
                    projectiles.append(projectile)

                    ammo -= 1
                    last_shot_time = time.time()

        # Recarregar se a mão estiver aberta
        for hand in results.multi_hand_landmarks:
            fingers = []
            for tip_id in [4, 8, 12, 16, 20]:
                tip_y = hand.landmark[tip_id].y
                pip_y = hand.landmark[tip_id - 2].y
                fingers.append(tip_y < pip_y)
            if all(fingers):
                ammo = 1

    # Atualiza e desenha projéteis
    for projectile in projectiles[:]:
        projectile["x"] += projectile["vx"]
        projectile["y"] += projectile["vy"]

        # Desenhar a bala azul
        cv2.circle(frame, (int(projectile["x"]), int(projectile["y"])), 10, (255, 0, 0), -1)

        # Verificar colisão com o alvo
        dist = np.sqrt((projectile["x"] - target_pos[0]) ** 2 + (projectile["y"] - target_pos[1]) ** 2)
        if dist < target_radius:
            score += 1
            target_pos = (np.random.randint(100, 500), np.random.randint(100, 400))
            projectiles.remove(projectile)

        # Remover bala se sair da tela
        elif projectile["x"] > w or projectile["x"] < 0 or projectile["y"] > h or projectile["y"] < 0:
            projectiles.remove(projectile)

    # Desenhar o alvo
    cv2.circle(frame, target_pos, target_radius, (0, 0, 255), -1)

    # HUD
    cv2.putText(frame, f"Municao: {ammo}/1", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(frame, f"Pontuacao: {score}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Hand Gun Game", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
