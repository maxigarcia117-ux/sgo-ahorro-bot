import os
import httpx

# 🔐 Configuración
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# AGREGÁ TU COOKIE ACÁ (o mejor, creá un Secret en GitHub llamado MASONLINE_COOKIE)
COOKIE_PERSONAL = os.environ.get("MASONLINE_COOKIE") 

PRODUCTOS = {
    "aceite natura": "7790272000840",
    "playadito": "7790310000351",
    "blancaflor": "7790580402412"
}

def enviar_supabase(ean, precio):
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    payload = {"ean": ean, "id_sucursal": "ch-bel", "valor": int(precio)}
    httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=headers, json=payload)

def cazar():
    headers_mas = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/121.0.0.0",
        "Cookie": COOKIE_PERSONAL # <--- Acá entra tu identidad de Santiago
    }
    
    print("🎯 Iniciando actualización definitiva de Santiago...")
    
    with httpx.Client(headers=headers_mas, timeout=30.0) as client:
        for nombre, ean in PRODUCTOS.items():
            try:
                # Buscamos por término de búsqueda (más estable)
                url = f"https://www.masonline.com.ar/api/catalog_system/pub/products/search/{nombre}"
                res = client.get(url)
                
                if res.status_code == 200:
                    data = res.json()[0]
                    precio = data['items'][0]['sellers'][0]['commertialOffer']['Price']
                    nombre_real = data['productName']
                    
                    enviar_supabase(ean, precio)
                    print(f"✅ {nombre_real}: ${precio} (Actualizado)")
                else:
                    print(f"❌ Error {res.status_code} en {nombre}")
            except Exception as e:
                print(f"⚠️ Falló {nombre}: {e}")

if __name__ == "__main__":
    cazar()
