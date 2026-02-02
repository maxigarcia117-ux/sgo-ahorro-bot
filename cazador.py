import os
import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 🔐 Configuración
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# 🔎 Mapeo Santiago
PRODUCTOS_MAP = {
    "natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def enviar_a_supabase(nombre_web, precio_texto):
    try:
        solo_num = "".join(filter(str.isdigit, precio_texto))
        precio_final = int(solo_num) if solo_num else 0
        
        nombre_min = nombre_web.lower()
        ean_detectado = None
        for clave, ean in PRODUCTOS_MAP.items():
            if clave in nombre_min:
                ean_detectado = ean
                break

        if ean_detectado and precio_final > 0:
            payload = {"ean": ean_detectado, "id_sucursal": "ch-bel", "valor": precio_final}
            r = httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json=payload)
            print(f"✅ ¡ACTUALIZADO! -> {nombre_web} | ${precio_final}")
        else:
            # Esto nos ayudará a ver qué nombres está leyendo realmente
            if precio_final > 0:
                print(f"🔎 Leí: '{nombre_web}' pero no está en mi lista de Santiago.")

    except Exception as e:
        print(f"❌ Error: {e}")

# --- INICIO ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("🚀 Entrando a MasOnline...")
    driver.get("https://www.masonline.com.ar/almacen")
    time.sleep(15)
    
    driver.execute_script("window.scrollBy(0, 2000);")
    time.sleep(5)

    # Buscamos los contenedores de productos
    items = driver.find_elements(By.CSS_SELECTOR, ".vtex-product-summary-2-x-container")
    print(f"📊 Analizando {len(items)} productos...")

    for item in items:
        try:
            # Intentamos sacar el nombre y el precio por separado para que no sea 'Desconocido'
            nombre = item.find_element(By.CSS_SELECTOR, "[class*='productBrandName']").text
            precio = item.find_element(By.CSS_SELECTOR, "[class*='currencyContainer']").text
            enviar_a_supabase(nombre, precio)
        except:
            continue

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
