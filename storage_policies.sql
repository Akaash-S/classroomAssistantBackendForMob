-- Supabase Storage RLS Policies for Lectures Bucket
-- Run this SQL in your Supabase SQL Editor

-- Enable RLS on storage.objects (if not already enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Create policies for the lectures bucket
-- Policy 1: Allow public uploads to lectures bucket
CREATE POLICY IF NOT EXISTS "Allow public uploads to lectures bucket" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'lectures');

-- Policy 2: Allow public downloads from lectures bucket
CREATE POLICY IF NOT EXISTS "Allow public downloads from lectures bucket" ON storage.objects
FOR SELECT USING (bucket_id = 'lectures');

-- Policy 3: Allow public updates to lectures bucket
CREATE POLICY IF NOT EXISTS "Allow public updates to lectures bucket" ON storage.objects
FOR UPDATE USING (bucket_id = 'lectures');

-- Policy 4: Allow public deletes from lectures bucket
CREATE POLICY IF NOT EXISTS "Allow public deletes from lectures bucket" ON storage.objects
FOR DELETE USING (bucket_id = 'lectures');

-- Verify policies were created
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual 
FROM pg_policies 
WHERE tablename = 'objects' AND schemaname = 'storage';
