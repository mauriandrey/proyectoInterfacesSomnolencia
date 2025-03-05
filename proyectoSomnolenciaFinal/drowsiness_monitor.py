import cv2
import numpy as np
import time

class DrowsinessMonitor:
    def __init__(self, ear_threshold=0.25):  #podemos ajustar el umbral de EAR a 0.20
        """
        Inicializa el monitor de somnolencia.
        
        :param ear_threshold: Valor umbral para considerar que el ojo está cerrado.
        """
        self.ear_threshold = ear_threshold
        self.total_frames = 0
        self.closed_frames = 0
        self.time_eye_closed = 0  # Tiempo total en el que los ojos están cerrados (en segundos)
        self.blinks = 0  # Contador de parpadeos
        self.last_eye_state = False  # Para detectar el parpadeo

    def euclidean_distance(self, p1, p2):
        """
        Calcula la distancia euclidiana entre dos puntos.
        :param p1: (x, y)
        :param p2: (x, y)
        :return: Distancia entre p1 y p2.
        """
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def calculate_ear(self, eye):
        """
        Calcula el Eye Aspect Ratio (EAR) para un ojo dado.
        
        Se asume que `eye` es una lista de 6 puntos en el siguiente orden:
        p1, p2, p3, p4, p5, p6  
        donde la fórmula es:
            EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        
        :param eye: Lista de 6 tuplas (x, y)
        :return: EAR (valor flotante)
        """
        p1, p2, p3, p4, p5, p6 = eye
        vertical1 = self.euclidean_distance(p2, p6)
        vertical2 = self.euclidean_distance(p3, p5)
        horizontal = self.euclidean_distance(p1, p4)
        ear = (vertical1 + vertical2) / (2.0 * horizontal)
        return ear

    def update(self, frame, face_landmarks, image_width, image_height):
        """
        Actualiza el análisis de somnolencia, calculando EAR y PERCLOS,
        y manteniendo estadísticas de parpadeos y tiempo de ojos cerrados.
        
        :param frame: Imagen actual (BGR)
        :param face_landmarks: Objeto de landmarks obtenido de MediaPipe.
        :param image_width: Ancho de la imagen.
        :param image_height: Alto de la imagen.
        :return: frame modificado, valor EAR, valor PERCLOS (en %)
        """
        # Índices para cada ojo (según MediaPipe)
        left_eye_indices = [33, 160, 158, 133, 153, 144]
        right_eye_indices = [362, 385, 387, 263, 373, 380]

        left_eye = []
        right_eye = []

        # Extraer y dibujar puntos del ojo izquierdo
        for idx in left_eye_indices:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * image_width), int(lm.y * image_height)
            left_eye.append((x, y))
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Extraer y dibujar puntos del ojo derecho
        for idx in right_eye_indices:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * image_width), int(lm.y * image_height)
            right_eye.append((x, y))
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Calcular EAR para cada ojo y promediar
        ear_left = self.calculate_ear(left_eye)
        ear_right = self.calculate_ear(right_eye)
        ear = (ear_left + ear_right) / 2.0

        # Detectar si los ojos están cerrados
        is_eye_closed = ear < self.ear_threshold

        # Actualizar conteo de frames y frames con ojos cerrados (EAR por debajo del umbral)
        self.total_frames += 1
        if is_eye_closed:
            self.closed_frames += 1
            self.time_eye_closed += 1 / 30  # Asumiendo 30 FPS (se puede ajustar según la tasa de cuadros)
            if not self.last_eye_state:  # Detectar parpadeo (cambio de estado)
                self.blinks += 1
        self.last_eye_state = is_eye_closed

        # Calcular PERCLOS como el porcentaje de frames en que el ojo está cerrado
        perclos = (self.closed_frames / self.total_frames) * 100

        # Mostrar EAR y PERCLOS en el frame
        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"PERCLOS: {perclos:.2f}%", (30, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return frame, ear, perclos

    def get_results(self):
        """
        Devuelve los resultados finales: tiempo de ojos cerrados, tasa de parpadeos y porcentaje de ojos cerrados.
        """
        blink_rate = self.blinks  # Número de parpadeos, no en porcentaje
        perc_closed = (self.closed_frames / self.total_frames) * 100 if self.total_frames > 0 else 0
        return self.time_eye_closed, blink_rate, perc_closed
