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

# 🎭 Headers para engañar a MasOnline (User-Agent real)
MAS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

PRODUCTOS_BUSQUEDA = {
    "aceite natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def actualizar_precio(ean, precio, nombre):
    try:
        # En Supabase, el ID de sucursal es "ch-bel" para ChangoMás Belgrano
        payload = {"ean": ean, "id_sucursal": "ch-bel", "valor": int(precio)}
        url = f"{SUPABASE_URL}/rest/v1/precios_sgo"
        r = httpx.post(url, headers=SUPA_HEADERS, json=payload)
        if r.status_code in [201, 200, 204]:
            print(f"✅ SGOAHORRO: {nombre} actualizado a ${precio}")
        else:
            print(f"⚠️ Supabase respondió: {r.status_code}")
    except Exception as e:
        print(f"❌ Error Supabase: {e}")

def buscar_en_masonline():
    print("📡 Conectando con la API de MasOnline (Modo Invisible)...")
    
    with httpx.Client(headers=MAS_HEADERS, timeout=30.0, follow_redirects=True) as client:
        for nombre_busqueda, ean in PRODUCTOS_BUSQUEDA.items():
            try:
                # El sc=13 es clave para los precios de Santiago/interior
                api_url = f"https://www.masonline.com.ar/api/catalog_system/pub/products/search/{nombre_busqueda}?sc=13"
                
                response = client.get(api_url)
                
                # Verificamos si la respuesta es una lista (que es lo que esperamos)
                if response.status_code == 200:
                    datos = response.json()
                    
                    if isinstance(datos, list) and len(datos) > 0:
                        producto = datos[0]
                        nombre_real = producto.get('productName', nombre_busqueda)
                        # Buscamos el precio en la profundidad del JSON de VTEX
                        try:
                            precio = producto['items'][0]['sellers'][0]['commertialOffer']['Price']
                            if precio > 0:
                                actualizar_precio(ean, precio, nombre_real)
                        except (KeyError, IndexError):
                            print(f"⚠️ No pude encontrar el precio en los datos de: {nombre_busqueda}")
                    else:
                        print(f"⚠️ Producto no encontrado en catálogo: {nombre_busqueda}")
                else:
                    print(f"❌ MasOnline denegó el acceso (Status {response.status_code})")
                    
            except Exception as e:
                print(f"❌ Error técnico con {nombre_busqueda}: {e}")

if __name__ == "__main__":
    buscar_en_masonline()
    print("🏁 Proceso terminado.")
