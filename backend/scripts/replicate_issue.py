import requests, uuid, time, os, json
BASE_URL = "http://127.0.0.1:8000"
email = f"replicate_{uuid.uuid4().hex[:8]}@example.com"
register_data = {
    "email": email,
    "password": "Password123!",
    "nickname": "replica",
    "gender": "male",
    "age": 30,
    "height": 170.0,
    "current_weight": 70.0,
    "target_weight": 65.0
}
print('Registering:', email)
r = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
print('Register status:', r.status_code)
try:
    print('Register response:', r.json())
except Exception:
    print('Register text:', r.text)

if r.status_code not in (200,201):
    raise SystemExit('register failed')

token = r.json().get('access_token')
user_id = r.json().get('user_id') or r.json().get('id')
headers = {"Authorization": f"Bearer {token}"}

print('\nCharging 200')
r = requests.post(f"{BASE_URL}/api/payments/charge", json={"amount":200.0, "payment_method_id":"default", "user_id": user_id}, headers=headers)
print('Charge status:', r.status_code)
try:
    print('Charge response:', r.json())
except Exception:
    print('Charge text:', r.text)

print('\nCheck balance via API')
r = requests.get(f"{BASE_URL}/api/payments/users/{user_id}/balance", headers=headers)
print('Balance status:', r.status_code)
try:
    print('Balance response:', r.json())
except Exception:
    print('Balance text:', r.text)

print('\nCreate betting plan')
plan = {
    "bet_amount": 200.0,
    "start_date": "2026-03-16",
    "end_date": "2026-03-29",
    "initial_weight": 60.0,
    "target_weight": 50.0,
    "description": "replicate"
}
r = requests.post(f"{BASE_URL}/api/betting-plans", json=plan, headers=headers)
print('Plan create status:', r.status_code)
try:
    print('Plan create response:', json.dumps(r.json(), ensure_ascii=False))
except Exception:
    print('Plan create text:', r.text)

# show last lines from app.log if exists
logpath = os.path.join(os.getcwd(), 'logs', 'app.log')
print('\nLog file:', logpath)
if os.path.exists(logpath):
    with open(logpath, 'rb') as f:
        f.seek(0, os.SEEK_END)
        size = f.tell()
        seek = max(0, size-20000)
        f.seek(seek)
        data = f.read().decode('utf-8', errors='replace')
        print('\n=== app.log tail ===')
        print(data)
else:
    print('No app.log')

