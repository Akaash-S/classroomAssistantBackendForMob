#!/usr/bin/env python3
"""
Script to automatically set up Supabase storage policies for the lectures bucket
"""

import os
import sys
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_storage_policies():
    """Set up storage policies for the lectures bucket"""
    print("=== Setting up Supabase Storage Policies ===\n")
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials!")
        print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file")
        return False
    
    try:
        # Create Supabase client with service role key
        supabase: Client = create_client(supabase_url, service_key)
        print("OK Connected to Supabase")
        
        # Define the policies to create
        policies = [
            {
                "name": "Allow public uploads to lectures bucket",
                "sql": """
                CREATE POLICY IF NOT EXISTS "Allow public uploads to lectures bucket" ON storage.objects
                FOR INSERT WITH CHECK (bucket_id = 'lectures');
                """
            },
            {
                "name": "Allow public downloads from lectures bucket", 
                "sql": """
                CREATE POLICY IF NOT EXISTS "Allow public downloads from lectures bucket" ON storage.objects
                FOR SELECT USING (bucket_id = 'lectures');
                """
            },
            {
                "name": "Allow public updates to lectures bucket",
                "sql": """
                CREATE POLICY IF NOT EXISTS "Allow public updates to lectures bucket" ON storage.objects
                FOR UPDATE USING (bucket_id = 'lectures');
                """
            },
            {
                "name": "Allow public deletes from lectures bucket",
                "sql": """
                CREATE POLICY IF NOT EXISTS "Allow public deletes from lectures bucket" ON storage.objects
                FOR DELETE USING (bucket_id = 'lectures');
                """
            }
        ]
        
        print("Creating storage policies...")
        
        # Create each policy
        for policy in policies:
            try:
                print(f"Creating policy: {policy['name']}")
                # Note: Supabase Python client doesn't have direct SQL execution
                # This would need to be done via the REST API or SQL editor
                print(f"OK Policy '{policy['name']}' would be created")
            except Exception as e:
                print(f"WARNING Could not create policy '{policy['name']}': {e}")
        
        print("\nWARNING Note: The Python client doesn't support direct SQL execution.")
        print("Please run the following SQL in your Supabase SQL Editor:")
        print("\n" + "="*60)
        print("-- Enable RLS on storage.objects")
        print("ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;")
        print()
        print("-- Create policies for lectures bucket")
        for policy in policies:
            print(f"-- {policy['name']}")
            print(policy['sql'].strip())
            print()
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up policies: {e}")
        return False

def check_bucket_exists():
    """Check if the lectures bucket exists"""
    print("\n=== Checking Bucket Existence ===")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, service_key)
        
        # List buckets
        buckets = supabase.storage.list_buckets()
        bucket_names = [bucket.name for bucket in buckets] if buckets else []
        
        print(f"Existing buckets: {bucket_names}")
        
        if 'lectures' in bucket_names:
            print("OK Lectures bucket exists")
            return True
        else:
            print("ERROR Lectures bucket does not exist")
            print("Please create the 'lectures' bucket in your Supabase dashboard:")
            print("1. Go to Storage → New Bucket")
            print("2. Name: lectures")
            print("3. Make it public: ✅")
            print("4. Click Create bucket")
            return False
            
    except Exception as e:
        print(f"ERROR Error checking buckets: {e}")
        return False

def create_bucket_if_needed():
    """Create the lectures bucket if it doesn't exist"""
    print("\n=== Creating Bucket if Needed ===")
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing Supabase credentials!")
        return False
    
    try:
        supabase: Client = create_client(supabase_url, service_key)
        
        # Try to create the bucket
        print("Attempting to create 'lectures' bucket...")
        result = supabase.storage.create_bucket('lectures', options={'public': True})
        
        if result:
            print("OK Lectures bucket created successfully")
            return True
        else:
            print("WARNING Bucket creation result was empty")
            return False
            
    except Exception as e:
        if "already exists" in str(e).lower():
            print("OK Lectures bucket already exists")
            return True
        else:
            print(f"ERROR Error creating bucket: {e}")
            return False

def main():
    """Main function"""
    print("Supabase Storage RLS Policy Setup")
    print("="*50)
    
    # Check if bucket exists
    bucket_exists = check_bucket_exists()
    
    # Create bucket if needed
    if not bucket_exists:
        create_bucket_if_needed()
    
    # Set up policies
    setup_storage_policies()
    
    print("\n" + "="*60)
    print("📋 MANUAL STEPS REQUIRED:")
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run the SQL commands shown above")
    print("4. Or go to Storage → Policies and create them manually")
    print("5. Test with: python test_supabase.py")
    print("="*60)

if __name__ == "__main__":
    main()
