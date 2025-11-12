#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Comprehensive test suite for Daur-AI v2.0
Tests all core modules: input, hardware, vision, security, database, and API
"""

import sys
import os
import json
import time
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_input_module():
    """Test the input control module"""
    print("\n" + "="*60)
    print("Testing Input Module (RealInputController)")
    print("="*60)
    
    try:
        from src.input.real_input_controller import RealInputController, RealMouseController, RealKeyboardController
        
        # Test initialization
        controller = RealInputController()
        print("✓ RealInputController initialized")
        
        # Test mouse controller
        mouse = RealMouseController()
        print("✓ RealMouseController initialized")
        
        # Test keyboard controller
        keyboard = RealKeyboardController()
        print("✓ RealKeyboardController initialized")
        
        return True
    except Exception as e:
        print(f"✗ Input module test failed: {e}")
        return False


def test_hardware_module():
    """Test the hardware monitoring module"""
    print("\n" + "="*60)
    print("Testing Hardware Module (RealHardwareMonitor)")
    print("="*60)
    
    try:
        from src.hardware.real_hardware_monitor import RealHardwareMonitor
        
        # Test initialization
        monitor = RealHardwareMonitor()
        print("✓ RealHardwareMonitor initialized")
        
        # Test getting full status
        status = monitor.get_full_status()
        print(f"✓ Hardware status retrieved")
        
        # Test getting CPU metrics
        cpu = monitor.get_cpu_metrics()
        print(f"✓ CPU metrics: {cpu['percent']}%")
        
        # Test getting memory metrics
        memory = monitor.get_memory_metrics()
        print(f"✓ Memory metrics: {memory['percent']}%")
        
        # Test getting disk metrics
        disk = monitor.get_disk_metrics()
        print(f"✓ Disk metrics: {disk['percent']}%")
        
        # Test getting network metrics
        network = monitor.get_network_metrics()
        print(f"✓ Network metrics retrieved")
        
        return True
    except Exception as e:
        print(f"✗ Hardware module test failed: {e}")
        return False


def test_vision_module():
    """Test the vision system module"""
    print("\n" + "="*60)
    print("Testing Vision Module (RealVisionSystem)")
    print("="*60)
    
    try:
        from src.vision.real_vision_system import RealVisionSystem
        
        # Test initialization
        vision = RealVisionSystem()
        print("✓ RealVisionSystem initialized")
        
        # Test OCR engine
        ocr_engine = vision.ocr_engine
        print(f"✓ OCR engine: {ocr_engine}")
        
        return True
    except Exception as e:
        print(f"✗ Vision module test failed: {e}")
        return False


def test_security_module():
    """Test the security module"""
    print("\n" + "="*60)
    print("Testing Security Module (RealSecurityManager)")
    print("="*60)
    
    try:
        from src.security.real_security_manager import RealSecurityManager, UserRole
        
        # Test initialization
        security = RealSecurityManager()
        print("✓ RealSecurityManager initialized")
        
        # Test user registration
        user_id = security.register_user('testuser', 'test@example.com', 'password123')
        print(f"✓ User registered: {user_id}")
        
        # Test user authentication
        valid, payload = security.authenticate_user('testuser', 'password123')
        print(f"✓ User authenticated: {valid}")
        
        # Test JWT token creation (correct method name)
        token = security.create_access_token('testuser', UserRole.USER.value)
        print(f"✓ JWT token created: {token[:20]}...")
        
        # Test JWT token verification
        valid, payload = security.verify_token(token)
        print(f"✓ JWT token verified: {valid}")
        
        # Test API key generation (correct method name)
        api_key = security.create_api_key('testuser')
        print(f"✓ API key generated: {api_key[:20]}...")
        
        # Test API key verification
        valid, username = security.verify_api_key(api_key)
        print(f"✓ API key verified: {valid}")
        
        # Test data encryption
        encrypted = security.encrypt_data('sensitive data')
        print(f"✓ Data encrypted: {encrypted[:20]}...")
        
        # Test data decryption
        decrypted = security.decrypt_data(encrypted)
        print(f"✓ Data decrypted: {decrypted}")
        
        return True
    except Exception as e:
        print(f"✗ Security module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_module():
    """Test the database module"""
    print("\n" + "="*60)
    print("Testing Database Module (RealDatabase)")
    print("="*60)
    
    try:
        from src.database.real_database import RealDatabase
        
        # Test initialization with in-memory database
        db = RealDatabase(':memory:')
        print("✓ RealDatabase initialized")
        
        # Test user operations
        user_id = db.insert_user('dbuser', 'db@example.com', 'hashedpass', 'user')
        print(f"✓ User inserted with ID: {user_id}")
        
        # Test user retrieval
        user = db.get_user('dbuser')
        print(f"✓ User retrieved: {user['username']}")
        
        # Test hardware metrics
        success = db.insert_hardware_metrics(45.5, 62.3, 78.9, 30.0, 50.0, 85.0, 65.0)
        print(f"✓ Hardware metrics inserted: {success}")
        
        # Test hardware metrics retrieval
        metrics = db.get_hardware_metrics(limit=5)
        print(f"✓ Hardware metrics retrieved: {len(metrics)} entries")
        
        # Test vision analysis
        success = db.insert_vision_analysis('test.jpg', 'OCR Text', 0.95, 2, '[]', 1, '[]', user_id)
        print(f"✓ Vision analysis inserted: {success}")
        
        # Test user actions
        success = db.insert_action('mouse_click', '{"x": 100, "y": 200}', user_id)
        print(f"✓ User action inserted: {success}")
        
        # Test statistics
        stats = db.get_statistics()
        print(f"✓ Statistics retrieved: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Database module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_server():
    """Test the API server"""
    print("\n" + "="*60)
    print("Testing API Server (RealAPIServer)")
    print("="*60)
    
    try:
        from src.web.real_api_server import app
        
        # Test Flask app initialization
        print("✓ Flask app initialized")
        
        # Count endpoints
        endpoints = [rule for rule in app.url_map.iter_rules()]
        print(f"✓ API endpoints available: {len(endpoints)}")
        
        # List some endpoints
        api_endpoints = [str(rule) for rule in endpoints if '/api' in str(rule)]
        print(f"✓ API routes: {len(api_endpoints)}")
        for endpoint in api_endpoints[:5]:
            print(f"  - {endpoint}")
        
        return True
    except Exception as e:
        print(f"✗ API server test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test integration between modules"""
    print("\n" + "="*60)
    print("Testing Module Integration")
    print("="*60)
    
    try:
        from src.security.real_security_manager import RealSecurityManager, UserRole
        from src.database.real_database import RealDatabase
        from src.hardware.real_hardware_monitor import RealHardwareMonitor
        
        # Create instances
        security = RealSecurityManager()
        db = RealDatabase(':memory:')
        hardware = RealHardwareMonitor()
        
        # Register user
        user_id = security.register_user('integrationuser', 'integration@example.com', 'password123')
        print(f"✓ User registered: {user_id}")
        
        # Insert user into database
        db_user_id = db.insert_user('integrationuser', 'integration@example.com', 'hashedpass', 'user')
        print(f"✓ User inserted into database: {db_user_id}")
        
        # Get hardware metrics and insert into database
        cpu = hardware.get_cpu_metrics()
        memory = hardware.get_memory_metrics()
        disk = hardware.get_disk_metrics()
        
        success = db.insert_hardware_metrics(
            cpu['percent'], 
            memory['percent'], 
            disk['percent'], 
            0.0, 0.0, 0.0, 0.0
        )
        print(f"✓ Hardware metrics stored in database: {success}")
        
        # Insert user action
        action_data = json.dumps({'module': 'integration_test', 'status': 'success'})
        success = db.insert_action('integration_test', action_data, db_user_id)
        print(f"✓ User action logged: {success}")
        
        # Get statistics
        stats = db.get_statistics()
        print(f"✓ Database statistics: {stats}")
        
        return True
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("DAUR-AI v2.0 COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    results = {}
    
    # Run all tests
    results['input'] = test_input_module()
    results['hardware'] = test_hardware_module()
    results['vision'] = test_vision_module()
    results['security'] = test_security_module()
    results['database'] = test_database_module()
    results['api'] = test_api_server()
    results['integration'] = test_integration()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{module:20} {status}")
    
    print("="*60)
    print(f"Total: {passed}/{total} tests passed")
    print(f"Test completed at: {datetime.now().isoformat()}")
    
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
