#!/usr/bin/env python3
"""
Test script to verify the app works before deployment
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from grok_client import GrokClient
        print("✅ GrokClient imported successfully")
    except ImportError as e:
        print(f"❌ GrokClient import failed: {e}")
        return False
    
    try:
        from tavily_client import TavilyClient
        print("✅ TavilyClient imported successfully")
    except ImportError as e:
        print(f"❌ TavilyClient import failed: {e}")
        return False
    
    try:
        from ticket_api import TicketAPI
        print("✅ TicketAPI imported successfully")
    except ImportError as e:
        print(f"❌ TicketAPI import failed: {e}")
        return False
    
    return True

def test_api_connections():
    """Test API connections"""
    print("\n🔗 Testing API connections...")
    
    try:
        from grok_client import GrokClient
        grok = GrokClient()
        print("✅ GrokClient initialized successfully")
    except Exception as e:
        print(f"❌ GrokClient initialization failed: {e}")
        return False
    
    try:
        from tavily_client import TavilyClient
        tavily = TavilyClient()
        print("✅ TavilyClient initialized successfully")
    except Exception as e:
        print(f"❌ TavilyClient initialization failed: {e}")
        return False
    
    return True

def test_data_files():
    """Test that required data files exist"""
    print("\n📁 Testing data files...")
    
    required_files = [
        "tickets_data.json",
        "streamlit_app.py",
        "requirements.txt",
        "config.py",
        "utils.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def test_ticket_data():
    """Test that ticket data can be loaded"""
    print("\n🎫 Testing ticket data...")
    
    try:
        from utils import load_tickets_data
        tickets = load_tickets_data()
        
        if tickets and len(tickets) > 0:
            print(f"✅ Loaded {len(tickets)} tickets successfully")
            print(f"   Sample ticket: {tickets[0].get('id', 'N/A')}")
            return True
        else:
            print("❌ No tickets loaded")
            return False
    except Exception as e:
        print(f"❌ Failed to load tickets: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Pre-Deployment Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Tests", test_imports),
        ("API Connection Tests", test_api_connections),
        ("Data File Tests", test_data_files),
        ("Ticket Data Tests", test_ticket_data)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * len(test_name))
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Run: ./deploy_to_streamlit.sh")
        print("2. Follow the deployment guide")
        return True
    else:
        print("❌ Some tests failed. Please fix issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
