import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {"fieldname": "name", "label": _("Task"), "fieldtype": "Link", "options": "Task", "width": 150},
        {"fieldname": "subject", "label": _("Subject"), "fieldtype": "Data", "width": 250},
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 180},
        {"fieldname": "custom_responsible_engineer", "label": _("Responsible Engineer"), "fieldtype": "Link", "options": "Employee", "width": 180},
        {"fieldname": "exp_end_date", "label": _("Expected End Date"), "fieldtype": "Date", "width": 130},
        {"fieldname": "custom_risk_level", "label": _("Risk Level"), "fieldtype": "Data", "width": 100},
        {"fieldname": "custom_delay_reason", "label": _("Delay Reason"), "fieldtype": "Data", "width": 200},
    ]


def get_data(filters):
    conditions = "(t.status = 'Overdue' OR (t.exp_end_date < CURDATE() AND t.status NOT IN ('Completed', 'Cancelled')))"
    values = {}
    if filters.get("project"):
        conditions += " AND t.project = %(project)s"
        values["project"] = filters["project"]

    return frappe.db.sql(
        f"""
        SELECT
            t.name,
            t.subject,
            t.project,
            t.custom_responsible_engineer,
            t.exp_end_date,
            t.custom_risk_level,
            t.custom_delay_reason
        FROM `tabTask` t
        WHERE {conditions}
          AND t.docstatus < 2
        ORDER BY t.exp_end_date ASC
        """,
        values,
        as_dict=True,
    )
