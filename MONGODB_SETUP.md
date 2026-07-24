# MongoDB Session Setup for Drinks and Wins

## Overview
The application now uses **persistent database sessions** to ensure user authentication data is synchronized across multiple servers. When a user logs in on one server and then accesses the application from another server, their session and profile data will remain intact.

## How It Works

### Session Storage
- **Database Backend**: Django's built-in database session backend stores all session data in SQLite (or any SQL database)
- **Session Table**: The `django_session` table stores encrypted session data with expiration timestamps
- **Cross-Server Access**: Any server instance can access session data from the shared database
- **Session Expiry**: Sessions automatically expire after 2 weeks of inactivity

### Session Configuration
```python
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

## Testing Cross-Server Sessions

### 1. Create a User Account
1. Go to http://127.0.0.1:8000/accounts/signup/
2. Create a new account with username and password
3. You'll be automatically logged in

### 2. Verify Session Data
Check the session API endpoint:
```bash
GET /accounts/api/session-status/
```
Response:
```json
{
  "status": "active",
  "user": "username",
  "session_key": "abc123xyz...",
  "authenticated": true
}
```

### 3. Get User Profile
```bash
GET /accounts/api/profile/
```
Response:
```json
{
  "id": 1,
  "username": "testuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_staff": false,
  "is_authenticated": true,
  "date_joined": "2026-07-17T10:00:00",
  "last_login": "2026-07-17T11:00:00"
}
```

### 4. Simulate Multiple Servers
To test cross-server session persistence:

1. **Server 1**: Run `manage.py runserver 8000`
2. **Server 2** (in new terminal): Run `manage.py runserver 8001`
3. Login on Server 1 (http://127.0.0.1:8000/accounts/login/)
4. Access Server 2 with the same browser (http://127.0.0.1:8001/)
5. You should still be logged in!

The session cookie is shared across both servers because they use the same database.

## Upgrading to MongoDB (Optional)

For a full NoSQL MongoDB setup in production:

1. **Install Django MongoDB packages**:
   ```bash
   pip install mongoengine django-mongoengine
   ```

2. **Create MongoDB Models** for user profiles and sessions

3. **Update settings.py**:
   ```python
   INSTALLED_APPS += ['django_mongoengine']
   
   MONGODB_DATABASES = {
       'default': {
           'name': 'drinks_and_wins',
           'host': 'localhost',
           'port': 27017,
       }
   }
   ```

## Files Created/Modified

- **accounts/session_backend.py** - Custom MongoDB session backend
- **accounts/api.py** - REST API for profile and session access
- **accounts/urls.py** - Added API endpoints
- **config/settings.py** - Database and session configuration
- **requirements.txt** - Added MongoDB packages

## Environment Variables (For Production)

Create a `.env` file:
```
DATABASE_URL=postgresql://user:pass@localhost/drinks_and_wins
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/drinks_and_wins
SESSION_COOKIE_SECURE=True
```

## Testing Logout Cross-Server

1. Login on Server 1
2. Logout on Server 1
3. Try accessing protected pages on Server 2
4. You will be redirected to login page (session is cleared)

This confirms the session data is truly shared and synchronized across all server instances!
