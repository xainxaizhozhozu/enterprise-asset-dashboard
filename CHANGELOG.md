# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [v1.3.0] - 2026-07-30

### Bug Fixes
- **WAL mode**: Enabled SQLite WAL (Write-Ahead Logging) mode to resolve concurrent write conflicts and improve database reliability under load
- **Function Calling error handling**: Added robust error handling for OpenAI Function Calling responses, preventing crashes on malformed or unexpected tool call results
- **is_active enforcement**: Fixed inactive user accounts still being able to authenticate; the `is_active` flag is now strictly enforced at the login endpoint

## [v1.2.0] - 2026-07-30

### Security
- **JWT secret hardening**: Replaced hardcoded JWT secret with environment-variable-based configuration; enforced minimum secret length and added startup validation
- **API key cleanup**: Removed accidentally committed API keys and secrets from source history; added `.env` to `.gitignore` and scrubbed sensitive data from logs

## [v1.1.0] - 2026-07-30

### Added
- **RBAC (Role-Based Access Control)**: Implemented three-tier role system (admin / manager / viewer) with granular endpoint-level permission checks
- **Audit logging**: Added comprehensive audit trail for all asset mutations (create, update, delete, status change) with user and timestamp attribution
- **OpenAI Function Calling**: Integrated AI-powered natural language asset queries via OpenAI Function Calling, allowing users to ask questions like "show all overdue assets"
- **MIT License**: Project released under the MIT License

## [v1.0.0] - 2026-07-30

### Initial Release
- Enterprise asset and permission management dashboard
- FastAPI backend with async SQLAlchemy ORM
- Vue 3 + Vite frontend with responsive UI
- AI-assisted audit capabilities via OpenAI integration
- SQLite persistence with seed data
- JWT-based authentication
- Docker and CI/CD infrastructure

[v1.3.0]: https://github.com/your-org/dashboard/compare/v1.2.0...v1.3.0
[v1.2.0]: https://github.com/your-org/dashboard/compare/v1.1.0...v1.2.0
[v1.1.0]: https://github.com/your-org/dashboard/compare/v1.0.0...v1.1.0
[v1.0.0]: https://github.com/your-org/dashboard/releases/tag/v1.0.0
