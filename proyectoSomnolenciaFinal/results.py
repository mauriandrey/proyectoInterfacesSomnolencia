import tkinter as tk
from tkinter import font
from sleep_test import get_resultados_test_cpt  # Importamos la función para obtener los resultados del test CPT
from activities import get_resultados_actividades  # Importamos la función para obtener los resultados de actividades
from registro import get_ci_usuario  # Importamos la función para obtener el CI del usuario
from registro import get_nombre_usuario  # Importamos la función para obtener el nombre del usuario
import psycopg2  # Importamos la librería psycopg2 para conectarnos a PostgreSQL
import datetime

class ResultsWindow:
    def __init__(self, master):
        self.top = tk.Toplevel(master)
        self.top.title("Resultados")
        self.top.attributes("-fullscreen", True)
        self.top.configure(bg="#e0f7fa")

        # Fuentes
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.label_font = font.Font(family="Arial", size=12)

        # Sección de resultados de actividades
        self.frame1 = tk.Frame(self.top, bg="#ffffff", padx=20, pady=10, relief="raised", bd=3)
        self.frame1.place(relx=0.05, rely=0.1, relwidth=0.4, relheight=0.35)

        tk.Label(self.frame1, text="Resultado Monitoreo de Actividades", font=self.title_font, bg="#ffffff", fg="#009688").pack(pady=5)

        self.tiempo_ojos_label = tk.Label(self.frame1, text="Tiempo de ojos cerrados: --", font=self.label_font, bg="#64b5f6")
        self.tiempo_ojos_label.pack(pady=5)
        self.parpadeos_label = tk.Label(self.frame1, text="Parpadeos detectados: --", font=self.label_font, bg="#64b5f6")
        self.parpadeos_label.pack(pady=5)
        self.porcentaje_label = tk.Label(self.frame1, text="Porcentaje de ojos cerrados: --", font=self.label_font, bg="#64b5f6")
        self.porcentaje_label.pack(pady=5)

        self.conclusion_actividades_label = tk.Label(self.frame1, text="Conclusión actividades: --", font=self.label_font, bg="#64b5f6")
        self.conclusion_actividades_label.pack(pady=5)

        # Sección de resultados del test CPT
        self.frame2 = tk.Frame(self.top, bg="#ffffff", padx=20, pady=10, relief="raised", bd=3)
        self.frame2.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.35)

        tk.Label(self.frame2, text="Resultado Test de CPT", font=self.title_font, bg="#ffffff", fg="#009688").pack(pady=5)

        self.omisiones_label = tk.Label(self.frame2, text="Total de omisiones: --", font=self.label_font, bg="#81c784")
        self.omisiones_label.pack(pady=5)
        self.comisiones_label = tk.Label(self.frame2, text="Total de comisiones: --", font=self.label_font, bg="#81c784")
        self.comisiones_label.pack(pady=5)
        self.promedio_label = tk.Label(self.frame2, text="Tiempo de reacción promedio: --", font=self.label_font, bg="#81c784")
        self.promedio_label.pack(pady=5)

        self.conclusion_test_label = tk.Label(self.frame2, text="Conclusión test: --", font=self.label_font, bg="#81c784")
        self.conclusion_test_label.pack(pady=5)

        # Conclusión final
        self.frame3 = tk.Frame(self.top, bg="#ffffff", padx=20, pady=10, relief="raised", bd=3)
        self.frame3.place(relx=0.1, rely=0.55, relwidth=0.8, relheight=0.1)

        self.conclusion_final_label = tk.Label(self.frame3, text="", font=self.title_font, bg="#ffeb3b")
        self.conclusion_final_label.pack(pady=10, fill="x")

        self.boton_cerrar = tk.Button(self.top, text="Cerrar", command=self.top.destroy, width=20, font=("Helvetica", 12), bg="white", fg="black", relief="solid", bd=2)
        self.boton_cerrar.place(relx=0.5, rely=0.9, anchor="center")

        self.conclusion_final_text = ""  # Variable para guardar la conclusión final

        self.actualizar_resultados()

    def actualizar_resultados(self):
        """Obtiene los resultados de las actividades y el test CPT y actualiza la interfaz."""
        actividades = get_resultados_actividades()
        test_cpt = get_resultados_test_cpt()

        # Si no hay datos aún, inicializar con valores por defecto
        if not test_cpt:
            test_cpt = {"omisiones": 0, "comisiones": 0, "tiempo_reaccion": 0.0}

        # Actualizar Actividades
        self.tiempo_ojos_label.config(text=f"Tiempo de ojos cerrados: {actividades.get('tiempo_ojos', '--')} s")
        self.parpadeos_label.config(text=f"Parpadeos detectados: {actividades.get('parpadeos', '--')}")
        self.porcentaje_label.config(text=f"Porcentaje de ojos cerrados: {actividades.get('porcentaje_ojos', '--')}%")

        # Evaluar somnolencia en actividades
        if actividades.get("porcentaje_ojos", 0) >= 80:
            self.conclusion_actividades_label.config(text="Se detecta somnolencia", bg="red", fg="white")
        else:
            self.conclusion_actividades_label.config(text="No se detecta somnolencia", bg="lightgreen")

        # Actualizar Test CPT con las variables correctas
        self.omisiones_label.config(text=f"Total de omisiones: {test_cpt.get('omisiones', 0)}")
        self.comisiones_label.config(text=f"Total de comisiones: {test_cpt.get('comisiones', 0)}")
        self.promedio_label.config(text=f"Tiempo de reacción promedio: {test_cpt.get('tiempo_reaccion', 0.0):.3f} segundos")

        # Evaluar falta de atención en el test CPT (Tiempo de reacción > 0.5 segundos)
        if test_cpt.get("tiempo_reaccion", 0.0) > 0.5:
            self.conclusion_test_label.config(text="Se detecta falta de atención", bg="red", fg="white")
        else:
            self.conclusion_test_label.config(text="No se detecta falta de atención", bg="lightgreen")

        self.actualizar_conclusion_final()

    def actualizar_conclusion_final(self):
        """Actualiza la conclusión final en base a los resultados"""
        actividades = get_resultados_actividades()
        test_cpt = get_resultados_test_cpt()

        # Si no hay datos aún, inicializar con valores por defecto
        if not test_cpt:
            test_cpt = {"omisiones": 0, "comisiones": 0, "tiempo_reaccion": 0.0}

        # Evaluar las conclusiones generales
        somnolencia_actividades = actividades.get("porcentaje_ojos", 0) >= 80
        falta_atencion_test = test_cpt.get("tiempo_reaccion", 0.0) > 0.5

        if somnolencia_actividades and falta_atencion_test:
            conclusion = "Usted sufre de falta de atención, probablemente a las consecuencias de la somnolencia"
            self.conclusion_final_label.config(text=conclusion, bg="orange", fg="black")
        elif somnolencia_actividades and not falta_atencion_test:
            conclusion = "Usted sufre de somnolencia, sin embargo los datos no detectan que esta condición afecte su atención"
            self.conclusion_final_label.config(text=conclusion, bg="yellow", fg="black")
        elif not somnolencia_actividades and falta_atencion_test:
            conclusion = "No hemos detectado somnolencia, sin embargo parece que su atención está centrada en otras actividades"
            self.conclusion_final_label.config(text=conclusion, bg="lightblue", fg="black")
        else:
            conclusion = "Usted se encuentra en buenas condiciones, pues no sufre de somnolencia ni de sus consecuencias"
            self.conclusion_final_label.config(text=conclusion, bg="lightgreen", fg="black")

        # Guardamos la conclusión en la variable de la clase
        self.conclusion_final_text = conclusion
        print(f"Conclusión final guardada: {self.conclusion_final_text}")

        # Ahora llamamos a la función de guardar pasando los parámetros
        self.llamar_guardar_datos()

    def llamar_guardar_datos(self):
        """Llamamos a la función para guardar los datos en la base de datos."""
        actividades = get_resultados_actividades()
        test_cpt = get_resultados_test_cpt()

        # Datos que vamos a enviar como parámetros
        ci = get_ci_usuario()
        nombre = get_nombre_usuario()
        tiempo_total_ojos_cerrados = actividades.get('tiempo_ojos', 0.0)
        parpadeos_totales = actividades.get('parpadeos', 0)
        porcentaje_ojos_cerrados = actividades.get('porcentaje_ojos', 0.0)
        comisiones = test_cpt.get('comisiones', 0)
        omisiones = test_cpt.get('omisiones', 0)
        t_promedio = test_cpt.get('tiempo_reaccion', 0.0)
        conclusion = self.conclusion_final_text
        fecha = datetime.datetime.now().strftime('%Y-%m-%d')

        # Llamada a la función que guarda los datos
        self.guardar_en_base_de_datos(ci, nombre, tiempo_total_ojos_cerrados, parpadeos_totales,
                                      porcentaje_ojos_cerrados, comisiones, omisiones, t_promedio,
                                      conclusion, fecha)

    def guardar_en_base_de_datos(self, ci, nombre, tiempo_total_ojos_cerrados, parpadeos_totales, 
                                 porcentaje_ojos_cerrados, comisiones, omisiones, t_promedio, 
                                 conclusion, fecha):
        """Guarda los resultados en la base de datos PostgreSQL."""
        try:
            # Conexión a la base de datos PostgreSQL
            connection = psycopg2.connect(
                host="mainline.proxy.rlwy.net",  
                dbname="railway",  
                user="postgres",  
                password="yZKptOSfoKPZkqdJraujkIOTlFmuDCQP",  
                port=57794  
            )
            cursor = connection.cursor()

            # Preparamos el comando SQL para insertar datos
            insert_query = """
                INSERT INTO supertabla (
                    ci, nombre, tiempo_total_ojos_cerrados, parpadeos_totales, porcentaje_ojos_cerrados, 
                    comisiones, omisiones, t_promedio, conclusion, fecha
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """

            # Insertar los datos en la base de datos
            cursor.execute(insert_query, (
                ci, nombre, tiempo_total_ojos_cerrados, parpadeos_totales, porcentaje_ojos_cerrados, 
                comisiones, omisiones, t_promedio, conclusion, fecha
            ))

            # Confirmamos la operación
            connection.commit()
            print("Datos guardados correctamente en la base de datos.")

        except Exception as error:
            print(f"Error al guardar los resultados en la base de datos: {error}")

        finally:
            # Cerramos la conexión
            if connection:
                cursor.close()
                connection.close()
