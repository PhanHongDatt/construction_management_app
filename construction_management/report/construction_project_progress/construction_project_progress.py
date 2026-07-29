import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters or {})
    return columns, data


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": "Project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 200,
        },
        {
            "fieldname": "project_name",
            "label": "Project Name",
            "fieldtype": "Data",
            "width": 250,
        },
        {
            "fieldname": "custom_construction_status",
            "label": "Construction Status",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "planned_progress",
            "label": "Planned Progress",
            "fieldtype": "Percent",
            "width": 130,
        },
        {
            "fieldname": "actual_progress",
            "label": "Actual Progress",
            "fieldtype": "Percent",
            "width": 130,
        },
        {
            "fieldname": "overdue_tasks",
            "label": "Overdue Tasks",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "fieldname": "risk_count",
            "label": "High/Critical Risk Tasks",
            "fieldtype": "Int",
            "width": 160,
        },
    ]


def get_data(filters):
    conditions = "p.status != 'Completed'"
    values = {}
    if filters.get("project"):
        conditions += " AND p.name = %(project)s"
        values["project"] = filters["project"]

    projects = frappe.db.sql(
        f"""
        SELECT
            p.name,
            p.project_name,
            p.custom_construction_status,
            p.percent_complete AS planned_progress,
            p.custom_actual_progress AS actual_progress,
            COALESCE(t.overdue_count, 0) AS overdue_tasks,
            COALESCE(t.risk_count, 0) AS risk_count
        FROM `tabProject` p
        LEFT JOIN (
            SELECT
                project,
                SUM(CASE WHEN status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_count,
                SUM(CASE WHEN custom_risk_level IN ('High', 'Critical') THEN 1 ELSE 0 END) AS risk_count
            FROM `tabTask`
            WHERE docstatus < 2
            GROUP BY project
        ) t ON t.project = p.name
        WHERE {conditions}
        ORDER BY p.modified DESC
        """,
        values,
        as_dict=True,
    )
    return projects
