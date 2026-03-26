"""
Test script to verify charge API behavior
"""
import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

# Register a new test user
test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
register_data = {
    "email": test_email,
    "password": "password123",
    "nickname": "testuser",
    "gender": "male",
    "age": 25,
    "height": 170.0,
    "current_weight": 70.0,
    "target_weight": 65.0
}

print("1. Registering new user...")
response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
if response.status_code == 201:
    user_data = response.json()
    token = user_data["access_token"]
    user_id = user_data["user_id"]
    print(f"   Registered successfully. User ID: {user_id}")
else:
    print(f"   Registration failed: {response.status_code} - {response.text}")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Check initial balance
print("\n2. Checking initial balance...")
response = requests.get(f"{BASE_URL}/api/payments/users/{user_id}/balance", headers=headers)
if response.status_code == 200:
    balance_data = response.json()
    initial_balance = balance_data["available_balance"]
    print(f"   Initial balance: {initial_balance}")
else:
    print(f"   Failed to get balance: {response.status_code} - {response.text}")
    exit(1)

# Charge 200
print("\n3. Charging 200...")
charge_data = {
    "amount": 200.0,
    "payment_method_id": "default",
    "user_id": "current_user_id"
}
response = requests.post(f"{BASE_URL}/api/payments/charge", json=charge_data, headers=headers)
if response.status_code == 200:
    charge_result = response.json()
    print(f"   Charge result: {charge_result}")
else:
    print(f"   Charge failed: {response.status_code} - {response.text}")
    exit(1)

# Check balance after charge
print("\n4. Checking balance after charge...")
response = requests.get(f"{BASE_URL}/api/payments/users/{user_id}/balance", headers=headers)
if response.status_code == 200:
    balance_data = response.json()
    new_balance = balance_data["available_balance"]
    print(f"   New balance: {new_balance}")
    print(f"   Expected: {initial_balance + 200}")
    if new_balance == initial_balance + 200:
        print("   ✅ Balance updated correctly!")
    else:
        print(f"   ❌ Balance NOT updated! Still {new_balance} instead of {initial_balance + 200}")
else:
    print(f"   Failed to get balance: {response.status_code} - {response.text}")

# Try to create a betting plan
print("\n5. Trying to create a betting plan...")
plan_data = {
    "bet_amount": 200.0,
    "start_date": "2026-03-16",
    "end_date": "2026-03-29",
    "initial_weight": 60.0,
    "target_weight": 50.0
}
response = requests.post(f"{BASE_URL}/api/betting-plans", json=plan_data, headers=headers)
if response.status_code == 201:
    print(f"   ✅ Plan created successfully!")
elif response.status_code == 402:
    print(f"   ❌ Insufficient balance error: {response.json()}")
else:
    print(f"   Failed: {response.status_code} - {response.text}")
