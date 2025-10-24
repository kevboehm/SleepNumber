# Environment Variables

This document describes all environment variables used in the SleepNumber Automation webapp.

## Backend Environment Variables

### Required Variables

- **`SECRET_KEY`**: Flask secret key for session management
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Example: `a1b2c3d4e5f6...`

- **`JWT_SECRET_KEY`**: Secret key for JWT token signing
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Example: `x1y2z3a4b5c6...`

- **`ENCRYPTION_KEY`**: Key for encrypting SleepNumber credentials
  - Generate with: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
  - Example: `gAAAAABh...`

### Optional Variables

- **`FLASK_ENV`**: Flask environment mode
  - Values: `development` | `production`
  - Default: `development`

- **`PORT`**: Port for the Flask application
  - Default: `5000`

- **`ADMIN_PASSWORD`**: Default admin password
  - Default: `admin123`
  - **Change this in production!**

- **`DATABASE_URL`**: Database connection URL (for production)
  - Format: `postgresql://user:password@host:port/database`
  - Default: SQLite database file

## Frontend Environment Variables

### Required Variables

- **`REACT_APP_API_URL`**: Backend API URL
  - Development: `http://localhost:5000/api`
  - Production: `https://your-backend-url.com/api`

## Production Deployment

### Render.com Backend

Set these environment variables in your Render.com service:

```bash
FLASK_ENV=production
SECRET_KEY=<generate-secure-key>
JWT_SECRET_KEY=<generate-secure-key>
ENCRYPTION_KEY=<generate-fernet-key>
ADMIN_PASSWORD=<secure-password>
DATABASE_URL=<postgresql-url-from-render>
```

### Vercel Frontend

Set this environment variable in your Vercel project:

```bash
REACT_APP_API_URL=https://your-render-backend-url.onrender.com/api
```

## Security Notes

1. **Never commit environment variables to version control**
2. **Use strong, randomly generated keys in production**
3. **Rotate keys periodically**
4. **Use different keys for different environments**
5. **Store production keys securely (use your platform's secret management)**

## Key Generation Commands

```bash
# Generate Flask secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Generate secure password
python -c "import secrets; import string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16)))"
```
