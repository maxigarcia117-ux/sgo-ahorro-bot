import os
import httpx

# 🔐 Configuración
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
COOKIE_PERSONAL = os.environ.get("MASONLINE_COOKIE", "") 

PRODUCTOS = {
    "aceite natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def enviar_supabase(ean, precio, nombre):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    payload = {"ean": ean, "id_sucursal": "ch-bel", "valor": int(precio)}
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=headers, json=payload)
    if r.status_code in [200, 201, 204]:
        print(f"✅ {nombre}: ${precio} (Actualizado)")

def cazar():
    headers_mas = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
        "Cookie": COOKIE_PERSONAL,
        "Accept": "application/json"
    }
    
    print("🎯 Actualizando Santiago del Estero...")
    
    with httpx.Client(headers=headers_mas, timeout=30.0, follow_redirects=True) as client:
        for busqueda, ean in PRODUCTOS.items():
            try:
                # Usamos una URL un poco más específica para evitar el error 206
                url = f"https://www.masonline.com.ar/api/catalog_system/pub/products/search/{busqueda.replace(' ', '%20')}"
                res = client.get(url)
                
                # Aceptamos 200 y 206 (ambos tienen datos)
                if res.status_code in [200, 206]:
                    data = res.json()
                    if data and len(data) > 0:
                        prod = data[0]
                        precio = prod['items'][0]['sellers'][0]['commertialOffer']['Price']
                        nombre_real = prod['productName']
                        enviar_supabase(ean, precio, nombre_real)
                    else:
                        print(f"⚠️ No se encontró stock para: {busqueda}")
                else:
                    print(f"❌ Error {res.status_code} en {busqueda}")
            except Exception as e:
                print(f"⚠️ Falló {busqueda}: {e}")

if __name__ == "__main__":
    cazar()
