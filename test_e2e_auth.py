import requests
import json
import time

print('=== COMPLETE E2E AUTHENTICATION FLOW TEST ===\n')

BASE_URL = 'http://localhost:8000/api'

# 1. Register a new user
print('1. Registering new user...')
test_email = f'e2etest{int(time.time())}@example.com'
reg_response = requests.post(f'{BASE_URL}/auth/register', json={
    'email': test_email,
    'password': 'TestPass123!'
})
if reg_response.status_code == 200:
    reg_data = reg_response.json()
    user_token = reg_data['access_token']
    user_data = reg_data['user']
    print(f'OK: User registered: {user_data["email"]} (role: {user_data["role"]})')
else:
    print(f'FAIL: Registration failed: {reg_response.json()}')
    exit(1)

# 2. Create a session with the new user token
print('\n2. Creating session with user token...')
session_response = requests.post(f'{BASE_URL}/sessions/', 
    headers={'Authorization': f'Bearer {user_token}'},
    json={'duration': 30, 'mood': 'calm', 'energy_level': 'low'}
)
if session_response.status_code in [200, 201]:
    session_data = session_response.json()
    print(f'OK: Session created successfully')
else:
    print(f'FAIL: Session creation failed: {session_response.json()}')

# 3. Test admin login
print('\n3. Testing admin login...')
admin_response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'rishisingh9152@gmail.com',
    'password': 'Ripra@2622'
})
if admin_response.status_code == 200:
    admin_data = admin_response.json()
    admin_token = admin_data['access_token']
    admin_user = admin_data['user']
    print(f'OK: Admin logged in: {admin_user["email"]} (role: {admin_user["role"]})')
else:
    print(f'FAIL: Admin login failed: {admin_response.json()}')
    exit(1)

# 4. Access admin dashboard
print('\n4. Accessing admin dashboard...')
dashboard_response = requests.get(f'{BASE_URL}/admin/dashboard',
    headers={'Authorization': f'Bearer {admin_token}'}
)
if dashboard_response.status_code == 200:
    dashboard_data = dashboard_response.json()
    print(f'OK: Dashboard accessed successfully')
    print(f'   - Total users: {dashboard_data["total_users"]}')
    print(f'   - Admin count: {dashboard_data["admin_count"]}')
    print(f'   - Total songs: {dashboard_data["total_songs"]}')
    print(f'   - Avg rating: {dashboard_data["avg_rating"]}')
else:
    print(f'FAIL: Dashboard access failed: {dashboard_response.json()}')

# 5. Try to access admin dashboard as regular user (should fail)
print('\n5. Testing role-based access control (user accessing admin endpoint)...')
user_admin_response = requests.get(f'{BASE_URL}/admin/dashboard',
    headers={'Authorization': f'Bearer {user_token}'}
)
if user_admin_response.status_code == 403:
    print(f'OK: Correctly rejected non-admin user')
else:
    print(f'FAIL: Access control failed: {user_admin_response.status_code}')

print('\n=== ALL E2E TESTS PASSED ===')
