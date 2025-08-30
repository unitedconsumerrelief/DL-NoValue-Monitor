#!/usr/bin/env python3
"""
Test script to test calls with empty target names (No Value calls)
Usage: python test_empty_target.py
"""

import requests
import json
from datetime import datetime

# Configuration - Test the deployed Render service
WEBHOOK_URL = "https://dl-novalue-monitor.onrender.com/ringba-webhook"
TEST_CAMPAIGN_NAME = "SPANISH DEBT | 1.0 STANDARD"
TEST_TARGET_NAME = ""  # Empty target name to simulate No Value calls

def test_empty_target_webhook():
    """Test a webhook with empty target name (should now pass the filter)"""
    payload = {
        "campaignName": TEST_CAMPAIGN_NAME,
        "targetName": TEST_TARGET_NAME,  # Empty string
        "callerId": "REAL_CALLER_123",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 0,
        "status": "completed"
    }
    
    print("📞 Testing webhook with empty target name (No Value call)...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 50)
        
        if response.status_code == 200:
            if "success" in response.text:
                print("✅ SUCCESS! Empty target call was processed")
                return True
            else:
                print("⚠️  Call was received but may have been filtered")
                return False
        else:
            print("❌ Webhook request failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

def test_null_target_webhook():
    """Test a webhook with null target name (should also pass the filter)"""
    payload = {
        "campaignName": TEST_CAMPAIGN_NAME,
        "targetName": None,  # Null target name
        "callerId": "REAL_CALLER_456",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 0,
        "status": "completed"
    }
    
    print("📞 Testing webhook with null target name (No Value call)...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print("-" * 50)
        
        if response.status_code == 200:
            if "success" in response.text:
                print("✅ SUCCESS! Null target call was processed")
                return True
            else:
                print("⚠️  Call was received but may have been filtered")
                return False
        else:
            print("❌ Webhook request failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {str(e)}")
        return False

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

if __name__ == "__main__":
    print("🚀 Testing Empty Target Name Filtering (No Value Calls)")
    print("=" * 60)
    print(f"Service URL: {WEBHOOK_URL}")
    print(f"Campaign: {TEST_CAMPAIGN_NAME}")
    print(f"Target: '{TEST_TARGET_NAME}' (empty string)")
    print("=" * 60)
    
    # Test health check first
    health_ok = test_health_check()
    
    if health_ok:
        # Test empty target name
        empty_target_ok = test_empty_target_webhook()
        
        # Test null target name
        null_target_ok = test_null_target_webhook()
        
        print("✅ Testing complete!")
        print(f"Health Check: {'✅' if health_ok else '❌'}")
        print(f"Empty Target: {'✅' if empty_target_ok else '❌'}")
        print(f"Null Target: {'✅' if null_target_ok else '❌'}")
        
        if empty_target_ok or null_target_ok:
            print("\n🎉 SUCCESS! Your system can now catch No Value calls!")
            print("Check your Google Sheet and Slack channel for the test entries.")
        else:
            print("\n⚠️  The filtering still needs adjustment.")
    else:
        print("❌ Health check failed. Service may not be ready.")
