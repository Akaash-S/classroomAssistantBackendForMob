#!/usr/bin/env python3
"""
Test script for Supabase Storage Service
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.supabase_storage import SupabaseStorageService

def test_supabase_service():
    """Test the Supabase Storage Service"""
    print("Testing Supabase Storage Service...")
    
    # Check environment variables
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_KEY: {os.getenv('SUPABASE_KEY')[:20] + '...' if os.getenv('SUPABASE_KEY') else 'None'}")
    print(f"SUPABASE_SERVICE_KEY: {os.getenv('SUPABASE_SERVICE_KEY')[:20] + '...' if os.getenv('SUPABASE_SERVICE_KEY') else 'None'}")
    
    # Initialize service
    service = SupabaseStorageService()
    
    print(f"Service URL: {service.supabase_url}")
    print(f"Service Available: {service.is_available()}")
    
    if service.is_available():
        print("SUPABASE SERVICE IS WORKING!")
        
        # Test bucket creation
        print("\nTesting bucket creation...")
        bucket_name = "lecture-audio"
        success = service.create_bucket(bucket_name, is_public=True)
        print(f"Bucket '{bucket_name}' creation: {'SUCCESS' if success else 'FAILED'}")
        
        # List buckets
        print("\nListing buckets...")
        buckets = service.list_buckets()
        if buckets:
            print("Available buckets:")
            for bucket in buckets:
                print(f"  - {bucket}")
        else:
            print("No buckets found or error listing buckets")
            
    else:
        print("SUPABASE SERVICE IS NOT AVAILABLE")
        print("Check your environment variables and Supabase configuration")

if __name__ == "__main__":
    test_supabase_service()
