import os
import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 🔐 Configuración desde Secrets de GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Diccionario de EANs basado en tu captura de SQL
PRODUCTOS_MAP = {
    "Aceite Natura": "7790272000840",
    "Yerba Playadito": "7790310000351",
    "Harina Blancaflor": "7790580402412"
}

def enviar_a_supabase(nombre_web, precio_texto):
    try:
        # 1. Limpiamos el precio (quitamos $, puntos y comas)
        solo_numeros = "".join(filter(str.isdigit, precio_texto))
        precio_final = int(solo_numeros) if solo_numeros else 0
        
        # 2. Buscamos si el producto de la web coincide con nuestro catálogo
        ean = next((ean for nombre, ean in PRODUCTOS_MAP.items() if nombre.lower() in nombre_web.lower()), None)
        
        if ean:
            # 3. Formato exacto de tu tabla precios_sgo
            payload = {
                "ean": ean,
                "id_sucursal": "ch-bel", # ChangoMás Belgrano
                "valor": precio_final
            }
            
            url_final = f"{SUPABASE_URL}/rest/v1/precios_sgo"
            with httpx.Client() as client:
                response = client.post(url_final, headers=HEADERS, json=payload)
                if response.status_code == 201:
                    print(f"✅ SGOAHORRO Actualizado: {nombre_web} -> ${precio_final}")
                else:
                    print(f"❌ Error DB: {response.text}")
    except Exception as e:
        print(f"⚠️ Error procesando {nombre_web}: {e}")

# --- ROBOT INVISIBLE ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("📡 Buscando precios en MasOnline Santiago...")
    driver.get("https://www.masonline.com.ar/almacen")
    time.sleep(10) # Esperamos carga
    
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(3)

    productos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary']")
    for p in productos:
        lineas = p.text.split('\n')
        if len(lineas) > 2 and "$" in p.text:
            # lineas[1] suele ser el nombre, lineas[2] el precio
            enviar_a_supabase(lineas[1], lineas[2])

finally:
    driver.quit()
    print("🏁 Robot finalizó.")
finally:
    print("\n✅ ¡Proceso terminado! Revisá tu panel de Supabase.")

    driver.quit()

