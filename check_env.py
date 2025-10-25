#!/usr/bin/env python3
"""
Environment variable checker for the backend
"""

import os
import sys

def check_env_vars():
    """Check all required environment variables"""
    print("Checking Environment Variables\n")
    
    # Required variables
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    # Optional variables
    optional_vars = [
        'SUPABASE_SERVICE_KEY',
        'GEMINI_API_KEY',
        'FLASK_ENV'
    ]
    
    print("=== Required Variables ===")
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"OK {var}: {masked_value}")
            else:
                print(f"OK {var}: {value}")
        else:
            print(f"ERROR {var}: Not set")
            missing_required.append(var)
    
    print("\n=== Optional Variables ===")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var:
                masked_value = value[:8] + '...' if len(value) > 8 else '***'
                print(f"OK {var}: {masked_value}")
            else:
                print(f"OK {var}: {value}")
        else:
            print(f"WARNING {var}: Not set (optional)")
    
    print("\n=== Summary ===")
    if missing_required:
        print(f"ERROR: Missing {len(missing_required)} required variables:")
        for var in missing_required:
            print(f"   - {var}")
        print("\nPlease set these environment variables before running the backend.")
        return False
    else:
        print("SUCCESS: All required environment variables are set!")
        return True

if __name__ == "__main__":
    success = check_env_vars()
    sys.exit(0 if success else 1)
