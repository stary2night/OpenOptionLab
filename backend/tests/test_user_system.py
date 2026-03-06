"""
User System API Tests
测试用户系统的所有 API 端点
"""
import asyncio
import httpx
import pytest
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Test user data
test_user = {
    "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
    "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
    "password": "TestPassword123!",
    "phone": "13800138000"
}

# Store tokens and user data
tokens = {}
current_user = {}


async def test_register():
    """Test user registration"""
    print("\n📝 Testing User Registration...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/register",
            json=test_user
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration successful")
            return True
        elif response.status_code == 400 and "already exists" in response.text:
            print("⚠️ User already exists, continuing...")
            return True
        else:
            print("❌ Registration failed")
            return False


async def test_login():
    """Test user login"""
    print("\n🔑 Testing User Login...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tokens["access_token"] = data["access_token"]
            tokens["refresh_token"] = data["refresh_token"]
            current_user.update(data["user"])
            print(f"✅ Login successful, user: {data['user']['username']}")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False


async def test_get_current_user():
    """Test get current user info"""
    print("\n👤 Testing Get Current User...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Got user info: {user['username']}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_update_profile():
    """Test update user profile"""
    print("\n✏️ Testing Update Profile...")
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BASE_URL}{API_PREFIX}/auth/profile",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "bio": "Test bio from API test",
                "phone": "13900139000"
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Profile updated: {response.json()}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_add_favorite():
    """Test add favorite symbol"""
    print("\n⭐ Testing Add Favorite...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/user/favorites",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "symbol": "510050",  # 50ETF
                "symbol_type": "ETF",
                "remark": "Test favorite"
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ Favorite added: {response.json()}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_get_favorites():
    """Test get favorites"""
    print("\n📋 Testing Get Favorites...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/user/favorites",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            favorites = response.json()
            print(f"✅ Got {len(favorites)} favorites")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_create_strategy():
    """Test create strategy"""
    print("\n📊 Testing Create Strategy...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/user/strategies",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json={
                "name": "Test Strategy",
                "description": "A test strategy",
                "strategy_type": "custom",
                "legs": [
                    {
                        "symbol": "10005213",
                        "side": "buy",
                        "quantity": 1,
                        "option_type": "call",
                        "strike": 2.5,
                        "expiry": "2025-03-26"
                    }
                ],
                "parameters": {
                    "max_profit": 1000,
                    "max_loss": -500
                },
                "tags": ["test", "bullish"]
            }
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            strategy = response.json()
            print(f"✅ Strategy created: {strategy['name']}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_get_strategies():
    """Test get strategies"""
    print("\n📈 Testing Get Strategies...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/user/strategies",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            strategies = response.json()
            print(f"✅ Got {len(strategies)} strategies")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_get_notifications():
    """Test get notifications"""
    print("\n🔔 Testing Get Notifications...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/user/notifications",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Got {len(notifications)} notifications")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_get_unread_count():
    """Test get unread notification count"""
    print("\n🔢 Testing Get Unread Count...")
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}{API_PREFIX}/user/notifications/unread-count",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            count = response.json()
            print(f"✅ Unread count: {count}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_refresh_token():
    """Test refresh token"""
    print("\n🔄 Testing Refresh Token...")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}{API_PREFIX}/auth/refresh",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tokens["access_token"] = data["access_token"]
            print("✅ Token refreshed successfully")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def test_delete_favorite():
    """Test delete favorite"""
    print("\n🗑️ Testing Delete Favorite...")
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}{API_PREFIX}/user/favorites/510050",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 204:
            print("✅ Favorite deleted")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False


async def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("🚀 Starting User System API Tests")
    print("=" * 60)
    
    results = []
    
    # Authentication tests
    results.append(("Register", await test_register()))
    results.append(("Login", await test_login()))
    results.append(("Get Current User", await test_get_current_user()))
    results.append(("Update Profile", await test_update_profile()))
    
    # Favorite tests
    results.append(("Add Favorite", await test_add_favorite()))
    results.append(("Get Favorites", await test_get_favorites()))
    
    # Strategy tests
    results.append(("Create Strategy", await test_create_strategy()))
    results.append(("Get Strategies", await test_get_strategies()))
    
    # Notification tests
    results.append(("Get Notifications", await test_get_notifications()))
    results.append(("Get Unread Count", await test_get_unread_count()))
    
    # Token refresh
    results.append(("Refresh Token", await test_refresh_token()))
    
    # Cleanup
    results.append(("Delete Favorite", await test_delete_favorite()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    failed = sum(1 for _, r in results if not r)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️ {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1)
