import requests
import sys

BASE_URL = "http://localhost:8001"

def test_garbage_token():
    print("\n--- Test 1: Garbage Token ---")
    headers = {"Authorization": "Token garbage_value_123"}
    try:
        response = requests.post(f"{BASE_URL}/upload/", headers=headers)
        print(f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e: print(e)

def test_no_header():
    print("\n--- Test 2: No Header ---")
    try:
        response = requests.post(f"{BASE_URL}/upload/")
        print(f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e: print(e)

def test_bearer_garbage():
    print("\n--- Test 3: Bearer Garbage ---")
    headers = {"Authorization": "Bearer garbage"}
    try:
        response = requests.post(f"{BASE_URL}/upload/", headers=headers)
        print(f"Status: {response.status_code}, Body: {response.text}")
    except Exception as e: print(e)

if __name__ == "__main__":
    test_garbage_token()
    test_no_header()
    test_bearer_garbage()
