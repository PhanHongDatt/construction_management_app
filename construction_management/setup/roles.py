import frappe

ROLES = [
    "Construction Administrator",
    "Construction Project Director",
    "Construction Project Manager",
    "Construction Site Manager",
    "Construction Site Engineer",
    "Construction Quantity Surveyor",
    "Construction Procurement Officer",
    "Construction Accountant",
    "Construction Contractor User",
]


def create_construction_roles() -> None:
    """Create all Construction roles. Idempotent — safe to call multiple times."""
    for role_name in ROLES:
        if frappe.db.exists("Role", role_name):
            continue
        frappe.get_doc(
            {"doctype": "Role", "role_name": role_name}
        ).insert(ignore_permissions=True)
    frappe.db.commit()
