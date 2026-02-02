import os
import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 🔐 Configuración de Supabase desde Secrets de GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Mapeo de EANs según tu base de datos actual
PRODUCTOS_MAP = {
    "Aceite Natura": "7790272000840",
    "Yerba Playadito": "7790310000351",
    "Harina Blancaflor": "7790580402412"
}

def enviar_a_supabase(nombre_web, precio_texto):
    try:
        solo_numeros = "".join(filter(str.isdigit, precio_texto))
        precio_final = int(solo_numeros) if solo_numeros else 0
        
        # Buscamos si el nombre de la web coincide con nuestro catálogo
        ean = next((ean for nombre, ean in PRODUCTOS_MAP.items() if nombre.lower() in nombre_web.lower()), None)
        
        if ean:
            payload = {
                "ean": ean,
                "id_sucursal": "ch-bel", # ChangoMás Belgrano
                "valor": precio_final
            }
            
            with httpx.Client() as client:
                url = f"{SUPABASE_URL}/rest/v1/precios_sgo"
                r = client.post(url, headers=HEADERS, json=payload)
                if r.status_code == 201:
                    print(f"✅ SGOAHORRO Actualizado: {nombre_web} -> ${precio_final}")
    except Exception as e:
        print(f"⚠️ Error: {e}")

# --- ROBOT INVISIBLE PARA GITHUB ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("📡 Iniciando rastreo en MasOnline Santiago...")
    driver.get("https://www.masonline.com.ar/almacen")
    time.sleep(10)
    
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(3)

    productos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary']")
    for p in productos:
        try:
            lineas = p.text.split('\n')
            if len(lineas) > 2 and "$" in p.text:
                enviar_a_supabase(lineas[1], lineas[2])
        except:
            continue
finally:
    driver.quit()
    print("🏁 Robot finalizó.")
