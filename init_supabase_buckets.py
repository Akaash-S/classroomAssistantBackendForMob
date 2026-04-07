"""
Initialize Supabase Storage Buckets.
Creates the required buckets: lectures, images, documents.
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_KEY')

BUCKETS = [
    {"name": "lectures", "public": True},
    {"name": "images", "public": True},
    {"name": "documents", "public": True},
]

def main():
    print("=" * 50)
    print("Supabase Bucket Initialization")
    print("=" * 50)

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("[FAIL] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY/SUPABASE_KEY in .env")
        return

    print(f"\nURL: {SUPABASE_URL}")
    print(f"Key: ...{SUPABASE_SERVICE_KEY[-8:]}")

    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("[OK] Supabase client initialized\n")
    except Exception as e:
        print(f"[FAIL] Failed to initialize client: {e}")
        return

    # List existing buckets
    existing_names = []
    try:
        existing = client.storage.list_buckets()
        for b in existing:
            name = b.name if hasattr(b, 'name') else b.get('name', str(b))
            existing_names.append(name)
        print(f"Existing buckets: {existing_names}\n")
    except Exception as e:
        print(f"[WARN] Could not list buckets: {e}")

    # Create missing buckets
    for bucket in BUCKETS:
        name = bucket["name"]
        is_public = bucket["public"]

        if name in existing_names:
            print(f"  [OK] Bucket '{name}' already exists")
            continue

        try:
            client.storage.create_bucket(
                name,
                options={"public": is_public}
            )
            print(f"  [OK] Created bucket '{name}' (public={is_public})")
        except Exception as e:
            err_str = str(e)
            if "already exists" in err_str.lower():
                print(f"  [OK] Bucket '{name}' already exists")
            else:
                print(f"  [FAIL] Failed to create bucket '{name}': {e}")

    # Verify
    print("\n--- Verification ---")
    try:
        final_buckets = client.storage.list_buckets()
        for b in final_buckets:
            name = b.name if hasattr(b, 'name') else b.get('name', str(b))
            is_public = b.public if hasattr(b, 'public') else b.get('public', '?')
            print(f"  - {name} (public={is_public})")
        print(f"\nTotal: {len(final_buckets)} bucket(s)")
    except Exception as e:
        print(f"  [FAIL] Verification failed: {e}")

    print("\n" + "=" * 50)
    print("Done!")

if __name__ == "__main__":
    main()
