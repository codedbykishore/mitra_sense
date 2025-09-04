#!/usr/bin/env python3
"""
Test script for Crisis API endpoints
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8001/api/v1/crisis"

def test_health():
    """Test the health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_keywords():
    """Test the keywords endpoint"""
    print("\nTesting /keywords endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/keywords")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_crisis_detection():
    """Test crisis detection endpoint"""
    print("\nTesting /detect endpoint...")
    test_cases = [
        {
            "text": "I feel sad today",
            "expected_risk": "low"
        },
        {
            "text": "I can't cope anymore, feeling hopeless",
            "expected_risk": "medium"
        },
        {
            "text": "I want to kill myself, life is worthless",
            "expected_risk": "high"
        },
        {
            "text": "मैं आत्महत्या करना चाहता हूं",  # Hindi: I want to commit suicide
            "expected_risk": "high"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}: '{test_case['text'][:30]}...'")
        try:
            payload = {
                "text": test_case["text"],
                "user_id": f"test_user_{i}"
            }
            response = requests.post(f"{BASE_URL}/detect", json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Risk Score: {data['risk_score']}")
                print(f"Risk Level: {data['risk_level']}")
                print(f"Expected: {test_case['expected_risk']}")
                print(f"Escalation Performed: {data.get('escalation_performed', False)}")
                print(f"Reason: {data.get('reason', 'N/A')}")
            else:
                print(f"Error Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

def test_status():
    """Test status endpoint"""
    print("\nTesting /status endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/status/test_user_1")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("🔥 Testing MITRA Crisis Detection API Endpoints")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Server not running on localhost:8001")
        print("Please start the server with: uvicorn app.main:app --reload --port 8001")
        sys.exit(1)
    
    # Run tests
    test_health()
    test_keywords()
    test_crisis_detection()
    test_status()
    
    print("\n✅ Crisis API testing completed!")

if __name__ == "__main__":
    main()
