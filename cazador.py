import os
import time
import httpx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# 🔐 Conexión con los Secretos de GitHub
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Diccionario simple para asignar EANs (puedes ampliarlo luego)
PRODUCTOS_EAN = {
    "Aceite Natura 1.5L": "7790272000840",
    "Yerba Playadito 1kg": "7790310000351",
    "Harina Blancaflor 1kg": "7790580402412"
}

def enviar_a_supabase(nombre_web, precio_texto):
    try:
        # 1. Limpiar precio
        solo_numeros = "".join(filter(str.isdigit, precio_texto))
        precio_final = int(solo_numeros) if solo_numeros else 0
        
        # 2. Buscar EAN (si el nombre coincide con nuestra lista)
        # Si no está en la lista, usamos un EAN genérico o saltamos
        ean = next((v for k, v in PRODUCTOS_EAN.items() if k in nombre_web), None)
        
        if ean:
            payload = {
                "ean": ean,
                "id_sucursal": "ch-bel", # ChangoMás Belgrano según tu SQL
                "valor": precio_final
                # fecha_actualizacion se pone sola por el default de tu DB
            }
            
            with httpx.Client() as client:
                client.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=HEADERS, json=payload)
                print(f"✅ Actualizado: {nombre_web} -> ${precio_final}")
    except Exception as e:
        print(f"❌ Error: {e}")

# --- CONFIGURACIÓN CHROME INVISIBLE ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("📡 Iniciando rastreo en MasOnline...")
    driver.get("https://www.masonline.com.ar/almacen")
    time.sleep(10)
    
    driver.execute_script("window.scrollBy(0, 2000);")
    time.sleep(3)

    productos = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary']")
    for p in productos:
        lineas = p.text.split('\n')
        if len(lineas) > 2 and "$" in p.text:
            enviar_a_supabase(lineas[1], lineas[2])

finally:
    driver.quit()
    print("🏁 Robot terminó su turno.")
                continue

finally:
    print("\n✅ ¡Proceso terminado! Revisá tu panel de Supabase.")

    driver.quit()
