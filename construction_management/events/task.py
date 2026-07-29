import frappe
from frappe import _


def validate_task(doc, method=None) -> None:
    """Server-side validation for Task with construction custom fields."""
    planned = float(doc.custom_planned_quantity or 0)
    completed = float(doc.custom_completed_quantity or 0)

    if planned < 0 or completed < 0:
        frappe.throw(_("Construction quantities cannot be negative."))

    if planned and completed > planned:
        frappe.throw(_("Completed quantity cannot exceed planned quantity."))

    if planned:
        doc.progress = min(round((completed / planned) * 100, 2), 100)
