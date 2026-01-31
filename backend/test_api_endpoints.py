"""
Test all API endpoints to verify backend is working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, path, data=None):
    """Test an API endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            r = requests.get(url)
        else:
            r = requests.post(url, json=data or {})
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {path}")
        print(f"Status: {r.status_code}")
        
        if r.status_code == 200:
            try:
                response = r.json()
                print(f"Response: {json.dumps(response, indent=2)[:200]}...")
                return True
            except:
                print(f"Response: {r.text[:200]}")
                return True
        else:
            print(f"Error: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    print("="*60)
    print("Backend API Endpoint Tests")
    print("="*60)
    
    # Test root endpoint
    test_endpoint("GET", "/")
    
    # Test schema inspection
    success = test_endpoint("POST", "/schema/inspect", {"db_type": "mysql"})
    
    if success:
        print("\n" + "="*60)
        print("[SUCCESS] Backend API is working correctly!")
        print("="*60)
        print("\nIf frontend still can't fetch details, check:")
        print("1. Frontend is using correct API_BASE URL")
        print("2. Frontend is running and can reach backend")
        print("3. Browser console for CORS or network errors")
        print("4. Check browser DevTools > Network tab for failed requests")
    else:
        print("\n" + "="*60)
        print("[ERROR] Backend API has issues")
        print("="*60)

if __name__ == "__main__":
    main()
