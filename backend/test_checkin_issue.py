# -*- coding: utf-8 -*-
"""
Test check-in functionality - Debug "invalid plan ID" error
"""
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_checkin():
    # Step 1: Login
    login_data = {
        "email": "test3@qq.com",
        "password": "12345678"
    }
    response = httpx.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Step 1 - Login status code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login failed: {response.json()}")
        return
    
    token = response.json()["access_token"]
    user_id = response.json()["user_id"]
    print(f"[OK] Login successful, User ID: {user_id}")
    
    # Step 2: Get user's plans
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/betting-plans/users/{user_id}/plans", headers=headers)
    print(f"\nStep 2 - Get plans status code: {response.status_code}")
    
    if response.status_code == 200:
        plans = response.json()
        active_plans = [p for p in plans if p["status"] == "active"]
        print(f"[OK] Found {len(active_plans)} ACTIVE plan(s)")
        
        if active_plans:
            plan_id = active_plans[0]["id"]
            print(f"Using plan ID: {plan_id}")
            
            # Step 3: Try to check in
            checkin_data = {
                "plan_id": plan_id,
                "weight": 79.5,
                "check_in_date": "2026-03-25"
            }
            response = httpx.post(f"{BASE_URL}/api/check-ins", json=checkin_data, headers=headers)
            print(f"\nStep 3 - Check-in status code: {response.status_code}")
            
            try:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if response.status_code == 201:
                    print("[OK] Check-in successful!")
                else:
                    print(f"[ERROR] Check-in failed: {result.get('message', result)}")
            except Exception as e:
                print(f"Failed to parse response: {e}")
        else:
            print("[ERROR] No ACTIVE plans found")
    else:
        print(f"Failed to get plans: {response.json()}")

if __name__ == "__main__":
    test_checkin()
