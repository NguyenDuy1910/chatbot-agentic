"""
Test script for Auth API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_signup():
    """Test user registration"""
    print("Testing user signup...")
    
    import time
    timestamp = int(time.time())

    signup_data = {
        "name": "Test User",
        "email": f"test{timestamp}@example.com",
        "password": "testpassword123",
        "profile_image_url": "/user.png"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Signup successful!")
        return response.json()
    else:
        print("❌ Signup failed!")
        return None

def test_signin(email):
    """Test user login"""
    print("\nTesting user signin...")

    signin_data = {
        "email": email,
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signin", json=signin_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Signin successful!")
        return response.json()
    else:
        print("❌ Signin failed!")
        return None

def test_get_user(token):
    """Test get current user"""
    print("\nTesting get current user...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/user", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get user successful!")
        return response.json()
    else:
        print("❌ Get user failed!")
        return None

def test_signout(token):
    """Test user logout"""
    print("\nTesting user signout...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signout", headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Signout successful!")
        return True
    else:
        print("❌ Signout failed!")
        return False

if __name__ == "__main__":
    print("🧪 Testing Auth API Endpoints")
    print("=" * 50)
    
    # Test signup
    signup_result = test_signup()

    if signup_result:
        token = signup_result.get("token")
        email = signup_result.get("email")

        # Test signin
        signin_result = test_signin(email)
        
        if signin_result:
            token = signin_result.get("token")
            
            # Test get user
            test_get_user(token)
            
            # Test signout
            test_signout(token)
    
    print("\n🏁 Testing completed!")
