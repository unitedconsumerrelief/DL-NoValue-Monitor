#!/usr/bin/env python3
"""
Test script to simulate Ringba webhook calls
Usage: python test_webhook.py
"""

import requests
import json
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:5000/ringba-webhook"  # Change this to your deployed URL
TEST_CAMPAIGN_NAME = "SPANISH DEBT | 1.0 STANDARD"  # Updated to match your config
TEST_TARGET_NAME = "-no value-"      # Updated to match your config

def test_valid_webhook():
    """Test a webhook that should pass the filter"""
    payload = {
        "campaignName": TEST_CAMPAIGN_NAME,
        "targetName": TEST_TARGET_NAME,
        "callerId": "TEST_CALLER_123",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 120,
        "status": "completed"
    }
    
    print("Testing valid webhook...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("-" * 50)

def test_invalid_webhook():
    """Test a webhook that should be filtered out"""
    payload = {
        "campaignName": "Wrong Campaign",
        "targetName": "Wrong Target",
        "callerId": "WRONG_CALLER_456",
        "timestamp": datetime.utcnow().isoformat(),
        "duration": 60,
        "status": "completed"
    }
    
    print("Testing invalid webhook (should be filtered)...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(WEBHOOK_URL, json=payload)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("-" * 50)

def test_health_check():
    """Test the health check endpoint"""
    health_url = WEBHOOK_URL.replace("/ringba-webhook", "/")
    
    print("Testing health check...")
    response = requests.get(health_url)
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("-" * 50)

if __name__ == "__main__":
    print("🚀 Ringba Webhook Test Script")
    print("=" * 50)
    
    # Test health check first
    test_health_check()
    
    # Test invalid webhook (should be filtered)
    test_invalid_webhook()
    
    # Test valid webhook (should be processed)
    test_valid_webhook()
    
    print("✅ Testing complete!")
    print("\nCheck your Google Sheet and Slack channel for results.")
