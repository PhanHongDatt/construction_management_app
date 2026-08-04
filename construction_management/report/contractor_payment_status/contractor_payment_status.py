import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"fieldname": "subcontractor", "label": _("Contractor"), "fieldtype": "Link", "options": "Supplier", "width": 200},
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 180},
        {"fieldname": "contract_value", "label": _("Contract Value"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "approved_acceptance_value", "label": _("Accepted Value"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_requested", "label": _("Total Requested"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "total_approved", "label": _("Total Approved"), "fieldtype": "Currency", "width": 150},
        {"fieldname": "remaining", "label": _("Remaining"), "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = "cpr.docstatus < 2"
    values = {}
    if filters.get("project"):
        conditions += " AND cpr.project = %(project)s"
        values["project"] = filters["project"]

    return frappe.db.sql(
        f"""
        SELECT
            cpr.subcontractor,
            cpr.project,
            MAX(cpr.contract_value) AS contract_value,
            MAX(cpr.approved_acceptance_value) AS approved_acceptance_value,
            SUM(cpr.gross_current_amount) AS total_requested,
            SUM(CASE WHEN cpr.docstatus = 1 THEN cpr.net_payment_amount ELSE 0 END) AS total_approved,
            MAX(cpr.approved_acceptance_value) - SUM(CASE WHEN cpr.docstatus = 1 THEN cpr.net_payment_amount ELSE 0 END) AS remaining
        FROM `tabContractor Payment Request` cpr
        WHERE {conditions}
        GROUP BY cpr.subcontractor, cpr.project
        ORDER BY cpr.subcontractor
        """,
        values,
        as_dict=True,
    )
