-- Step 1: Define the concept
-- Title: TaskMaster Pro - A collaborative task management tool for teams
-- One-line pitch: Organize, track, and collaborate on tasks efficiently with TaskMaster Pro, where every user's tasks stay secure and private.

-- Step 2: SQL code to create the necessary table with RLS policies

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create users table (if it doesn't exist, typically this would be part of your authentication setup)
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Step 3: Enable Row Level Security on tasks table
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- Step 4: Create RLS policy to allow users to view only their tasks
CREATE POLICY "select_own_tasks"
    ON tasks
    FOR SELECT
    USING (user_id = auth.uid());

-- Step 5: Create RLS policy to allow users to insert their tasks
CREATE POLICY "insert_own_tasks"
    ON tasks
    FOR INSERT
    WITH CHECK (user_id = auth.uid());

-- Step 6: Create RLS policy to allow users to update their tasks
CREATE POLICY "update_own_tasks"
    ON tasks
    FOR UPDATE
    USING (user_id = auth.uid());

-- Step 7: Create RLS policy to allow users to delete their tasks
CREATE POLICY "delete_own_tasks"
    ON tasks
    FOR DELETE
    USING (user_id = auth.uid());

-- Note: Make sure the current user is set correctly in Supabase to match the auth.uid() function for RLS policies to work properly.