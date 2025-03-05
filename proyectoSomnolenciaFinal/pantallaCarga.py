import tkinter as tk
import time
from main_interface import MainInterface


def show_loading_screen(usuario_nombre):
    # Crear la única instancia de Tk para la aplicación
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal mientras se muestra la pantalla de carga

    # Crear la pantalla de carga como una ventana secundaria (Toplevel)
    loading_window = tk.Toplevel(root)
    loading_window.title("Cargando...")

    # Dimensiones y posición de la ventana de carga
    window_width, window_height = 800, 500
    screen_width = loading_window.winfo_screenwidth()
    screen_height = loading_window.winfo_screenheight()
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2
    loading_window.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
    loading_window.resizable(False, False)
    loading_window.configure(bg="#1a1a2e")  # Azul oscuro elegante

    # Título llamativo
    title_label = tk.Label(
        loading_window,
        text="Sistema de Monitoreo de Somnolencia",
        font=("Arial", 22, "bold"),
        fg="#f9a826",  # Amarillo vibrante
        bg="#1a1a2e",
    )
    title_label.pack(pady=20)

    # Frase motivadora
    quote_text = (
        "“Cuando tienes insomnio, nunca estás realmente dormido y nunca estás realmente despierto.”\n"
        "— Chuck Palahniuk."
    )
    quote_label = tk.Label(
        loading_window,
        text=quote_text,
        font=("Helvetica", 14, "italic"),
        fg="#ffffff",
        bg="#1a1a2e",
        wraplength=window_width * 0.8,
        justify="center",
    )
    quote_label.pack(pady=10)

    # Barra de progreso
    progress_frame = tk.Frame(loading_window, bg="#1a1a2e")
    progress_frame.pack(pady=20)

    progress_canvas = tk.Canvas(progress_frame, width=600, height=40, bg="#16213e", bd=0, highlightthickness=0)
    progress_canvas.pack()

    progress_bar = progress_canvas.create_rectangle(0, 0, 10, 40, fill="#f9a826", outline="")

    def update_progress():
        # Simula una carga progresiva
        for i in range(1, 101):
            progress_canvas.coords(progress_bar, 0, 0, i * 6, 40)
            progress_canvas.update()
            time.sleep(0.05)
        close_loading_window()

    def close_loading_window():
        loading_window.destroy()
        root.deiconify()
        # Pasar el nombre del usuario a MainInterface
        main_app = MainInterface(root, usuario_nombre)
        main_app.run()

    # Inicia la animación de la barra de carga después de 500ms
    loading_window.after(500, update_progress)
    loading_window.mainloop()

if __name__ == "__main__":
    show_loading_screen()
