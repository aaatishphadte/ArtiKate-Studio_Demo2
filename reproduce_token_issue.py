import os
import django
import requests
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def test_token_auth():
    print("--- Starting Token Auth Test ---")
    
    # 1. Create or get a test user
    username = "test_auth_user"
    password = "test_password_123"
    email = "test@example.com"
    
    user, created = User.objects.get_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()
        print(f"Created test user: {username}")
    else:
        print(f"Using existing test user: {username}")

    # 2. Get or create token
    token_obj, _ = Token.objects.get_or_create(user=user)
    token_key = token_obj.key
    print(f"Token: {token_key}")

    # 3. Test URL
    url = "http://127.0.0.1:8000/ask/"
    
    # 4. Test with VALID token
    headers = {
        "Authorization": f"Token {token_key}"
    }
    data = {
        "question": "Hello?"
    }
    
    print(f"\nAttempting request to {url} with VALID token...")
    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("SUCCESS: Valid token was accepted.")
        elif response.status_code == 401:
            print("FAILURE: Valid token was rejected (401 Unauthorized).")
        else:
            print(f"Unexpected status code: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Is it running on port 8000?")
        return

    # 5. Test with INVALID token
    print(f"\nAttempting request to {url} with INVALID token...")
    bad_headers = {
        "Authorization": "Token invalidtoken12345"
    }
    try:
        response = requests.post(url, json=data, headers=bad_headers)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 401:
            print("SUCCESS: Invalid token was rejected.")
        else:
            print(f"FAILURE: Invalid token was NOT rejected properly (Status: {response.status_code}).")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_token_auth()
