import os
import sys
import httpx

def check_health(url: str):
    target = url.rstrip("/") + "/api/v1/health"
    print(f"Pinging {target}...")
    try:
        res = httpx.get(target, timeout=10.0)
        if res.status_code == 200:
            print(f"[SUCCESS] Backend healthy: {res.json()}")
            return True
        else:
            print(f"[ERROR] HTTP {res.status_code}: {res.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection error: {e}")
        return False

if __name__ == "__main__":
    backend = sys.argv[1] if len(sys.argv) > 1 else "https://environmental-operation-system-h41o.onrender.com"
    success = check_health(backend)
    sys.exit(0 if success else 1)
