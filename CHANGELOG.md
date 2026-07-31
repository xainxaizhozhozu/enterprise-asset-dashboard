# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.5.0] - 2026-08-01

### Added
- **AuthContext**: Extracted auth state management into `contexts/AuthContext.jsx` (JWT validation, login/logout, localStorage sync)
- **useApi hook**: Generic async API wrapper with loading/error/data state (`hooks/useApi.js`)
- **Component splitting**: Dashboard.jsx split into 5 components (417→76 lines): Sidebar, OverviewTab, AssetsTab, AuditTab, AuditLogsTab
- **Shared constants**: `components/constants.js` for role labels, category labels, status maps, chart colors

### Changed
- **useApi integration**: Dashboard and AuditLogsTab now use `useApi` hook instead of manual loading/error state management
- **App.jsx simplified**: Auth logic delegated to `AuthProvider`, route logic to `AppRoutes` component using `useAuth()`

### Previous releases

## [v1.3.0] - 2026-07-30

### Bug Fixes
- **WAL mode**: Enabled SQLite WAL mode for concurrent write reliability
- **Function Calling**: Robust error handling for OpenAI Function Calling responses
- **is_active enforcement**: Inactive accounts blocked from authentication

## [v1.2.0] - 2026-07-30

### Security
- **JWT secret hardening**: Environment-variable-based configuration with startup validation
- **API key cleanup**: Removed committed secrets from source history

## [v1.1.0] - 2026-07-30

### Added
- RBAC (admin / manager / viewer), audit logging, OpenAI Function Calling, MIT License

## [v1.0.0] - 2026-07-30

### Initial Release
- Enterprise asset and permission management dashboard
- FastAPI backend with async SQLAlchemy ORM
- React + Vite frontend with responsive UI
- AI-assisted audit capabilities via OpenAI integration
- JWT-based authentication, Docker and CI/CD infrastructure
