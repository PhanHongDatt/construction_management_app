from construction_management.setup.custom_fields import create_construction_custom_fields
from construction_management.setup.roles import create_construction_roles


def after_migrate() -> None:
    """Run after every bench migrate. Must be idempotent."""
    create_construction_roles()
    create_construction_custom_fields()
