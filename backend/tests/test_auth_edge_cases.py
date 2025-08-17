"""
Test edge cases for Auth API endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_duplicate_signup():
    """Test duplicate email signup"""
    print("Testing duplicate email signup...")
    
    timestamp = int(time.time())
    email = f"duplicate{timestamp}@example.com"
    
    signup_data = {
        "name": "Test User",
        "email": email,
        "password": "testpassword123",
        "profile_image_url": "/user.png"
    }
    
    # First signup
    response1 = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"First signup - Status Code: {response1.status_code}")
    
    # Second signup with same email
    response2 = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Second signup - Status Code: {response2.status_code}")
    print(f"Response: {json.dumps(response2.json(), indent=2)}")
    
    if response2.status_code == 400 and "already taken" in response2.json().get("detail", ""):
        print("✅ Duplicate email properly rejected!")
        return True
    else:
        print("❌ Duplicate email not properly handled!")
        return False

def test_invalid_signin():
    """Test signin with invalid credentials"""
    print("\nTesting invalid signin...")
    
    signin_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✅ Invalid credentials properly rejected!")
        return True
    else:
        print("❌ Invalid credentials not properly handled!")
        return False

def test_unauthorized_access():
    """Test accessing protected endpoint without token"""
    print("\nTesting unauthorized access...")
    
    response = requests.get(f"{BASE_URL}/auth/user")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 403:
        print("✅ Unauthorized access properly rejected!")
        return True
    else:
        print("❌ Unauthorized access not properly handled!")
        return False

def test_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    print("\nTesting invalid token...")
    
    headers = {
        "Authorization": "Bearer invalid_token_here"
    }
    
    response = requests.get(f"{BASE_URL}/auth/user", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ Invalid token properly rejected!")
        return True
    else:
        print("❌ Invalid token not properly handled!")
        return False

def test_update_profile():
    """Test updating user profile"""
    print("\nTesting profile update...")
    
    # First create a user
    timestamp = int(time.time())
    email = f"profile{timestamp}@example.com"
    
    signup_data = {
        "name": "Profile Test User",
        "email": email,
        "password": "testpassword123",
        "profile_image_url": "/user.png"
    }
    
    signup_response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    if signup_response.status_code != 200:
        print("❌ Failed to create user for profile test!")
        return False
    
    token = signup_response.json().get("token")
    
    # Update profile
    update_data = {
        "name": "Updated Name",
        "profile_image_url": "/updated_user.png"
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/auth/update/profile", json=update_data, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        updated_user = response.json()
        if updated_user.get("name") == "Updated Name":
            print("✅ Profile update successful!")
            return True
    
    print("❌ Profile update failed!")
    return False

if __name__ == "__main__":
    print("🧪 Testing Auth API Edge Cases")
    print("=" * 50)
    
    results = []
    
    # Test duplicate signup
    results.append(test_duplicate_signup())
    
    # Test invalid signin
    results.append(test_invalid_signin())
    
    # Test unauthorized access
    results.append(test_unauthorized_access())
    
    # Test invalid token
    results.append(test_invalid_token())
    
    # Test profile update
    results.append(test_update_profile())
    
    print(f"\n🏁 Testing completed!")
    print(f"✅ Passed: {sum(results)}/{len(results)} tests")
    
    if all(results):
        print("🎉 All edge case tests passed!")
    else:
        print("⚠️  Some tests failed!")
