import frappe
from frappe import _


def validate_payment_request(doc, method=None) -> None:
    """Validate Contractor Payment Request amounts."""
    gross = float(doc.gross_current_amount or 0)
    approved = float(doc.approved_acceptance_value or 0)
    previous = float(doc.previously_requested or 0)

    if gross < 0:
        frappe.throw(_("Gross current amount cannot be negative."))

    available = max(approved - previous, 0)
    if gross > available:
        frappe.throw(
            _(
                "Requested amount ({0}) exceeds the remaining approved acceptance value ({1})."
            ).format(frappe.format(gross, {"fieldtype": "Currency"}), frappe.format(available, {"fieldtype": "Currency"}))
        )

    total_deduction = sum(float(row.amount or 0) for row in doc.deductions)
    if total_deduction < 0:
        frappe.throw(_("Total deduction cannot be negative."))

    doc.total_deduction = round(total_deduction, 2)
    doc.net_payment_amount = round(
        gross - total_deduction + float(doc.tax_amount or 0), 2
    )

    if doc.net_payment_amount < 0:
        frappe.throw(_("Net payment amount cannot be negative."))
