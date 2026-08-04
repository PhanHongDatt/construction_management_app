import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 180},
        {"fieldname": "work_package", "label": _("Work Package"), "fieldtype": "Link", "options": "Work Package", "width": 180},
        {"fieldname": "task", "label": _("Task"), "fieldtype": "Link", "options": "Task", "width": 150},
        {"fieldname": "uom", "label": _("UOM"), "fieldtype": "Link", "options": "UOM", "width": 80},
        {"fieldname": "requested_quantity", "label": _("Requested Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "accepted_quantity", "label": _("Accepted Qty"), "fieldtype": "Float", "width": 120},
        {"fieldname": "accepted_amount", "label": _("Accepted Amount"), "fieldtype": "Currency", "width": 150},
    ]


def get_data(filters):
    conditions = "pa.docstatus = 1"
    values = {}
    if filters.get("project"):
        conditions += " AND pa.project = %(project)s"
        values["project"] = filters["project"]
    if filters.get("from_date"):
        conditions += " AND pa.acceptance_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]
    if filters.get("to_date"):
        conditions += " AND pa.acceptance_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    return frappe.db.sql(
        f"""
        SELECT
            pa.project,
            pa.work_package,
            ai.task,
            ai.uom,
            ai.requested_quantity,
            ai.accepted_quantity,
            ai.accepted_amount
        FROM `tabProgress Acceptance` pa
        INNER JOIN `tabAcceptance Item` ai ON ai.parent = pa.name
        WHERE {conditions}
        ORDER BY pa.project, pa.work_package, ai.task
        """,
        values,
        as_dict=True,
    )
