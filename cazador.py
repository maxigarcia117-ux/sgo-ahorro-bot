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
        texto_min = texto_cuadro.lower()
        ean_detectado = None
        for clave, ean in PRODUCTOS_MAP.items():
            if clave in texto_min:
                ean_detectado = ean
                break

        if ean_detectado:
            lineas = texto_cuadro.split('\n')
            precio_texto = next((l for l in lineas if "$" in l), "0")
            solo_num = "".join(filter(str.isdigit, precio_texto))
            precio_final = int(solo_num) if solo_num else 0

            if precio_final > 0:
                payload = {"ean": ean_detectado, "id_sucursal": "ch-bel", "valor": precio_final}
                httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json=payload)
                print(f"✅ SANTIAGO DETECTADO -> {ean_detectado} | ${precio_final}")
    except Exception as e:
        print(f"❌ Error: {e}")

# --- INICIO ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
# Importante: permitir geolocalización
options.add_argument("--enable-features=NetworkServiceInProcess")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 📍 TRUCO MAESTRO: Forzamos las coordenadas de Santiago del Estero
    # Estas son coordenadas aproximadas cerca del ChangoMás de Belgrano
    params = {
        "latitude": -27.7833,
        "longitude": -64.2667,
        "accuracy": 100
    }
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", params)
    print("🌍 Coordenadas fijadas en Santiago del Estero.")

    urls = [
        "https://www.masonline.com.ar/almacen/aceites-y-vinagres/aceites",
        "https://www.masonline.com.ar/almacen/infusiones/yerba-mate"
    ]
    
    for url in urls:
        driver.get(url)
        time.sleep(15) # Damos tiempo a que la web lea la ubicación simulada
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)

        items = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary-2-x-container']")
        for item in items:
            enviar_a_supabase(item.text)

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
