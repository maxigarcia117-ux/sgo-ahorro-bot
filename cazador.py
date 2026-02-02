import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# --- CONFIGURACIÓN DE TU APP (SgoAhorro) ---
# Estos datos los sacás de tu configuración de Supabase
SUPABASE_URL = "https://cuedfwadmfooxyvafory.supabase.co"
SUPABASE_KEY = "TU_KEY_ANON_AQUÍ" # Pegá la misma que usás en CodePen
TABLA_NOMBRE = "precios_sgo" # Asegurate que sea el nombre de tu tabla en Supabase

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

def enviar_a_supabase(nombre, precio_texto):
    try:
        # Convertimos "$ 2.500,50" en un número entero simple 2500
        solo_numeros = "".join(filter(str.isdigit, precio_texto))
        precio_final = int(solo_numeros) if solo_numeros else 0
        
        # Este objeto debe coincidir con las columnas de tu tabla en Supabase
        payload = {
            "nombre": nombre,
            "precio": precio_final,
            "sucursal": "ChangoMas_Sgo",
            "fecha": "now()"
        }
        
        with httpx.Client() as client:
            r = client.post(f"{SUPABASE_URL}/rest/v1/{TABLA_NOMBRE}", headers=HEADERS, json=payload)
            if r.status_code == 201:
                print(f"💾 Guardado en DB: {nombre} -> ${precio_final}")
            else:
                print(f"⚠️ Error al subir: {r.text}")
    except Exception as e:
        print(f"❌ Error procesando {nombre}: {e}")

# --- INICIO DEL ROBOT ---
print("🚀 SGO-AHORRO: Iniciando actualización automática...")

options = webdriver.ChromeOptions()
options.add_argument("--headless") # 🫥 MODO INVISIBLE
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    categorias = ["almacen", "bebidas", "limpieza"]
    for cat in categorias:
        print(f"📡 Escaneando categoría: {cat.upper()}...")
        driver.get(f"https://www.masonline.com.ar/{cat}")
        time.sleep(7) # Esperamos que la web cargue los datos
        
        # Scrolleamos para despertar a la web
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)

        productos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary']")
        for p in productos:
            try:
                lineas = p.text.split('\n')
                # Buscamos el nombre (línea 1 o 2) y el precio (la que tenga $)
                if len(lineas) > 2 and "$" in p.text:
                    nombre = lineas[1]
                    precio = next((l for l in lineas if "$" in l), "0")
                    enviar_a_supabase(nombre, precio)
            except:
                continue

finally:
    print("\n✅ ¡Proceso terminado! Revisá tu panel de Supabase.")
    driver.quit()