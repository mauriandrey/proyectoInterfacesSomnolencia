import tkinter as tk
import time
import random
from threading import Thread
from tkinter import messagebox
import psycopg2
from tkinter import ttk
from registro import get_ci_usuario  # Importamos la función para recuperar el CI
from ayudas import HelpWindowTestSomnolencia
from PIL import Image, ImageTk

# 📌 Diccionario global para almacenar los resultados del test CPT
test_cpt_resultados = {
    "omisiones": 0,  # Cambiado de 'aciertos' a 'omisiones'
    "comisiones": 0,  # Cambiado de 'errores' a 'comisiones'
    "tiempo_reaccion": 0.0
}

def guardar_resultados_test_cpt(omisiones, comisiones, tiempo_reaccion):
    """📌 Guarda los resultados del test CPT en la variable global."""
    global test_cpt_resultados
    test_cpt_resultados["omisiones"] = omisiones
    test_cpt_resultados["comisiones"] = comisiones
    test_cpt_resultados["tiempo_reaccion"] = tiempo_reaccion

def get_resultados_test_cpt():
    """📌 Devuelve los resultados del test CPT."""
    return test_cpt_resultados

def obtener_conexion():
    """
    Establece una conexión a la base de datos PostgreSQL en Railway.
    """
    conn = psycopg2.connect(
        host="mainline.proxy.rlwy.net",  # Dirección del servidor de Railway
        dbname="railway",  # Nombre de la base de datos (verifícalo en el panel de Railway)
        user="postgres",  # Usuario predeterminado en Railway (o el que hayas creado)
        password="yZKptOSfoKPZkqdJraujkIOTlFmuDCQP",  # Contraseña proporcionada por Railway
        port=57794  # Puerto especificado por Railway
    )
    return conn

class CPTTestWindow:
    def __init__(self, master, callback):
        #self.master = master
        self.top = tk.Toplevel(master)
        self.callback = callback  # Guardamos la función de callback
        self.top.title("Continuous Performance Test (CPT)")
        self.top.attributes("-fullscreen", True)
        self.top.configure(bg="#1E1E1E")
        
        #self.top.after(1000, self.show_help)  # Mostrar la ayuda después de 1 segundo
        
        
        self.container = tk.Frame(self.top, bg="#1E1E1E", relief=tk.RAISED, borderwidth=3)
        self.container.pack(expand=True, padx=10, pady=10)
        
        self.label = tk.Label(self.container, text="Presiona la barra espaciadora cuando veas la letra 'X'", font=("Arial", 16), fg="white", bg="#1E1E1E")
        self.label.pack(pady=20)
        
        self.stimulus_label = tk.Label(self.container, text="", font=("Arial", 100, "bold"), fg="white", bg="#1E1E1E")
        self.stimulus_label.pack(pady=20)
        
        self.progress_frame = tk.Frame(self.container, bg="#1E1E1E", relief=tk.RIDGE, borderwidth=3)
        self.progress_frame.pack(pady=10)
        
        self.progress = ttk.Progressbar(self.progress_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=10)
        
        self.progress_label = tk.Label(self.progress_frame, text="0%", font=("Arial", 14), fg="white", bg="#1E1E1E")
        self.progress_label.pack(side=tk.LEFT)
        
        self.start_button = tk.Button(self.container, text="Iniciar Test", command=self.start_test, font=("Arial", 14, "bold"), bg="#28A745", fg="white", activebackground="white", activeforeground="black", padx=20, pady=10)
        self.start_button.pack(pady=20)
        
        self.back_button = tk.Button(self.container, text="Volver", command=self.close_window, font=("Arial", 14, "bold"), bg="#DC3545", fg="white", relief=tk.RAISED, borderwidth=3, padx=20, pady=10)
        self.back_button.pack(pady=20)
        
        self.end_button = tk.Button(self.container, text="Finalizar Test", command=self.close_window, font=("Arial", 14, "bold"), bg="#DC3545", fg="white", padx=20, pady=10)
        self.end_button.pack(pady=20)
        self.end_button.pack_forget()  # Ocultar el botón al inicio
        
        self.exit_button = tk.Button(self.container, text="Salir", command=self.exit_test, font=("Arial", 14, "bold"), bg="#FF5733", fg="white", padx=20, pady=10)
        self.exit_button.pack(pady=20)
        self.exit_button.pack_forget()  # Ocultar el botón al inicio
        
        self.ayuda_button = tk.Button(self.top, text="Ayuda", command=self.show_help, font=("Arial", 14, "bold"), bg="#3498db", fg="white", padx=20, pady=10)
        self.ayuda_button.place(relx=0.9, rely=0.9, anchor="center")
        
        self.top.bind("<space>", self.record_response)
        
        self.running = False
        self.responses = []
        self.omissions = 0
        self.commissions = 0
        self.response_received = False
        self.current_stimulus = ""
        self.stimulus_time = None
        


    def start_test(self):
        
        # Llamar al callback para bloquear el botón de test en MainInterface

        self.callback()
        
        self.start_button.pack_forget()  # Ocultar el botón al iniciar el test
        self.back_button.pack_forget()  # Ocultar el botón de volver
        self.running = True
        self.responses.clear()
        self.omissions = 0
        self.commissions = 0
        
        self.test_thread = Thread(target=self.run_test)
        self.test_thread.start()
    
    def run_test(self):
        start_time = time.time()
        duration = 90  # 3 minutos en segundos
        
        while time.time() - start_time < duration:
            elapsed_time = time.time() - start_time
            progress_percentage = (elapsed_time / duration) * 100
            self.progress["value"] = progress_percentage
            self.progress_label.config(text=f"{int(progress_percentage)}%")
            
            letter = random.choice(["X", "A", "B", "C", "D"])
            self.current_stimulus = letter
            self.response_received = False
            self.stimulus_time = time.time()
            self.stimulus_label.config(text=letter)
            
            time.sleep(random.uniform(1, 3))  # Intervalo variable entre estímulos
            
            # Verificar omisión: si el estímulo era objetivo y no se recibió respuesta
            if letter == "X" and not self.response_received:
                self.omissions += 1
        
        self.running = False
        self.stimulus_label.config(text="Fin del test")
        self.progress["value"] = 100
        self.progress_label.config(text="100%")
        self.show_results()
    
    def record_response(self, event):
        if not self.running:
            return
        if self.response_received:
            return
        
        # Si se responde:
        if self.current_stimulus == "X":
            reaction_time = time.time() - self.stimulus_time
            self.responses.append(reaction_time)
            self.response_received = True
        else:
            # Responder cuando el estímulo no es el objetivo: comisión
            self.commissions += 1
            self.response_received = True
    
    def show_results(self):
        avg_reaction_time = sum(self.responses) / len(self.responses) if self.responses else 0
        result_text = (f"Tiempo de reacción promedio: {avg_reaction_time:.3f} s\n"
                       f"Omisiones: {self.omissions}\n"
                       f"Comisiones: {self.commissions}")
        
        tk.Label(self.container, text=result_text, font=("Arial", 14), fg="white", bg="#1E1E1E").pack(pady=10)
        self.exit_button.pack(pady=20)  # Mostrar el botón de salir al finalizar el test
        
        

        
        # Obtener el CI del usuario verificado
        ci_usuario = get_ci_usuario()

        # Guardar en la base de datos
        guardar_resultados(ci_usuario, self.commissions, self.omissions, avg_reaction_time)
        
        
        # Guardar datos en la variable global
        guardar_resultados_test_cpt(self.omissions, self.commissions, avg_reaction_time)
  
    
    def exit_test(self):
        self.top.destroy()
    
    def close_window(self):
        self.top.destroy()
        

    def show_help(self):
        HelpWindowTestSomnolencia(self.top)

        
        
def guardar_resultados(ci, comisiones, omisiones, t_promedio):
    conn = obtener_conexion()
    cursor = conn.cursor()
    
    # Insertar los resultados en la tabla Rtest (siempre se insertan, sin importar si ya existen)
    cursor.execute('''
        INSERT INTO Rtest (CI, Comisiones, Omisiones, T_promedio)
        VALUES (%s, %s, %s, %s);
    ''', (ci, comisiones, omisiones, t_promedio))
    
    conn.commit()
    cursor.close()
    conn.close()

    # Mostrar ventana emergente con el mensaje (si lo deseas, puedes descomentar esta línea)
    # messagebox.showinfo("Guardado Exitoso", f"Resultados guardados para CI: {ci}")

def main():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    CPTTestWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
