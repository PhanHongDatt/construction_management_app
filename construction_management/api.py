import frappe


@frappe.whitelist()
def get_work_package_payment_summary(work_package: str, exclude_name: str = "") -> dict:
    """Return aggregated payment figures for a Work Package.

    Used by the Contractor Payment Request form to auto-populate read-only
    financial fields when the user selects a Work Package.

    Returns:
        contract_value: from Work Package
        approved_acceptance_value: sum of total_accepted_amount on submitted Progress Acceptances
        previously_requested: sum of gross_current_amount on submitted CPRs (excluding current doc)
    """
    if not frappe.db.exists("Work Package", work_package):
        frappe.throw(frappe._("Work Package {0} not found.").format(work_package))

    contract_value = frappe.db.get_value("Work Package", work_package, "contract_value") or 0

    approved_acceptance_value = (
        frappe.db.sql(
            """
            SELECT COALESCE(SUM(total_accepted_amount), 0)
            FROM `tabProgress Acceptance`
            WHERE work_package = %(wp)s AND docstatus = 1
            """,
            {"wp": work_package},
        )[0][0]
        or 0
    )

    prev_conditions = "work_package = %(wp)s AND docstatus = 1"
    prev_values: dict = {"wp": work_package}
    if exclude_name:
        prev_conditions += " AND name != %(excl)s"
        prev_values["excl"] = exclude_name

    previously_requested = (
        frappe.db.sql(
            f"""SELECT COALESCE(SUM(gross_current_amount), 0)
            FROM `tabContractor Payment Request`
            WHERE {prev_conditions}""",
            prev_values,
        )[0][0]
        or 0
    )

    return {
        "contract_value": float(contract_value),
        "approved_acceptance_value": float(approved_acceptance_value),
        "previously_requested": float(previously_requested),
    }
