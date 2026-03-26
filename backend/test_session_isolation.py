"""
Test to verify database session isolation issue
"""
import requests
import json
import uuid
import os
from app.config import settings

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
user_data = response.json()
token = user_data["access_token"]
user_id = user_data["user_id"]
print(f"   User ID: {user_id}")

headers = {"Authorization": f"Bearer {token}"}

# Charge 200
print("\n2. Charging 200...")
charge_data = {
    "amount": 200.0,
    "payment_method_id": "default",
    "user_id": "current_user_id"
}
response = requests.post(f"{BASE_URL}/api/payments/charge", json=charge_data, headers=headers)
print(f"   Charge result: {response.json()}")

# Check balance immediately (same as charge endpoint would see)
print("\n3. Checking balance via API...")
response = requests.get(f"{BASE_URL}/api/payments/users/{user_id}/balance", headers=headers)
balance_data = response.json()
print(f"   Balance via API: {balance_data['available_balance']}")

# Now check what freeze_funds would see by directly querying
print("\n4. Simulating what freeze_funds sees...")
import sqlite3

# Resolve the same sqlite file path as app.database
db_url = settings.DATABASE_URL
if db_url.startswith('sqlite:'):
    db_path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
    if not os.path.isabs(db_path):
        # make absolute relative to backend directory
        base_dir = os.path.dirname(__file__)
        db_path = os.path.abspath(os.path.join(base_dir, db_path))
else:
    # fallback to tests' legacy path
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend', 'weight_loss_betting.db'))

print(f"   Using DB file for direct query: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT available_balance FROM balances WHERE user_id = ?', (user_id,))
result = cursor.fetchone()
print(f"   Balance in DB (direct query): {result[0] if result else 'NOT FOUND'}")
conn.close()

# Try to create a betting plan
print("\n5. Creating betting plan...")
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
    print(f"\n   This confirms the bug: balance was updated to 200 but freeze_funds still sees 0!")
else:
    print(f"   Failed: {response.status_code} - {response.text}")
