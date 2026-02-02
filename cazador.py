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

PRODUCTOS_MAP = {"natura": "7790272000840", "playadito": "7790310000351", "blancaflor": "7790580402412"}

def enviar_a_supabase(texto_cuadro):
    try:
        texto_min = texto_cuadro.lower()
        ean_detectado = next((ean for clave, ean in PRODUCTOS_MAP.items() if clave in texto_min), None)
        if ean_detectado:
            precio_texto = next((l for l in texto_cuadro.split('\n') if "$" in l), "0")
            precio_final = int("".join(filter(str.isdigit, precio_texto)))
            if precio_final > 0:
                httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json={"ean": ean_detectado, "id_sucursal": "ch-bel", "valor": precio_final})
                print(f"✅ SANTIAGO: {ean_detectado} | ${precio_final}")
    except: pass

# --- INICIO ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# 🎭 Camuflaje: Hacemos que parezca un usuario real
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 📍 Geolocalización Santiago
    driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {"latitude": -27.7833, "longitude": -64.2667, "accuracy": 100})
    
    # Vamos a una sola URL para probar si carga
    url = "https://www.masonline.com.ar/almacen/aceites-y-vinagres/aceites"
    print(f"🚀 Intentando entrar a: {url}")
    driver.get(url)
    
    # Espera agresiva: le damos tiempo a los scripts de la web
    time.sleep(20) 
    
    # Bajamos poco a poco para que la web crea que estamos leyendo
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(2)

    # Buscamos por una clase más básica si la anterior falló
    items = driver.find_elements(By.CLASS_NAME, "vtex-product-summary-2-x-container")
    if not items:
        items = driver.find_elements(By.CSS_SELECTOR, "[class*='product-summary']")

    print(f"📊 Se encontraron {len(items)} productos.")
    for item in items:
        enviar_a_supabase(item.text)

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
