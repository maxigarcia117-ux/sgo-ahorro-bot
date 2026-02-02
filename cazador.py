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

# Mapeo de EANs
PRODUCTOS_MAP = {"natura": "7790272000840", "playadito": "7790310000351", "blancaflor": "7790580402412"}

def enviar_a_supabase(nombre, precio):
    try:
        solo_num = "".join(filter(str.isdigit, precio))
        precio_int = int(solo_num)
        ean = next((v for k, v in PRODUCTOS_MAP.items() if k in nombre.lower()), None)
        
        if ean and precio_int > 0:
            httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json={"ean": ean, "id_sucursal": "ch-bel", "valor": precio_int})
            print(f"✅ ¡LOGRADO! {nombre}: ${precio_int}")
    except: pass

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # 🎯 Vamos a la versión "liviana" de la web que los bots suelen ver mejor
    url = "https://www.masonline.com.ar/almacen/aceites-y-vinagres/aceites?_q=aceites&map=ft"
    print(f"🚀 Intentando acceso profundo a: {url}")
    driver.get(url)
    
    # Esperamos a que el sistema de "Shield" de la web nos deje pasar
    time.sleep(25) 
    
    # Intentamos sacar los nombres y precios de una forma más rústica
    nombres = driver.find_elements(By.CSS_SELECTOR, "[class*='productBrandName']")
    precios = driver.find_elements(By.CSS_SELECTOR, "[class*='currencyContainer']")
    
    print(f"📊 Encontré {len(nombres)} nombres y {len(precios)} precios.")

    for n, p in zip(nombres, precios):
        enviar_a_supabase(n.text, p.text)

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
