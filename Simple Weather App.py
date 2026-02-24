import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from datetime import datetime
from collections import defaultdict
from datetime import datetime, timedelta
import threading
import json
import os
import sys
import time
import ctypes

# Función para mostrar mensaje de error de Windows
def error_windows(titulo, mensaje):
    ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x10)  # 0x10 = icono de error

def advertencia_windows(titulo, mensaje):
    ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x30)  # 0x30 = icono de advertencia

def info_windows(titulo, mensaje):
    ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x40)  # 0x40 = icono de información

API_KEY = "5c97b0aee92db0df591194a41bcc65ab"

opciones_archivo = "settings.json"
opciones = {
    "system": "imperial",
    "language": "en"
}

if os.path.exists(opciones_archivo):
    try:
        with open(opciones_archivo, "r", encoding="utf-8") as f:
            opciones.update(json.load(f))
    except:
        pass
else:
    error_windows("Error", "Unable to load the settings file.")
    sys.exit()

if os.path.exists("Assets"):
    pass
else:
    error_windows("Error", "Unable to load the app resources.")
    sys.exit()

ciudad = None
data_actual = None
data_pro = None
datos_cargados = False

traducciones = {
    "es": {
        "Actualizar": "Actualizar",
        "Opciones": "Opciones",
        "Cargando...": "Cargando...",
        "Ver pronóstico": "Ver pronóstico",
        "Volver": "Volver",
        "Ciudad": "Ciudad",
        "Humedad": "Humedad",
        "Viento": "Viento",
        "Próximas 24 horas:": "Próximas 24 horas:",
        "Próximos días:": "Próximos días:",
        "Sistema": "Sistema",
        "Idioma": "Idioma",
        "Métrico": "Métrico",
        "Imperial": "Imperial",
        "Español": "Español",
        "Inglés": "Inglés",
        "Opciones guardadas": "Opciones guardadas",
        "Cargando datos...": "Cargando datos...",
        "Temperatura": "Temperatura",
        "Descripción": "Descripción"
    },
    "en": {
        "Actualizar": "Update",
        "Opciones": "Options",
        "Cargando...": "Loading...",
        "Ver pronóstico": "View Forecast",
        "Volver": "Back",
        "Ciudad": "City",
        "Humedad": "Humidity",
        "Viento": "Wind",
        "Próximas 24 horas:": "Next 24 hours:",
        "Próximos días:": "Next days:",
        "Sistema": "System",
        "Idioma": "Language",
        "Métrico": "Metric",
        "Imperial": "Imperial",
        "Español": "Spanish",
        "Inglés": "English",
        "Opciones guardadas": "Options saved",
        "Cargando datos...": "Loading data...",
        "Temperatura": "Temperature",
        "Descripción": "Description"
    }
}

def t(texto):
    traducciones_climas = {
        "Tormenta eléctrica con lluvia ligera": "Thunderstorm with light rain",
        "Tormenta eléctrica con lluvia": "Thunderstorm with rain",
        "Tormenta eléctrica con lluvia intensa": "Thunderstorm with heavy rain",
        "Tormenta eléctrica ligera": "Light thunderstorm",
        "Tormenta eléctrica": "Thunderstorm",
        "Tormenta eléctrica intensa": "Heavy thunderstorm",
        "Tormenta eléctrica disgregada": "Ragged thunderstorm",
        "Tormenta eléctrica con llovizna ligera": "Thunderstorm with light drizzle",
        "Tormenta eléctrica con llovizna": "Thunderstorm with drizzle",
        "Tormenta eléctrica con llovizna intensa": "Thunderstorm with heavy drizzle",
        "Llovizna ligera": "Light drizzle",
        "Llovizna": "Drizzle",
        "Llovizna intensa": "Heavy drizzle",
        "Llovizna ligera con lluvia": "Light drizzle with rain",
        "Llovizna con lluvia": "Drizzle with rain",
        "Llovizna intensa con lluvia": "Heavy drizzle with rain",
        "Chubascos con llovizna": "Showers with drizzle",
        "Chubascos intensos con llovizna": "Heavy showers with drizzle",
        "Chubascos de llovizna": "Drizzle showers",
        "Lluvia ligera": "Light rain",
        "Lluvia moderada": "Moderate rain",
        "Lluvia intensa": "Heavy rain",
        "Lluvia muy intensa": "Very heavy rain",
        "Lluvia extrema": "Extreme rain",
        "Lluvia helada": "Freezing rain",
        "Aguacero ligero": "Light shower rain",
        "Aguacero": "Shower rain",
        "Aguacero intenso": "Heavy shower rain",
        "Chubascos irregulares": "Irregular showers",
        "Nieve ligera": "Light snow",
        "Nieve": "Snow",
        "Nieve pesada": "Heavy snow",
        "Aguanieve": "Sleet",
        "Aguanieve con chubascos ligeros": "Sleet with light showers",
        "Aguanieve con chubascos": "Sleet with showers",
        "Lluvia ligera con nieve": "Light rain with snow",
        "Lluvia con nieve": "Rain with snow",
        "Chubascos ligeros de nieve": "Light snow showers",
        "Chubascos de nieve": "Snow showers",
        "Chubascos intensos de nieve": "Heavy snow showers",
        "Neblina": "Mist",
        "Humo": "Smoke",
        "Calina / neblina seca": "Haze",
        "Remolinos de polvo / arena": "Dust/sand whirls",
        "Niebla": "Fog",
        "Arena": "Sand",
        "Polvo": "Dust",
        "Ceniza volcánica": "Volcanic ash",
        "Ráfagas": "Squalls",
        "Tornado": "Tornado",
        "Cielo despejado": "Clear sky",
        "Pocas nubes": "Few clouds",
        "Nubes dispersas": "Scattered clouds",
        "Nubes rotas": "Broken clouds",
        "Nubes cubiertas": "Overcast clouds"
    }
    if opciones["language"]=="en" and texto in traducciones_climas:
        return traducciones_climas[texto]
    return traducciones[opciones["language"]].get(texto, texto)

def cargar_datos_iniciales():
    """Carga los datos del clima en un hilo separado"""
    global ciudad, data_actual, data_pro, datos_cargados
    
    try:
        print("Obteniendo ciudad...")
        resp_loc = requests.get("http://ip-api.com/json/", timeout=10)
        data_loc = resp_loc.json()
        ciudad = data_loc.get("city", "Los Angeles")
        print("\033[92mCiudad obtenida!\033[0m")
    except:
        error_windows("Error", "Unable to get your location. Please check your internet connection and try again.")
        ventana.destroy()
        sys.exit()
    try:
        print("Obteniendo datos del clima...")
        url_actual = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
        data_actual = requests.get(url_actual, timeout=10).json()
        print("\033[92mDatos del clima obtenidos!\033[0m")
    except:
        error_windows("Error", "Unable to get weather data. Please check your internet connection and try again.")
        ventana.destroy()
        sys.exit()
    try:
        print("Obteniendo datos del pronóstico...")
        url_pro = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
        data_pro = requests.get(url_pro, timeout=10).json()
        print("\033[92mDatos del pronóstico obtenidos!\033[0m")
    except:
        error_windows("Error", "Unable to get weather data. Please check your internet connection and try again.")
        ventana.destroy()
        sys.exit()
    
    datos_cargados = True
    ventana.after(0, mostrar_clima_actual)

def solicitarclima():
    global ciudad, data_actual, data_pro, datos_cargados
    try:
        print("Obteniendo datos del clima...")
        url_actual = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
        data_actual = requests.get(url_actual, timeout=10).json()
        print("\033[92mDatos del clima obtenidos!\033[0m")
    except:
        error_windows("Error", "Unable to get weather data. Please check your internet connection and try again.")
        ventana.destroy()
        sys.exit()
    try:
        print("Obteniendo datos del pronóstico...")
        url_pro = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid={API_KEY}&units=metric&lang=es"
        data_pro = requests.get(url_pro, timeout=10).json()
        print("\033[92mDatos del pronóstico obtenidos!\033[0m")
    except:
        error_windows("Error", "Unable to get weather data. Please check your internet connection and try again.")
        ventana.destroy()
        sys.exit()

climas = {
    200: "Tormenta eléctrica con lluvia ligera",
    201: "Tormenta eléctrica con lluvia",
    202: "Tormenta eléctrica con lluvia intensa",
    210: "Tormenta eléctrica ligera",
    211: "Tormenta eléctrica",
    212: "Tormenta eléctrica intensa",
    221: "Tormenta eléctrica disgregada",
    230: "Tormenta eléctrica con llovizna ligera",
    231: "Tormenta eléctrica con llovizna",
    232: "Tormenta eléctrica con llovizna intensa",
    300: "Llovizna ligera",
    301: "Llovizna",
    302: "Llovizna intensa",
    310: "Llovizna ligera con lluvia",
    311: "Llovizna con lluvia",
    312: "Llovizna intensa con lluvia",
    313: "Chubascos con llovizna",
    314: "Chubascos intensos con llovizna",
    321: "Chubascos de llovizna",
    500: "Lluvia ligera",
    501: "Lluvia moderada",
    502: "Lluvia intensa",
    503: "Lluvia muy intensa",
    504: "Lluvia extrema",
    511: "Lluvia helada",
    520: "Aguacero ligero",
    521: "Aguacero",
    522: "Aguacero intenso",
    531: "Chubascos irregulares",
    600: "Nieve ligera",
    601: "Nieve",
    602: "Nieve pesada",
    611: "Aguanieve",
    612: "Aguanieve con chubascos ligeros",
    613: "Aguanieve con chubascos",
    615: "Lluvia ligera con nieve",
    616: "Lluvia con nieve",
    620: "Chubascos ligeros de nieve",
    621: "Chubascos de nieve",
    622: "Chubascos intensos de nieve",
    701: "Neblina",
    711: "Humo",
    721: "Calina / neblina seca",
    731: "Remolinos de polvo / arena",
    741: "Niebla",
    751: "Arena",
    761: "Polvo",
    762: "Ceniza volcánica",
    771: "Ráfagas",
    781: "Tornado",
    800: "Cielo despejado",
    801: "Pocas nubes",
    802: "Nubes dispersas",
    803: "Nubes rotas",
    804: "Nubes cubiertas"
}

ventana = tk.Tk()
ventana.title("Simple Weather App")
ventana.geometry("640x480")
ventana.resizable(True, True)
ventana.iconbitmap('Assets/logo.ico')
ventana.minsize(640, 480)

imagenes_pil = {
    "soleado": Image.open(os.path.join("Assets/sunny.png")),
    "nublado": Image.open(os.path.join("Assets/cloudy.png")),
    "lluvia": Image.open(os.path.join("Assets/rain.png")),
    "tormenta": Image.open(os.path.join("Assets/storm.png"))
}

img_referencia = None

def redimensionarfondo(event, nombre_clima, label_objetivo):
    global img_referencia
    nuevoancho = event.width
    nuevoalto = event.height
    imagen_redimensionada = imagenes_pil[nombre_clima].resize((nuevoancho, nuevoalto))
    img_referencia = ImageTk.PhotoImage(imagen_redimensionada)
    label_objetivo.config(image=img_referencia)

frame_actual = tk.Frame(ventana)
frame_pronostico = tk.Frame(ventana)

ultimo_update = 0
cooldown_segundos = 1800

boton_actualizar = None
    
def mostrar_pantalla_cargando():
    for w in frame_actual.winfo_children():
        w.destroy()
    
    frame_actual.pack(fill="both", expand=True)
    
    fondo_label = tk.Label(frame_actual)
    fondo_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    fondo_label.bind("<Configure>", lambda e: redimensionarfondo(e, "soleado", fondo_label))

    cuadradoblanco = tk.Frame(frame_actual, bg="white", highlightbackground="gray30", highlightthickness=1.2)
    cuadradoblanco.place(relx=0, rely=0, width=250, relheight=160/480)
    cuadradoblanco.tkraise(aboveThis=None)
    
    # Textos de carga con posiciones relativas
    tk.Label(frame_actual, text=f"{t('Ciudad')}: {t('Cargando...')}", bg="white", font=("Arial", 18, "bold")).place(relx=10/640, rely=5/480)
    tk.Label(frame_actual, text=t("Cargando..."), bg="white", font=("Arial", 22, "bold")).place(relx=10/640, rely=35/480)
    tk.Label(frame_actual, text=t("Cargando..."), bg="white", font=("Arial", 16)).place(relx=10/640, rely=65/480)
    tk.Label(frame_actual, text=f"{t('Humedad')}: {t('Cargando...')}", bg="white", font=("Arial", 16)).place(relx=10/640, rely=95/480)
    tk.Label(frame_actual, text=f"{t('Viento')}: {t('Cargando...')}", bg="white", font=("Arial", 16)).place(relx=10/640, rely=125/480)
    
    tk.Button(frame_actual, text=t("Ver pronóstico"), bg="white", font=("Arial", 12), state="disabled").place(relx=510/640, rely=10/480)
    
    global boton_actualizar
    boton_actualizar = tk.Button(frame_actual, text=t("Cargando..."), bg="white", font=("Arial", 12), state="disabled")
    boton_actualizar.place(relx=540/640, rely=440/480)
    
    boton_opciones = tk.Button(frame_actual, text=t("Opciones"), bg="white", font=("Arial", 12), command=abrir_opciones)
    boton_opciones.place(relx=460/640, rely=440/480)

def actualizarclima():
    global ultimo_update
    if time.time() - ultimo_update < cooldown_segundos:
        restante = int((cooldown_segundos - (time.time() - ultimo_update)) / 60)
        msg = f"{restante} min antes de actualizar de nuevo" if opciones["language"]=="es" else f"Wait {restante} min before updating again"
        messagebox.showinfo(t("Cooldown"), msg)
        return
    ultimo_update = time.time()
    boton_actualizar.config(text=t("Cargando..."), state="disabled")
    def tarea():
        solicitarclima()
        ventana.after(0, mostrar_clima_actual)
        ventana.after(0, lambda: boton_actualizar.config(text=t("Actualizar"), state="normal"))
        print("Clima actualizado!")
    threading.Thread(target=tarea).start()

def mostrar_clima_actual():
    global boton_actualizar
    
    if not datos_cargados:
        mostrar_pantalla_cargando()
        return
    
    frame_pronostico.pack_forget()
    for w in frame_actual.winfo_children():
        w.destroy()

    frame_actual.pack(fill="both", expand=True)

    codigo = data_actual["weather"][0]["id"]
    temp = data_actual["main"]["temp"]
    humedad = data_actual["main"]["humidity"]
    viento = data_actual["wind"]["speed"]
    desc = t(climas.get(codigo, data_actual["weather"][0]["description"].capitalize()))

    if opciones["system"] == "imperial":
        temp = temp * 9/5 + 32
        viento = viento * 2.23694

    if codigo in [800, 801]:
        clima_key = "soleado"
    elif codigo in [802, 803, 804]:
        clima_key = "nublado"
    elif codigo // 100 == 2:
        clima_key = "tormenta"
    elif codigo // 100 == 5:
        clima_key = "lluvia"
    else:
        clima_key = "soleado"

    fondo_label = tk.Label(frame_actual)
    fondo_label.place(relx=0, rely=0, relwidth=1, relheight=1)
    fondo_label.bind('<Configure>', lambda e: redimensionarfondo(e, clima_key, fondo_label))

    unidad_temp = "°C" if opciones["system"]=="metric" else "°F"
    unidad_viento = "m/s" if opciones["system"]=="metric" else "mph"

    cuadradoblanco = tk.Frame(frame_actual, bg="white", highlightbackground="gray30", highlightthickness=1.2)
    cuadradoblanco.place(relx=0, rely=0, width=250, relheight=160/480)
    cuadradoblanco.tkraise(aboveThis=None)

    tk.Label(frame_actual, text=f"{t('Ciudad')}: {ciudad}", bg="white", font=("Arial", 18, "bold")).place(relx=10/640, rely=5/480)
    tk.Label(frame_actual, text=f"{temp:.1f} {unidad_temp}", bg="white", font=("Arial", 22, "bold")).place(relx=10/640, rely=35/480)
    tk.Label(frame_actual, text=f"{desc}", bg="white", font=("Arial", 16)).place(relx=10/640, rely=65/480)
    tk.Label(frame_actual, text=f"{t('Humedad')}: {humedad}%", bg="white", font=("Arial", 16)).place(relx=10/640, rely=95/480)
    tk.Label(frame_actual, text=f"{t('Viento')}: {viento:.1f} {unidad_viento}", bg="white", font=("Arial", 16)).place(relx=10/640, rely=125/480)
    
    tk.Button(frame_actual, text=t("Ver pronóstico"), bg="white", font=("Arial", 12), command=mostrar_pronostico).place(relx=510/640, rely=10/480)

    boton_actualizar = tk.Button(frame_actual, text=t("Actualizar"), bg="white", font=("Arial", 12), command=actualizarclima)
    boton_actualizar.place(relx=540/640, rely=440/480)

    boton_opciones = tk.Button(frame_actual, text=t("Opciones"), bg="white", font=("Arial", 12), command=abrir_opciones)
    boton_opciones.place(relx=460/640, rely=440/480)

def abrir_opciones():
    ventana_opc = tk.Toplevel(ventana)
    ventana_opc.title(t("Settings"))
    ventana_opc.geometry("300x150")
    ventana_opc.resizable(False, False)
    ventana_opc.iconbitmap("Assets/logo.ico")

    tk.Label(ventana_opc, text=t("Sistema"), font=("Arial", 12, "bold")).place(x=10, y=10)
    sistema_var = tk.StringVar(value=opciones["system"])
    tk.Radiobutton(ventana_opc, text=t("Métrico"), variable=sistema_var, value="metric").place(x=120, y=10)
    tk.Radiobutton(ventana_opc, text=t("Imperial"), variable=sistema_var, value="imperial").place(x=200, y=10)

    tk.Label(ventana_opc, text=t("Idioma"), font=("Arial", 12, "bold")).place(x=10, y=50)
    idioma_var = tk.StringVar(value=opciones["language"])
    tk.Radiobutton(ventana_opc, text=t("Español"), variable=idioma_var, value="es").place(x=120, y=50)
    tk.Radiobutton(ventana_opc, text=t("Inglés"), variable=idioma_var, value="en").place(x=200, y=50)

    def guardar():
        opciones["system"] = sistema_var.get()
        opciones["language"] = idioma_var.get()
        with open(opciones_archivo, "w", encoding="utf-8") as f:
            json.dump(opciones, f, ensure_ascii=False, indent=2)
        messagebox.showinfo(t("Opciones"), t("Opciones guardadas"))
        ventana_opc.destroy()
        mostrar_clima_actual()  

    tk.Button(ventana_opc, text="Guardar" if opciones["language"]=="es" else "Save", command=guardar).place(x=120, y=100)

def mostrar_pronostico():
    if not datos_cargados:
        return
        
    frame_actual.pack_forget()
    for w in frame_pronostico.winfo_children():
        w.destroy()

    frame_pronostico.pack(fill="both", expand=True)

    fondo = tk.Label(frame_pronostico)
    fondo.place(relx=0, rely=0, relwidth=1, relheight=1)
    fondo.bind('<Configure>', lambda e: redimensionarfondo(e, "nublado", fondo))

    tk.Button(frame_pronostico, text=t("Volver"), bg="white", font=("Arial", 12), command=mostrar_clima_actual).place(relx=550/640, rely=10/480)
    tk.Label(frame_pronostico, text=f"{t('Próximos días:')} {ciudad}", bg="white", highlightbackground="gray30", highlightthickness=0.7, font=("Arial", 18, "bold")).place(relx=10/640, rely=10/480)

    canvas = tk.Canvas(frame_pronostico, bg="white", highlightthickness=0)
    scroll_y = ttk.Scrollbar(frame_pronostico, orient="vertical", command=canvas.yview)
    contenedor = tk.Frame(canvas, bg="white")
    contenedor.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=contenedor, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    # Posiciones relativas para el canvas y scroll
    canvas.place(relx=10/640, rely=50/480, relwidth=600/640, relheight=400/480)
    scroll_y.place(relx=610/640, rely=50/480, relheight=400/480)

    cuadradoblanco = tk.Frame(frame_pronostico, bg="white", highlightbackground="gray30", highlightthickness=1.2)
    cuadradoblanco.place(relx=9.2/640, rely=49/480, relwidth=620/640, relheight=405/480)
    cuadradoblanco.tkraise(aboveThis=fondo)

    tk.Label(contenedor, text=t("Próximas 24 horas:"), bg="white", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
    for item in data_pro["list"][:8]:
        hora_utc = datetime.fromisoformat(item["dt_txt"]).strftime("%H:%M")
        hora_dt = datetime.strptime(hora_utc, "%H:%M")
        hora = hora_dt - timedelta(hours=3)
        temp = item["main"]["temp"]
        if opciones["system"]=="imperial":
            temp = temp*9/5 + 32
        desc = t(climas.get(item["weather"][0]["id"], item["weather"][0]["description"].capitalize()))
        unidad_temp = "°C" if opciones["system"]=="metric" else "°F"
        tk.Label(contenedor, text=f"{hora.strftime('%H:%M')}: {temp:.1f}{unidad_temp} - {desc}", bg="white", font=("Arial", 13)).pack(anchor="w", padx=20)

    dias = defaultdict(list)
    for item in data_pro["list"]:
        fecha = item["dt_txt"].split()[0]
        dias[fecha].append(item["main"]["temp"])

    tk.Label(contenedor, text="\n" + t("Próximos días:"), bg="white", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=5)
    for fecha, temps in list(dias.items())[:5]:
        dt_obj = datetime.fromisoformat(fecha)
        if opciones["language"]=="en" or opciones["system"]=="imperial":
            fecha_fmt = dt_obj.strftime("%m/%d") 
        else:
            fecha_fmt = dt_obj.strftime("%d/%m")  
        temp_min = min(temps)
        temp_max = max(temps)
        if opciones["system"]=="imperial":
            temp_min = temp_min*9/5 + 32
            temp_max = temp_max*9/5 + 32
        unidad_temp = "°C" if opciones["system"]=="metric" else "°F"
        textopronosticomaximo = "Máx" if opciones["language"]=="es" else "Max"
        textopronosticominimo = "Mín" if opciones["language"]=="es" else "Min"
        tk.Label(contenedor, text=f"{fecha_fmt}: {textopronosticominimo} {temp_min:.1f}{unidad_temp} / {textopronosticomaximo} {temp_max:.1f}{unidad_temp}", bg="white", font=("Arial", 13)).pack(anchor="w", padx=20)

# Mostrar pantalla de carga inmediatamente
mostrar_pantalla_cargando()

# Iniciar carga de datos en segundo plano
threading.Thread(target=cargar_datos_iniciales, daemon=True).start()

print("Interfaz iniciada!")
ventana.mainloop()