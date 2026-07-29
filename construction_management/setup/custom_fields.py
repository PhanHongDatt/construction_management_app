import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Project": [
        {
            "fieldname": "construction_section",
            "label": "Construction Information",
            "fieldtype": "Section Break",
            "insert_after": "notes",
        },
        {
            "fieldname": "custom_construction_code",
            "label": "Construction Code",
            "fieldtype": "Data",
            "unique": 1,
            "insert_after": "construction_section",
        },
        {
            "fieldname": "custom_investor",
            "label": "Investor",
            "fieldtype": "Data",
            "insert_after": "custom_construction_code",
        },
        {
            "fieldname": "custom_site_location",
            "label": "Site Location",
            "fieldtype": "Small Text",
            "insert_after": "custom_investor",
        },
        {
            "fieldname": "custom_project_category",
            "label": "Construction Category",
            "fieldtype": "Select",
            "options": "Residential\nCommercial\nIndustrial\nInfrastructure\nRenovation\nOther",
            "insert_after": "custom_site_location",
        },
        {
            "fieldname": "custom_site_manager",
            "label": "Site Manager",
            "fieldtype": "Link",
            "options": "Employee",
            "insert_after": "custom_project_category",
        },
        {
            "fieldname": "custom_contract_value",
            "label": "Contract Value",
            "fieldtype": "Currency",
            "insert_after": "custom_site_manager",
        },
        {
            "fieldname": "custom_commencement_date",
            "label": "Commencement Date",
            "fieldtype": "Date",
            "insert_after": "custom_contract_value",
        },
        {
            "fieldname": "custom_handover_date",
            "label": "Expected Handover Date",
            "fieldtype": "Date",
            "insert_after": "custom_commencement_date",
        },
        {
            "fieldname": "custom_actual_progress",
            "label": "Actual Construction Progress",
            "fieldtype": "Percent",
            "read_only": 1,
            "insert_after": "custom_handover_date",
        },
        {
            "fieldname": "custom_construction_status",
            "label": "Construction Status",
            "fieldtype": "Select",
            "options": "Preparation\nIn Progress\nOn Hold\nDelayed\nUnder Acceptance\nCompleted\nHanded Over",
            "insert_after": "custom_actual_progress",
        },
    ],
    "Task": [
        {
            "fieldname": "construction_task_section",
            "label": "Construction Task",
            "fieldtype": "Section Break",
            "insert_after": "description",
        },
        {
            "fieldname": "custom_work_item_code",
            "label": "Work Item Code",
            "fieldtype": "Data",
            "insert_after": "construction_task_section",
        },
        {
            "fieldname": "custom_work_package",
            "label": "Work Package",
            "fieldtype": "Link",
            "options": "Work Package",
            "insert_after": "custom_work_item_code",
        },
        {
            "fieldname": "custom_work_category",
            "label": "Work Category",
            "fieldtype": "Select",
            "options": "Site Preparation\nFoundation\nStructure\nArchitecture\nMEP\nFinishing\nInspection\nOther",
            "insert_after": "custom_work_package",
        },
        {
            "fieldname": "custom_work_area",
            "label": "Work Area",
            "fieldtype": "Data",
            "insert_after": "custom_work_category",
        },
        {
            "fieldname": "custom_planned_quantity",
            "label": "Planned Quantity",
            "fieldtype": "Float",
            "non_negative": 1,
            "insert_after": "custom_work_area",
        },
        {
            "fieldname": "custom_completed_quantity",
            "label": "Completed Quantity",
            "fieldtype": "Float",
            "non_negative": 1,
            "insert_after": "custom_planned_quantity",
        },
        {
            "fieldname": "custom_uom",
            "label": "UOM",
            "fieldtype": "Link",
            "options": "UOM",
            "insert_after": "custom_completed_quantity",
        },
        {
            "fieldname": "custom_responsible_engineer",
            "label": "Responsible Engineer",
            "fieldtype": "Link",
            "options": "Employee",
            "insert_after": "custom_uom",
        },
        {
            "fieldname": "custom_subcontractor",
            "label": "Subcontractor",
            "fieldtype": "Link",
            "options": "Supplier",
            "insert_after": "custom_responsible_engineer",
        },
        {
            "fieldname": "custom_acceptance_status",
            "label": "Acceptance Status",
            "fieldtype": "Select",
            "options": "Not Requested\nRequested\nUnder Review\nAccepted\nRejected",
            "default": "Not Requested",
            "insert_after": "custom_subcontractor",
        },
        {
            "fieldname": "custom_risk_level",
            "label": "Risk Level",
            "fieldtype": "Select",
            "options": "Low\nMedium\nHigh\nCritical",
            "insert_after": "custom_acceptance_status",
        },
        {
            "fieldname": "custom_delay_reason",
            "label": "Delay Reason",
            "fieldtype": "Small Text",
            "depends_on": "eval:doc.status=='Overdue' || doc.custom_risk_level=='Critical'",
            "insert_after": "custom_risk_level",
        },
    ],
    "Supplier": [
        {
            "fieldname": "construction_supplier_section",
            "label": "Construction Contractor",
            "fieldtype": "Section Break",
            "insert_after": "supplier_group",
        },
        {
            "fieldname": "custom_is_contractor",
            "label": "Is Contractor",
            "fieldtype": "Check",
            "insert_after": "construction_supplier_section",
        },
        {
            "fieldname": "custom_contractor_license",
            "label": "Contractor License",
            "fieldtype": "Data",
            "depends_on": "custom_is_contractor",
            "insert_after": "custom_is_contractor",
        },
    ],
}


def create_construction_custom_fields() -> None:
    """Create all custom fields. Idempotent — safe to call multiple times.

    Skips the Work Package Link field on Task if Work Package DocType
    does not yet exist (first-install scenario before DocType migration).
    """
    custom_fields = {
        doctype: list(fields) for doctype, fields in CUSTOM_FIELDS.items()
    }
    if not frappe.db.exists("DocType", "Work Package"):
        custom_fields["Task"] = [
            field
            for field in custom_fields["Task"]
            if field.get("fieldname") != "custom_work_package"
        ]

    create_custom_fields(custom_fields, update=True)
    frappe.db.commit()
