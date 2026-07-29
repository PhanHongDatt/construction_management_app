# Construction Management

Custom Frappe app extending ERPNext for Construction project management.

## Features

- Custom fields on Project, Task, Supplier for construction workflows
- Domain-specific DocTypes: Work Package, Site Daily Report, Progress Acceptance, Contractor Payment Request
- Vietnamese translation (vi)
- Role-based permissions aligned to construction hierarchy
- Server-side validation for quantities and payment amounts
- Three approval workflows (Daily Report, Acceptance, Payment)

## Requirements

- Frappe `version-16`
- ERPNext `version-16`
- Python 3.11+

## Installation

```bash
# In frappe-bench directory
bench get-app --branch main https://github.com/<your-org>/construction_management
bench --site <your-site> install-app construction_management
```

## Development Setup

See [.devcontainer/](../../.devcontainer/) for Docker-based development environment.

```bash
# Start dev container (VS Code)
code .
# Then: Reopen in Container

# Or using Docker directly
docker compose -f .devcontainer/docker-compose.yml up -d
```

## Build & Deploy

```bash
# From project root
make app-build        # Build Docker image
make app-deploy       # Deploy to RKE2
make app-migrate      # Run bench migrate in cluster
make app-seed         # Seed demo data
make app-verify       # Run acceptance tests
```

## Version

See [image/versions.env](../image/versions.env) for pinned Frappe/ERPNext versions.
