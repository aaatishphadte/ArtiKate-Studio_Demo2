import os
import django
import requests
import sys
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def test_jwt_authentication():
    print("=" * 60)
    print("JWT Authentication Test Suite")
    print("=" * 60)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test 1: Register a new user
    print("\n[TEST 1] Registration with JWT tokens")
    print("-" * 60)
    
    username = f"jwt_test_user_{int(time.time())}"
    password = "test_password_123"
    
    register_url = f"{base_url}/register/"
    register_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(register_url, json=register_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            data = response.json()
            if "access" in data and "refresh" in data:
                print("✓ SUCCESS: Registration returned JWT tokens (access & refresh)")
                access_token = data["access"]
                refresh_token = data["refresh"]
            else:
                print("✗ FAILURE: Registration did not return JWT tokens")
                return
        else:
            print(f"✗ FAILURE: Registration failed with status {response.status_code}")
            return
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return
    
    # Test 2: Login with existing user
    print("\n[TEST 2] Login with JWT tokens")
    print("-" * 60)
    
    login_url = f"{base_url}/login/"
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "access" in data and "refresh" in data:
                print("✓ SUCCESS: Login returned JWT tokens")
            else:
                print("✗ FAILURE: Login did not return JWT tokens")
        else:
            print(f"✗ FAILURE: Login failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 3: Access protected endpoint with JWT
    print("\n[TEST 3] Accessing protected endpoint (/ask/) with JWT")
    print("-" * 60)
    
    ask_url = f"{base_url}/ask/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    ask_data = {
        "question": "What is JWT?"
    }
    
    try:
        response = requests.post(ask_url, json=ask_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ SUCCESS: JWT token authenticated successfully")
            print(f"Response preview: {str(response.text)[:200]}...")
        elif response.status_code == 401:
            print("✗ FAILURE: JWT token was rejected (401 Unauthorized)")
            print(f"Response: {response.text}")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 4: Test with invalid token
    print("\n[TEST 4] Accessing with INVALID JWT token")
    print("-" * 60)
    
    bad_headers = {
        "Authorization": "Bearer invalidtoken12345"
    }
    
    try:
        response = requests.post(ask_url, json=ask_data, headers=bad_headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 401:
            print("✓ SUCCESS: Invalid JWT token was correctly rejected")
        else:
            print(f"✗ FAILURE: Invalid token was NOT rejected (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 5: Test token refresh
    print("\n[TEST 5] Token Refresh")
    print("-" * 60)
    
    refresh_url = f"{base_url}/token/refresh/"
    refresh_data = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(refresh_url, json=refresh_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "access" in data:
                print("✓ SUCCESS: Token refresh returned new access token")
                new_access_token = data["access"]
                
                # Test 6: Use the new access token
                print("\n[TEST 6] Using refreshed access token")
                print("-" * 60)
                
                new_headers = {
                    "Authorization": f"Bearer {new_access_token}"
                }
                
                response = requests.post(ask_url, json=ask_data, headers=new_headers)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    print("✓ SUCCESS: Refreshed token works correctly")
                else:
                    print(f"✗ FAILURE: Refreshed token failed (Status: {response.status_code})")
            else:
                print("✗ FAILURE: Token refresh did not return access token")
        else:
            print(f"✗ FAILURE: Token refresh failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    # Test 7: Use standard token endpoint
    print("\n[TEST 7] Using /token/ endpoint (Standard JWT obtain)")
    print("-" * 60)
    
    token_url = f"{base_url}/token/"
    token_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(token_url, json=token_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "access" in data and "refresh" in data:
                print("✓ SUCCESS: /token/ endpoint returned JWT tokens")
            else:
                print("✗ FAILURE: /token/ endpoint did not return JWT tokens")
        else:
            print(f"✗ FAILURE: /token/ endpoint failed with status {response.status_code}")
    except Exception as e:
        print(f"✗ ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("JWT Authentication Test Suite Completed")
    print("=" * 60)

if __name__ == "__main__":
    test_jwt_authentication()
