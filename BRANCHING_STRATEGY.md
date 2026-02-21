# Branch Strategy & Git Workflow

## Overview
This project uses a **feature branch workflow** with separate development branches for frontend and backend to prevent conflicts and maintain code isolation.

## Branch Structure

### Production Branches
- **master** - Production-ready code. Stable releases only. Protected branch.

### Development Branches
- **develop/backend** - Backend development (FastAPI/Python)
  - Base: All Python, API endpoints, database migrations, services
  - Team: Backend developers
  - PRs merge to master after testing
  
- **develop/frontend** - Frontend development (React/JavaScript)
  - Base: All React components, pages, styles, utilities
  - Team: Frontend developers
  - PRs merge to master after testing

## Why Separate Branches?

1. **Zero Merge Conflicts** - Frontend and backend teams work independently
2. **Clear Code Ownership** - Each team owns their branch
3. **Independent CI/CD** - Each branch can have its own deployment pipeline
4. **Easier Code Reviews** - Reviews focus on specific domain
5. **Parallel Development** - Teams can work simultaneously without blocking each other

## Directory Structure Alignment

### Backend Branch (develop/backend)
```
/backend
  /app
    /api       (API endpoints)
    /models    (Database models)
    /services  (Business logic)
    /schemas   (Data validation)
    /repositories  (Data access)
  /alembic   (Database migrations)
  requirements.txt
  Dockerfile
```

### Frontend Branch (develop/frontend)
```
/frontend
  /src
    /components   (React components)
    /pages        (Page components)
    /services     (API clients)
  package.json
  vite.config.js
  Dockerfile
```

## Workflow

### For Backend Developers
```bash
# Work on backend features
git checkout develop/backend
git pull origin develop/backend
git checkout -b feature/your-feature-name
# Make changes to /backend
git add backend/
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
# Create PR to develop/backend
# After approval and testing, PR is merged to develop/backend
```

### For Frontend Developers
```bash
# Work on frontend features
git checkout develop/frontend
git pull origin develop/frontend
git checkout -b feature/your-feature-name
# Make changes to /frontend
git add frontend/
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
# Create PR to develop/frontend
# After approval and testing, PR is merged to develop/frontend
```

## Commit Message Convention

Use conventional commits:
- `feat: Add new feature`
- `fix: Fix bug`
- `docs: Update documentation`
- `style: Code style changes`
- `refactor: Code refactoring`
- `test: Add tests`
- `chore: Maintenance tasks`

Example:
```
feat: Add user authentication endpoint
  
- Implement JWT token generation
- Add password hashing with bcrypt
- Create login endpoint at /auth/login
```

## Key Rules

1. ✅ Each branch is independent - **NO cross-branch dependencies**
2. ✅ Only commit changes to your respective folder (backend/ or frontend/)
3. ✅ Pull requests go to your development branch, not master
4. ✅ Master is only updated with stable, tested code
5. ✅ Feature branches are short-lived (typically 1-2 weeks max)
6. ✅ Always pull before pushing to avoid conflicts

## Protected Branches

- **master** - Requires at least 1 approval before merge
- **develop/backend** - Requires at least 1 approval before merge
- **develop/frontend** - Requires at least 1 approval before merge

## Integration Points

### Shared Files (Rarely Modified)
These files should trigger discussions before changes:
- `.env.example` - Environment variables
- `docker-compose.yml` - Orchestration
- `.gitignore` - Git configuration
- Root README.md - Project documentation

If you must modify these:
1. Create a feature branch from master
2. Make minimal changes
3. Get approval from both teams
4. Merge to master
5. Both teams pull latest master

## Releasing to Production

1. Test both develop/backend and develop/frontend thoroughly
2. Create release PRs from both branches to master
3. Code review and testing
4. Merge to master (fast-forward merge preferred)
5. Tag the release: `git tag -a v1.0.0 -m "Release version 1.0.0"`
6. Push tags: `git push origin --tags`

## Quick Reference

```bash
# Clone repository
git clone https://github.com/Shahzebsoomro1/Task-Management.git

# For Backend Development
git checkout develop/backend

# For Frontend Development
git checkout develop/frontend

# Create feature branch
git checkout -b feature/feature-name

# Push changes
git push origin feature/feature-name

# Create Pull Request on GitHub
```

---

**Last Updated**: February 21, 2026
**Maintainer**: Senior Developer
