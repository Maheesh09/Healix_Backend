
import requests
import time
import sys
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/v1/users"

def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def verify_crud():
    # 1. Create User
    email = f"test_{get_random_string(5)}@example.com"
    nic = f"NIC_{get_random_string(5)}"
    payload = {
        "email": email,
        "password": "secretpassword",
        "nic": nic,
        "full_name": "Test User",
        "is_active": True,
        "user_type": "PATIENT"
    }
    
    print(f"Creating user with email: {email}...")
    response = requests.post(BASE_URL + "/", json=payload)
    if response.status_code != 200:
        print(f"Failed to create user: {response.text}")
        sys.exit(1)
    
    user_data = response.json()
    user_id = user_data["id"]
    print(f"User created: {user_data}")
    
    # 2. Read User
    print(f"Reading user {user_id}...")
    response = requests.get(f"{BASE_URL}/{user_id}")
    if response.status_code != 200:
        print(f"Failed to read user: {response.text}")
        sys.exit(1)
    print(f"Read user: {response.json()}")

    # 3. Update User
    print(f"Updating user {user_id}...")
    update_payload = {"full_name": "Updated Name"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_payload)
    if response.status_code != 200:
        print(f"Failed to update user: {response.text}")
        sys.exit(1)
    
    updated_user = response.json()
    if updated_user["full_name"] != "Updated Name":
        print("Update failed: Name match mismatch")
        sys.exit(1)
    print(f"User updated: {updated_user}")

    # 4. List Users
    print("Listing users...")
    response = requests.get(BASE_URL + "/")
    if response.status_code != 200:
        print(f"Failed to list users: {response.text}")
        sys.exit(1)
    users = response.json()
    print(f"Found {len(users)} users")

    # 5. Delete User
    print(f"Deleting user {user_id}...")
    response = requests.delete(f"{BASE_URL}/{user_id}")
    if response.status_code != 200:
        print(f"Failed to delete user: {response.text}")
        sys.exit(1)
    print("User deleted")

    # Verify deletion
    response = requests.get(f"{BASE_URL}/{user_id}")
    if response.status_code != 404:
        print("User still exists after deletion!")
        sys.exit(1)
    print("Deletion verified")

if __name__ == "__main__":
    # Wait for server to start (if running in parallel)
    print("Waiting for server to be ready...")
    for _ in range(10):
        try:
            requests.get("http://127.0.0.1:8000/")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        print("Server not reachable. Make sure it's running.")
        sys.exit(1)

    verify_crud()
