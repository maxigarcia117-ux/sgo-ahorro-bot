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
    try:
        r = httpx.post(f"{SUPABASE_URL}/rest/v1/precios_sgo", headers=headers, json=payload)
        if r.status_code in [200, 201, 204]:
            print(f"✅ {nombre}: ${precio} (Actualizado)")
    except:
        print(f"❌ Error enviando a base de datos")

def cazar():
    # Usamos un User-Agent rotativo o fijo pero robusto
    headers_mas = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    
    # Si la cookie está presente, la usamos. Si no, el robot intenta entrar como invitado.
    if COOKIE_PERSONAL:
        headers_mas["Cookie"] = COOKIE_PERSONAL
    
    print("🤖 Robot Autónomo: Iniciando búsqueda...")
    
    with httpx.Client(headers=headers_mas, timeout=30.0, follow_redirects=True) as client:
        for busqueda, ean in PRODUCTOS.items():
            try:
                # API secundaria de VTEX que es más estable para bots
                url = f"https://www.masonline.com.ar/api/catalog_system/pub/products/search/{busqueda.replace(' ', '%20')}?sc=13"
                res = client.get(url)
                
                if res.status_code in [200, 206]:
                    data = res.json()
                    if data:
                        prod = data[0]
                        precio = prod['items'][0]['sellers'][0]['commertialOffer']['Price']
                        nombre_real = prod['productName']
                        enviar_supabase(ean, precio, nombre_real)
                    else:
                        print(f"⚠️ {busqueda} sin stock.")
                else:
                    # SI DA ERROR DE COOKIE (401/403), acá podrías disparar un aviso
                    print(f"❌ Error {res.status_code} en {busqueda}. (Posible cookie vencida)")
                    
            except Exception as e:
                print(f"⚠️ Error técnico: {e}")

if __name__ == "__main__":
    cazar()
