# 🚨 QUICK FIX: Supabase RLS (Row Level Security) Issue

## **Problem**
```
ERROR Failed to save lecture: [Error: Failed to upload file to storage]
```

## **Root Cause**
Supabase storage buckets have Row Level Security (RLS) enabled by default, which blocks all operations unless explicit policies are created.

## **✅ IMMEDIATE SOLUTION**

### **Step 1: Go to Supabase Dashboard**
1. Open your Supabase project dashboard
2. Navigate to **SQL Editor** (in the left sidebar)

### **Step 2: Run This SQL Code**
Copy and paste this SQL code into the SQL Editor and click **"Run"**:

```sql
-- Enable RLS on storage.objects (if not already enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Create policies for the lectures bucket
CREATE POLICY IF NOT EXISTS "Allow public uploads to lectures bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'lectures');

CREATE POLICY IF NOT EXISTS "Allow public downloads from lectures bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'lectures');

CREATE POLICY IF NOT EXISTS "Allow public updates to lectures bucket" ON storage.objects
FOR UPDATE USING (bucket_id = 'lectures');

CREATE POLICY IF NOT EXISTS "Allow public deletes from lectures bucket" ON storage.objects
FOR DELETE USING (bucket_id = 'lectures');
```

### **Step 3: Verify Policies Were Created**
Run this query to check if the policies were created:

```sql
-- Check if policies were created
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';
```

You should see 4 policies listed for the `storage.objects` table.

### **Step 4: Test the Fix**
1. Start your backend: `python backend/app.py`
2. Try recording a lecture in the frontend
3. Check that the upload succeeds

## **Alternative: Using Storage Policies UI**

If you prefer using the UI:

### **Step 1: Go to Storage Policies**
1. In Supabase dashboard, go to **Storage** → **Policies**
2. Select the `lectures` bucket

### **Step 2: Create Policies Manually**
For each policy, click **"New Policy"** and create:

**Policy 1 - Upload:**
- Name: `Allow public uploads to lectures bucket`
- Operation: `INSERT`
- Target roles: `public`
- USING expression: `bucket_id = 'lectures'`

**Policy 2 - Download:**
- Name: `Allow public downloads from lectures bucket`
- Operation: `SELECT`
- Target roles: `public`
- USING expression: `bucket_id = 'lectures'`

**Policy 3 - Update:**
- Name: `Allow public updates to lectures bucket`
- Operation: `UPDATE`
- Target roles: `public`
- USING expression: `bucket_id = 'lectures'`

**Policy 4 - Delete:**
- Name: `Allow public deletes from lectures bucket`
- Operation: `DELETE`
- Target roles: `public`
- USING expression: `bucket_id = 'lectures'`

## **🧪 Test the Fix**

After creating the policies:

```bash
# Test environment
python backend/check_env.py

# Test Supabase connection
python backend/test_supabase.py

# Start backend
python backend/app.py
```

## **✅ Expected Results**

After setting up the policies:
- ✅ Storage test should show "Upload successful"
- ✅ Recording should upload to Supabase storage
- ✅ Files should appear in the `lectures` bucket
- ✅ Public URLs should be accessible

## **🔍 Troubleshooting**

### **Issue: "Permission denied"**
**Solution**: Check that the policies are created and enabled

### **Issue: "RLS policy violation"**
**Solution**: Verify the policy conditions match your bucket name

### **Issue: "Bucket not found"**
**Solution**: Make sure the `lectures` bucket exists and is public

## **📋 Quick Checklist**

- [ ] Supabase project is active
- [ ] `lectures` bucket exists and is public
- [ ] RLS policies are created for the bucket
- [ ] Backend environment variables are set
- [ ] Test upload works

## **🎯 Why This Happens**

Supabase enables Row Level Security by default on storage buckets to prevent unauthorized access. Without explicit policies, all operations are blocked, which is why the upload fails with "Failed to upload file to storage".

The policies we create allow public access to the `lectures` bucket specifically, which is what we need for the recording functionality to work.

## **🔒 Security Note**

The policies above make the `lectures` bucket completely public. For production, consider more restrictive policies based on user authentication.

---

**This should resolve the RLS issue and allow audio uploads to work properly!** 🎉
