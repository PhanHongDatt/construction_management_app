import frappe
from frappe import _


def validate_acceptance(doc, method=None) -> None:
    """Validate Progress Acceptance items and compute totals."""
    total = 0.0
    for row in doc.items:
        requested = float(row.requested_quantity or 0)
        accepted = float(row.accepted_quantity or 0)
        rate = float(row.unit_rate or 0)

        if requested < 0 or accepted < 0 or rate < 0:
            frappe.throw(
                _("Acceptance quantity and rate cannot be negative.")
            )
        if accepted > requested:
            frappe.throw(
                _("Accepted quantity cannot exceed requested quantity.")
            )

        row.accepted_amount = accepted * rate
        total += row.accepted_amount

    doc.total_accepted_amount = round(total, 2)


def on_submit(doc, method=None) -> None:
    """After acceptance is submitted, mark tasks as Accepted."""
    for row in doc.items:
        if row.task:
            frappe.db.set_value(
                "Task", row.task, "custom_acceptance_status", "Accepted"
            )
    frappe.db.commit()
