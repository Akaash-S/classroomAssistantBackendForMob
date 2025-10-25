# 🔒 Supabase RLS (Row Level Security) Fix

## **Problem Identified**
The audio upload fails because Supabase storage buckets have Row Level Security (RLS) enabled by default, which blocks all operations unless proper policies are configured.

## **Solution: Configure Storage Policies**

### **Method 1: Using Supabase Dashboard (Recommended)**

#### **Step 1: Access Storage Policies**
1. Go to your Supabase project dashboard
2. Navigate to **Storage** → **Policies**
3. Select the `lectures` bucket

#### **Step 2: Create Upload Policy**
1. Click **"New Policy"**
2. Choose **"For full customization"**
3. Enter the following policy:

**Policy Name**: `Allow public uploads to lectures bucket`

**Policy Definition**:
```sql
CREATE POLICY "Allow public uploads to lectures bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'lectures');
```

#### **Step 3: Create Download Policy**
1. Click **"New Policy"** again
2. Choose **"For full customization"**
3. Enter the following policy:

**Policy Name**: `Allow public downloads from lectures bucket`

**Policy Definition**:
```sql
CREATE POLICY "Allow public downloads from lectures bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'lectures');
```

#### **Step 4: Create Update Policy (Optional)**
1. Click **"New Policy"** again
2. Choose **"For full customization"**
3. Enter the following policy:

**Policy Name**: `Allow public updates to lectures bucket`

**Policy Definition**:
```sql
CREATE POLICY "Allow public updates to lectures bucket" ON storage.objects
FOR UPDATE USING (bucket_id = 'lectures');
```

#### **Step 5: Create Delete Policy (Optional)**
1. Click **"New Policy"** again
2. Choose **"For full customization"**
3. Enter the following policy:

**Policy Name**: `Allow public deletes from lectures bucket`

**Policy Definition**:
```sql
CREATE POLICY "Allow public deletes from lectures bucket" ON storage.objects
FOR DELETE USING (bucket_id = 'lectures');
```

### **Method 2: Using SQL Editor**

#### **Step 1: Open SQL Editor**
1. Go to **SQL Editor** in your Supabase dashboard
2. Click **"New Query"**

#### **Step 2: Run the Following SQL**
```sql
-- Enable RLS on storage.objects (if not already enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Create policies for the lectures bucket
CREATE POLICY "Allow public uploads to lectures bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'lectures');

CREATE POLICY "Allow public downloads from lectures bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'lectures');

CREATE POLICY "Allow public updates to lectures bucket" ON storage.objects
FOR UPDATE USING (bucket_id = 'lectures');

CREATE POLICY "Allow public deletes from lectures bucket" ON storage.objects
FOR DELETE USING (bucket_id = 'lectures');
```

### **Method 3: Using Service Role Key (Programmatic)**

If you want to handle this programmatically, you can use the service role key to create policies:

```python
# This would go in your backend setup script
import os
from supabase import create_client

def setup_storage_policies():
    """Set up storage policies programmatically"""
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("Missing Supabase credentials")
        return False
    
    # Create client with service role key
    supabase = create_client(supabase_url, service_key)
    
    # SQL to create policies
    policies_sql = """
    -- Enable RLS on storage.objects
    ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;
    
    -- Create policies for lectures bucket
    CREATE POLICY IF NOT EXISTS "Allow public uploads to lectures bucket" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'lectures');
    
    CREATE POLICY IF NOT EXISTS "Allow public downloads from lectures bucket" ON storage.objects
    FOR SELECT USING (bucket_id = 'lectures');
    
    CREATE POLICY IF NOT EXISTS "Allow public updates to lectures bucket" ON storage.objects
    FOR UPDATE USING (bucket_id = 'lectures');
    
    CREATE POLICY IF NOT EXISTS "Allow public deletes from lectures bucket" ON storage.objects
    FOR DELETE USING (bucket_id = 'lectures');
    """
    
    try:
        # Execute the SQL
        result = supabase.rpc('exec_sql', {'sql': policies_sql})
        print("Storage policies created successfully")
        return True
    except Exception as e:
        print(f"Error creating policies: {e}")
        return False
```

## **Alternative: Disable RLS (Less Secure)**

If you want to disable RLS entirely for the storage bucket (less secure but simpler):

```sql
-- Disable RLS on storage.objects
ALTER TABLE storage.objects DISABLE ROW LEVEL SECURITY;
```

**⚠️ Warning**: This makes your storage bucket completely public. Only use this for development/testing.

## **Verification Steps**

### **1. Check Policies in Dashboard**
1. Go to **Storage** → **Policies**
2. Verify you see the policies for the `lectures` bucket
3. Make sure they're **enabled**

### **2. Test Upload**
```bash
# Run the Supabase test
python backend/test_supabase.py
```

### **3. Test Recording**
1. Start the backend: `python backend/app.py`
2. Try recording a lecture in the frontend
3. Check that the upload succeeds

## **Expected Results**

After setting up the policies:
- ✅ Storage test should show "Upload successful"
- ✅ Recording should upload to Supabase storage
- ✅ Files should appear in the `lectures` bucket
- ✅ Public URLs should be accessible

## **Troubleshooting**

### **Issue: "Permission denied"**
**Solution**: Check that the policies are created and enabled

### **Issue: "RLS policy violation"**
**Solution**: Verify the policy conditions match your bucket name

### **Issue: "Bucket not found"**
**Solution**: Make sure the `lectures` bucket exists and is public

## **Security Notes**

- The policies above make the `lectures` bucket completely public
- For production, consider more restrictive policies based on user authentication
- You can add user-based policies if you implement proper authentication

## **Quick Fix Commands**

```sql
-- Run this in Supabase SQL Editor
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public uploads to lectures bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'lectures');

CREATE POLICY "Allow public downloads from lectures bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'lectures');
```

This should resolve the RLS issue and allow audio uploads to work properly! 🎉
