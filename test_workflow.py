#!/usr/bin/env python3
"""
Test script to validate workflow functionality
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    try:
        import app
        print("✅ App module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import app module: {e}")
        return False

def test_create_app():
    """Test create_app function"""
    try:
        from app import create_app
        app_instance, socketio = create_app()
        print("✅ create_app function works")
        return True
    except Exception as e:
        print(f"❌ create_app failed: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    try:
        from app import create_app
        app_instance, socketio = create_app()
        
        with app_instance.test_client() as client:
            response = client.get('/health')
            print(f"Health endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed with status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running workflow validation tests...")
    
    tests = [
        test_imports,
        test_create_app,
        test_health_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main()