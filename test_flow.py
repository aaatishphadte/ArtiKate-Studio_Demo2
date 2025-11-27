import requests
import os

BASE_URL = "http://127.0.0.1:8001"

def test_flow():
    # 1. Register User A
    print("Registering User A...")
    resp = requests.post(f"{BASE_URL}/register/", json={"username": "usera", "password": "password123"})
    if resp.status_code == 201:
        token_a = resp.json()["token"]
        print("User A registered.")
    elif resp.status_code == 400 and "already exists" in resp.text:
        print("User A already exists, logging in...")
        resp = requests.post(f"{BASE_URL}/login/", json={"username": "usera", "password": "password123"})
        token_a = resp.json()["token"]
    else:
        print(f"Failed to register User A: {resp.text}")
        return

    # 2. Register User B
    print("Registering User B...")
    resp = requests.post(f"{BASE_URL}/register/", json={"username": "userb", "password": "password123"})
    if resp.status_code == 201:
        token_b = resp.json()["token"]
        print("User B registered.")
    elif resp.status_code == 400 and "already exists" in resp.text:
        print("User B already exists, logging in...")
        resp = requests.post(f"{BASE_URL}/login/", json={"username": "userb", "password": "password123"})
        token_b = resp.json()["token"]
    else:
        print(f"Failed to register User B: {resp.text}")
        return

    # Create dummy files
    with open("doc_a.txt", "w") as f:
        f.write("The secret code for User A is ALPHA-123.")
    
    with open("doc_b.txt", "w") as f:
        f.write("The secret code for User B is BETA-456.")

    # 3. Upload for User A
    print("Uploading doc for User A...")
    with open("doc_a.txt", "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload/", 
            headers={"Authorization": f"Token {token_a}"},
            files={"file": f}
        )
    print(f"User A Upload: {resp.status_code}")
    if resp.status_code != 201:
        with open("failure.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Saved failure.html")

    # 4. Upload for User B
    print("Uploading doc for User B...")
    with open("doc_b.txt", "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/upload/", 
            headers={"Authorization": f"Token {token_b}"},
            files={"file": f}
        )
    print(f"User B Upload: {resp.status_code} {resp.text}")

    # 5. Ask as User A
    print("Asking as User A...")
    resp = requests.post(
        f"{BASE_URL}/ask/",
        headers={"Authorization": f"Token {token_a}"},
        json={"question": "What is the secret code?"}
    )
    print(f"User A Answer: {resp.json().get('answer')}")

    # 6. Ask as User B
    print("Asking as User B...")
    resp = requests.post(
        f"{BASE_URL}/ask/",
        headers={"Authorization": f"Token {token_b}"},
        json={"question": "What is the secret code?"}
    )
    print(f"User B Answer: {resp.json().get('answer')}")

if __name__ == "__main__":
    test_flow()
