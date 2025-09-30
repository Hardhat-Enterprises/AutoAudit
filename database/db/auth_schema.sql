-- =========================================================
-- AutoAudit - Database Authentication (Auth Schema)
-- Author: Sai Tejaswini
-- Purpose: Sign-up, sign-in, refresh token lifecycle
-- =========================================================

CREATE SCHEMA IF NOT EXISTS auth;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users table
CREATE TABLE IF NOT EXISTS auth.users (
  id            SERIAL PRIMARY KEY,
  email         TEXT NOT NULL UNIQUE,
  password      TEXT NOT NULL,
  first_name    TEXT NOT NULL,
  last_name     TEXT NOT NULL,
  last_login_at TIMESTAMPTZ,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Refresh/session tokens
CREATE TABLE IF NOT EXISTS auth.refresh_tokens (
  id         SERIAL PRIMARY KEY,
  user_id    INT NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  token      TEXT NOT NULL,
  issued_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ
);

-- ============== Example flows ==============

-- Register new user
WITH new_user AS (
  INSERT INTO auth.users (email, password, first_name, last_name)
  VALUES (
    'sai@gmail.com',
    crypt('Pass@123', gen_salt('bf', 12)),
    'Sai', 'Gajji'
  )
  RETURNING id
)
SELECT id AS registered_user_id FROM new_user;

-- Verify login
WITH candidate AS (
  SELECT id
  FROM auth.users
  WHERE email = 'sai@gmail.com'
    AND password = crypt('Pass@123', password)
)
SELECT id AS logged_in_user_id FROM candidate;

-- Update last login
UPDATE auth.users
SET last_login_at = now(), updated_at = now()
WHERE email = 'sai@gmail.com';

-- Issue refresh token
WITH u AS (
  SELECT id FROM auth.users WHERE email = 'sai@gmail.com'
), tg AS (
  SELECT encode(gen_random_bytes(24), 'hex') AS new_token
)
INSERT INTO auth.refresh_tokens (user_id, token, expires_at)
SELECT u.id, tg.new_token, now() + interval '60 days'
FROM u, tg
RETURNING token AS my_session_token, issued_at, expires_at;

-- Validate token
SELECT user_id
FROM auth.refresh_tokens
WHERE token = '<TOKEN_HERE>'
  AND revoked_at IS NULL
  AND expires_at > now();

-- Revoke token (logout)
UPDATE auth.refresh_tokens
SET revoked_at = now()
WHERE token = '<TOKEN_HERE>' AND revoked_at IS NULL;
