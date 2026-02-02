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

# 🔎 Palabras clave para Santiago (macheo flexible)
PRODUCTOS_MAP = {
    "natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def enviar_a_supabase(texto_completo):
    # El robot va a intentar encontrar el precio y el nombre en todo el bloque de texto
    try:
        lineas = texto_completo.split('\n')
        nombre_encontrado = "Desconocido"
        precio_final = 0
        ean_detectado = None

        for linea in lineas:
            linea_min = linea.lower()
            # 1. Buscamos el EAN por palabra clave
            for clave, ean in PRODUCTOS_MAP.items():
                if clave in linea_min:
                    ean_detectado = ean
                    nombre_encontrado = linea
            
            # 2. Buscamos el precio
            if "$" in linea:
                solo_num = "".join(filter(str.isdigit, linea))
                if solo_num: precio_final = int(solo_num)

        if ean_detectado and precio_final > 0:
            payload = {"ean": ean_detectado, "id_sucursal": "ch-bel", "valor": precio_final}
            url = f"{SUPABASE_URL}/rest/v1/precios_sgo"
            r = httpx.post(url, headers=HEADERS, json=payload)
            print(f"✅ ¡ENCONTRADO Y SUBIDO! -> {nombre_encontrado} | ${precio_final}")
        else:
            # Esto es lo que nos va a decir qué está fallando
            print(f"❓ Vi esto pero no lo subí: {nombre_encontrado} | Precio: {precio_final}")

    except Exception as e:
        print(f"❌ Error interno: {e}")

# --- INICIO ---
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("🚀 Entrando a MasOnline...")
    driver.get("https://www.masonline.com.ar/almacen")
    time.sleep(15) # Le damos tiempo de sobra para cargar
    
    # Bajamos un poco para que aparezcan los productos
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(5)

    items = driver.find_elements(By.CSS_SELECTOR, "[class*='vtex-product-summary']")
    print(f"📊 El robot detectó {len(items)} cuadritos de productos.")

    for item in items:
        enviar_a_supabase(item.text)

finally:
    driver.quit()
    print("🏁 Fin del reporte.")
