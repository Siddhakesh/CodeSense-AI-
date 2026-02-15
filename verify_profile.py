
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def test_profile():
    print(f"Testing profile endpoint at {BASE_URL}/api/profile/tiangolo...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/api/profile/tiangolo")
            
            if response.status_code == 200:
                data = response.json()
                print("[OK] Profile endpoint successful!")
                print("-" * 50)
                print(f"Name: {data.get('name')}")
                print(f"Username: {data.get('username')}")
                
                summary = data.get('summary')
                if summary:
                    print("[OK] Summary generated successfully:")
                    print(summary[:100] + "...")
                else:
                    print("[WARN] Summary field is empty or missing.")
                print("-" * 50)
                return True
            else:
                print(f"[FAIL] Failed: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_profile())
