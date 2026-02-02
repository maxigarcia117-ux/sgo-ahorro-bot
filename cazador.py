import os
import httpx

# 🔐 Configuración Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SUPA_HEADERS = {
    "apikey": SUPABASE_KEY, 
    "Authorization": f"Bearer {SUPABASE_KEY}", 
    "Content-Type": "application/json"
}

# 🔎 Qué buscamos y qué EAN tiene en tu base de datos
PRODUCTOS_BUSQUEDA = {
    "aceite natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def actualizar_precio(ean, precio, nombre):
    try:
        payload = {"ean": ean, "id_sucursal": "ch-bel", "valor": int(precio)}
        url = f"{SUPABASE_URL}/rest/v1/precios_sgo"
        r = httpx.post(url, headers=SUPA_HEADERS, json=payload)
        if r.status_code == 201:
            print(f"✅ SGOAHORRO: {nombre} actualizado a ${precio}")
    except Exception as e:
        print(f"❌ Error subiendo a Supabase: {e}")

def buscar_en_masonline():
    print("📡 Conectando con la central de datos de MasOnline...")
    
    # Usamos la API de búsqueda directa de MasOnline
    # El sc=13 es el código que suele usar ChangoMás para sucursales del interior
    for nombre_busqueda, ean in PRODUCTOS_BUSQUEDA.items():
        try:
            api_url = f"https://www.masonline.com.ar/api/catalog_system/pub/products/search/{nombre_busqueda}?sc=13"
            
            with httpx.Client(timeout=20.0) as client:
                response = client.get(api_url)
                datos = response.json()
                
                if datos:
                    # Agarramos el primer resultado
                    producto = datos[0]
                    nombre_real = producto['productName']
                    # Buscamos el precio en la estructura del JSON
                    precio = producto['items'][0]['sellers'][0]['commertialOffer']['Price']
                    
                    if precio > 0:
                        actualizar_precio(ean, precio, nombre_real)
                else:
                    print(f"⚠️ No se encontró el producto: {nombre_busqueda}")
        except Exception as e:
            print(f"❌ Error buscando {nombre_busqueda}: {e}")

if __name__ == "__main__":
    buscar_en_masonline()
    print("🏁 Proceso terminado.")
