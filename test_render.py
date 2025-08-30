#!/usr/bin/env python3
"""
Test script to test the deployed Render service
Usage: python test_render.py
"""

import requests
import json
from datetime import datetime

# Configuration - Test the deployed Render service
WEBHOOK_URL = "https://dl-novalue-monitor.onrender.com/ringba-webhook"
TEST_CAMPAIGN_NAME = "SPANISH DEBT | 1.0 STANDARD"
TEST_TARGET_NAME = "-no value-"

def test_health_check():
    """Test the health check endpoint"""
    health_url = "https://dl-novalue-monitor.onrender.com/"
    
    print("🏥 Testing health check...")
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_valid_webhook():
    """Test a webhook that should pass the filter"""
    payload = {
        "campaignName": TEST_CAMPAIGN_NAME,
        "targetName": TEST_TARGET_NAME,
        "callerId": "TEST_CALLER_456",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 120,
        "status": "completed"
    }
    
    print("📞 Testing valid webhook...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Valid webhook test failed: {str(e)}")
        return False

def test_invalid_webhook():
    """Test a webhook that should be filtered out"""
    payload = {
        "campaignName": "Wrong Campaign",
        "targetName": "Wrong Target",
        "callerId": "WRONG_CALLER_789",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 60,
        "status": "completed"
    }
    
    print("🚫 Testing invalid webhook (should be filtered)...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Invalid webhook test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Deployed Render Service")
    print("=" * 50)
    print(f"Service URL: {WEBHOOK_URL}")
    print(f"Campaign: {TEST_CAMPAIGN_NAME}")
    print(f"Target: {TEST_TARGET_NAME}")
    print("=" * 50)
    
    # Test health check first
    health_ok = test_health_check()
    
    if health_ok:
        # Test invalid webhook (should be filtered)
        invalid_ok = test_invalid_webhook()
        
        # Test valid webhook (should be processed)
        valid_ok = test_valid_webhook()
        
        print("✅ Testing complete!")
        print(f"Health Check: {'✅' if health_ok else '❌'}")
        print(f"Invalid Webhook: {'✅' if invalid_ok else '❌'}")
        print(f"Valid Webhook: {'✅' if valid_ok else '❌'}")
        
        if valid_ok:
            print("\n🎉 Check your Google Sheet and Slack channel for results!")
        else:
            print("\n⚠️  Some tests failed. Check the logs above.")
    else:
        print("❌ Health check failed. Service may not be running.")

