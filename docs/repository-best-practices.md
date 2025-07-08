# 📋 National Document Repository - Best Practices Guide

## Table of Contents

1. [Project Structure & Organization](#1-project-structure--organization)
2. [Version Control & Branching](#2-version-control--branching)
3. [Documentation Standards](#3-documentation-standards)
4. [Development Environment](#4-development-environment)
5. [Testing Practices](#5-testing-practices)
6. [Code Quality & Formatting](#6-code-quality--formatting)
7. [Build & Deployment](#7-build--deployment)
8. [Security Best Practices](#8-security-best-practices)
9. [Monitoring & Alerts](#9-monitoring--alerts)
10. [Makefile Commands Reference](#10-makefile-commands-reference)
11. [Git Workflow](#11-git-workflow)
12. [Team Collaboration](#14-team-collaboration)

## 1. Project Structure & Organization

```
📁 Repository Structure:
├── 📄 README.md (Main documentation entry point)
├── 📁 app/ (React frontend application)
│   ├── 📄 README.md (UI-specific documentation)
│   ├── 📁 src/ (Source code)
│   └── 📁 cypress/ (E2E tests)
├── 📁 lambdas/ (AWS Lambda functions)
│   ├── 📄 README.md (Lambda-specific documentation)
│   ├── 📁 handlers/ (Lambda entry points)
│   ├── 📁 services/ (Business logic)
│   ├── 📁 repositories/ (Data access layer)
│   ├── 📁 models/ (Data models)
│   ├── 📁 utils/ (Shared utilities)
│   └── 📁 tests/ (Unit tests)
├── 📁 docs/ (API specs and process documentation)
├── 📁 tests/ (Integration/bulk upload tests)
└── 📁 .github/workflows/ (CI/CD pipelines)
```

## 2. Version Control & Branching

- **Branch Naming**: Name branches after ticket IDs (e.g., `PRME-54`, `NDR-100`, `PRM-300`)
- **Commit Messages**: Use format `[TICKET-ID] Description` (e.g., `[PRMT-435] Stitching manual trigger doesn't add all records to queue`)
- **Main Branch**: Keep `main` as the primary branch with protection rules
- **Feature Branches**: Create from main, merge via PR after reviews

## 3. Documentation Standards

- **API Documentation**: Maintain in `docs/` directory
- **Process Documentation**: Include flow diagrams and authentication processes

## 4. Development Environment

- **Python Version**: Standardise on Python 3.11 for Lambda functions
- **Node Version**: Use Node@24 for React application
- **Virtual Environments**: Use `make env` for consistent Python environments
- **Package Management**:
  - Python: Use requirements files with version pinning
  - Node: Use npm with `--legacy-peer-deps` flag

## 5. Testing Practices

```makefile
# Unit Testing
make test-unit           # Run all unit tests
make test-unit-coverage  # Generate coverage reports

# UI Testing
make test-ui            # Run Vitest tests
make cypress-run        # Run Cypress E2E tests
make cypress-open       # Open Cypress interactive mode
```

## 6. Code Quality & Formatting

**Linting Configuration**

- Use ruff for Python linting
- ESLint for JavaScript/TypeScript
- Prettier for consistent formatting

```makefile
# Python Code Quality
make format             # Auto-format with isort, black, and ruff
make check-packages     # Security audit with pip-audit
```

## 7. Build & Deployment

- **Lambda Layers**: Apply SOLID Principles and Separate conern, core, data, and reports requirements
- **CI/CD**: Leverage GitHub Actions and AWS sandbox enviroments

## 8. Security Best Practices

- **Secrets Management**: Never commit secrets, use AWS Systems Manager
- **Dependency Scanning**: Regular `make check-packages` runs
- **.gitignore**: Comprehensive exclusions for sensitive/generated files
- **Access Control**: Use AWS IAM roles and policies

## 9. Monitoring & Alerts

- **CloudWatch Integration**: Set up alarms for critical metrics
- **SNS Notifications**: Subscribe to alerts via email
- **Logging Standards**: Structured logging in Lambda functions

## 10. Makefile Commands Reference

```bash
# Environment Setup
make env                # Setup Python virtual environment
make clean              # Clean all generated files

# Development
make format             # Format all Python code
make sort-requirements  # Sort requirements files

# Testing
make test-unit          # Run unit tests
make test-ui            # Run UI tests
make cypress-run        # Run E2E tests
```

## 11. Git Workflow

### Feature Development

```bash
git checkout -b TICKET-123-feature-description
# Make changes
git commit -m "[TICKET-123] Add new feature"
git push origin TICKET-123-feature-description
```

## 12. Team Collaboration

- **Code Reviews**: Require at least one approval before merging
- **Knowledge Sharing**: Document complex logic and decisions
- **Pair Programming**: For complex features or bug fixes
- **Regular Syncs**: Team meetings to discuss architecture changes

---

## Additional Guidelines

### Error Handling

- Implement comprehensive error handling in Lambda functions
- Use structured error responses
- Log errors with appropriate context

### Testing Strategy

- Aim for >80% code coverage
- Write tests for edge cases
- Include integration tests for critical paths

### Performance Monitoring

- Set up performance budgets
- Monitor Lambda execution times
- Track API response times

### Documentation Updates

- Update documentation with code changes
- Include examples in API documentation
- Keep README files current
