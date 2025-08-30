#!/usr/bin/env python3
"""
Simple health check script for the Ringba No Values webhook service
Usage: python health_check.py
"""

import requests
import json
from datetime import datetime

def check_service_health():
    """Check if the webhook service is healthy"""
    url = "https://dl-novalue-monitor.onrender.com/"
    
    try:
        print(f"🔍 Checking service health at {url}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status', 'unknown')}")
            print(f"🎯 Campaign Filter: {data.get('filters', {}).get('campaign_name', 'unknown')}")
            print(f"🎯 Target Filter: {data.get('filters', {}).get('target_name', 'unknown')}")
            print("🎉 Service is HEALTHY!")
            return True
        else:
            print(f"❌ Service returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - Service is not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Connection Error - Service is down")
        return False
    except Exception as e:
        print(f"💥 Error checking service: {str(e)}")
        return False

if __name__ == "__main__":
    print("🏥 Ringba No Values Webhook Health Check")
    print("=" * 50)
    
    is_healthy = check_service_health()
    
    print("=" * 50)
    if is_healthy:
        print("✅ HEALTH CHECK PASSED - Service is operational")
    else:
        print("❌ HEALTH CHECK FAILED - Service needs attention")

