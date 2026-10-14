import time
import requests
from frontend.api_client import ensure_backend_alive, is_backend_healthy

print("[TEST] Calling ensure_backend_alive()...")
url = ensure_backend_alive()
print(f"[TEST] Returned URL: {url}")
healthy = is_backend_healthy(url)
print(f"[TEST] Is backend healthy? {healthy}")
if healthy:
    res = requests.get(f"{url}/api/documents")
    print(f"[TEST] Documents endpoint status: {res.status_code}, count: {len(res.json())}")
