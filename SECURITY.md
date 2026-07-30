# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please do NOT open a public GitHub issue.

Instead, email us at **ck20060210@qq.com** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact

We will acknowledge receipt within 48 hours and provide a detailed response within 7 days.

## Security Measures

- JWT authentication with configurable secret key (required via environment variable)
- bcrypt password hashing for all user credentials
- Role-Based Access Control (RBAC) with admin/manager/viewer roles
- Disabled accounts are rejected immediately on every authenticated request
- OpenAI Function Calling with timeout and rate limit handling
- SQLite WAL mode for concurrent write safety
- Environment variables (.env) excluded from version control
- Global exception handler prevents internal error exposure

## Best Practices for Deployment

- Generate a strong random `SECRET_KEY` (at least 32 bytes)
- Set `CORS_ORIGINS` to your specific frontend domain(s)
- Use HTTPS in production (configure via reverse proxy)
- Rotate JWT tokens periodically; current expiry is 8 hours
- Run behind a reverse proxy with rate limiting
- Back up the SQLite database file regularly
