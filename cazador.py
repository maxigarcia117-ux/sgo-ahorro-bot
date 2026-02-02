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

PRODUCTOS_MAP = {
    "natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def enviar_a_supabase(texto_cuadro):
    try:
        # Separamos el texto por líneas
        lineas = [l.strip() for l in texto_cuadro.split('\n') if l.strip()]
        if not lineas: return

        # El nombre suele ser la primera o segunda línea
        nombre_web = lineas[0]
        # El precio es cualquier línea que tenga el "$"
        precio_texto = next((l for l in lineas if "$" in l), "0")
        
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
            httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json=payload)
            print(f"✅ ¡SUBIDO! -> {nombre_web} | ${precio_final}")
        else:
            # ESTO ES LO QUE VEREMOS EN LOS LOGS PARA SABER QUÉ PASA
            print(f"👀 Vi esto: '{nombre_web}' | Precio detectado: ${precio_final}")

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
    
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(5)

    # Selector más general de cuadritos
    items = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary-2-x-container']")
    print(f"📊 Analizando {len(items)} cuadritos...")

    for item in items:
        enviar_a_supabase(item.text)

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
