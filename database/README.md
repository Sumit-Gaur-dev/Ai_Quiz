# AI Quiz Platform — Database

Supabase PostgreSQL database migrations and schema.

## Overview

This directory contains SQL migration files for the Supabase PostgreSQL database, including table schemas, triggers, and Row Level Security (RLS) policies.

## Structure

```
database/
├── migrations/
│   ├── 001_create_profiles.sql  # Profiles table, RLS policies, and auth.users trigger
│   └── ...
└── README.md
```

## Database Setup Instructions

### Option 1: Supabase Dashboard (SQL Editor)

1. Open your Supabase project dashboard at [https://supabase.com/dashboard](https://supabase.com/dashboard).
2. Navigate to the **SQL Editor** from the left sidebar.
3. Open `database/migrations/001_create_profiles.sql`.
4. Copy and paste the entire script into the SQL editor and click **Run**.
5. Verify in **Table Editor** that the `public.profiles` table is created and **RLS is enabled** (indicated by the shield icon).

### Option 2: Supabase CLI (Local or Remote)

If you use the Supabase CLI:

```bash
# Link your local project to your remote Supabase project
supabase link --project-ref your-project-ref

# Apply pending migrations
supabase db push
```

## Security Invariants

- **Row Level Security (RLS)** is strictly enabled on `public.profiles`.
- Users can only `SELECT`, `UPDATE`, and `INSERT` their own record matching `auth.uid() = id`.
- Automatic profile creation runs with `SECURITY DEFINER` scoped to the `public.handle_new_user()` function triggered on `auth.users` insert.
- **Never disable RLS** to circumvent authentication or authorization checks.
