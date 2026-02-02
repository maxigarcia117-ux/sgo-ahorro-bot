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

# Mapeo de EANs (Palabras clave)
PRODUCTOS_MAP = {"natura": "7790272000840", "playadito": "7790310000351", "blancaflor": "7790580402412"}

def enviar_a_supabase(nombre, precio):
    try:
        solo_num = "".join(filter(str.isdigit, precio))
        precio_int = int(solo_num)
        # Buscamos la palabra clave en el nombre que encontremos
        ean = next((v for k, v in PRODUCTOS_MAP.items() if k in nombre.lower()), None)
        
        if ean and precio_int > 0:
            payload = {"ean": ean, "id_sucursal": "ch-bel", "valor": precio_int}
            httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json=payload)
            print(f"✅ ¡LOGRADO! {nombre}: ${precio_int}")
        else:
            print(f"🔎 Ignorado: {nombre[:20]}... | ${precio_int}")
    except: pass

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 📍 Forzamos Santiago
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {"latitude": -27.7833, "longitude": -64.2667, "accuracy": 100})
    
    url = "https://www.masonline.com.ar/almacen/aceites-y-vinagres/aceites"
    print(f"🚀 Intentando capturar nombres y precios en: {url}")
    driver.get(url)
    
    time.sleep(20) # Tiempo para que cargue todo
    
    # Buscamos el CONTENEDOR completo de cada producto
    cuadritos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary-2-x-container']")
    
    print(f"📊 Analizando {len(cuadritos)} productos encontrados...")

    for c in cuadritos:
        try:
            # Sacamos todo el texto del cuadrito y lo procesamos
            texto_completo = c.text
            lineas = texto_completo.split('\n')
            
            # El nombre suele estar en las primeras líneas, el precio tiene el $
            nombre_detectado = lineas[0] if len(lineas) > 0 else "Sin nombre"
            precio_detectado = next((l for l in lineas if "$" in l), "0")
            
            enviar_a_supabase(nombre_detectado, precio_detectado)
        except:
            continue

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
