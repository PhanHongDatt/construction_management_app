import frappe

from construction_management.setup.custom_fields import create_construction_custom_fields
from construction_management.setup.roles import create_construction_roles


def after_install() -> None:
    """Run once after app installation. Must be idempotent."""
    create_construction_roles()
    create_construction_custom_fields()
    set_system_defaults()


def set_system_defaults() -> None:
    """Set system-wide defaults for construction use."""
    frappe.db.set_single_value("System Settings", "language", "vi")
    frappe.db.set_single_value("System Settings", "time_zone", "Asia/Ho_Chi_Minh")
    frappe.db.commit()
