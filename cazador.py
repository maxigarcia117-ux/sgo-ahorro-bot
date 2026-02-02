import os
import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 🔐 Configuración
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

PRODUCTOS_MAP = {"natura": "7790272000840", "playadito": "7790310000351", "blancaflor": "7790580402412"}

def enviar_a_supabase(nombre, precio):
    try:
        precio_int = int("".join(filter(str.isdigit, precio)))
        ean = next((v for k, v in PRODUCTOS_MAP.items() if k in nombre.lower()), None)
        if ean and precio_int > 0:
            httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json={"ean": ean, "id_sucursal": "ch-bel", "valor": precio_int})
            print(f"✅ ¡LOGRADO! {nombre}: ${precio_int}")
    except: pass

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080") # Ventana grande
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("🚀 Entrando a la góndola...")
    driver.get("https://www.masonline.com.ar/almacen/aceites-y-vinagres/aceites")
    
    # ⏬ Scroll progresivo para cargar productos
    for i in range(5):
        driver.execute_script(f"window.scrollTo(0, {i * 400});")
        time.sleep(3)

    # Esperamos que aparezca al menos un cuadro de producto
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "vtex-product-summary-2-x-container")))
    except:
        print("⚠️ Tiempo de espera agotado, intentando leer lo que haya...")

    cuadritos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary-2-x-container']")
    print(f"📊 Analizando {len(cuadritos)} productos encontrados...")

    for c in cuadritos:
        texto = c.text
        if texto and "$" in texto:
            lineas = texto.split('\n')
            enviar_a_supabase(lineas[0], next((l for l in lineas if "$" in l), "0"))

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
