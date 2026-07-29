"""Demo seed for construction_management.
Idempotent — safe to run multiple times.

Usage:
    bench --site <site> execute construction_management.setup.demo.run
"""

import frappe
from frappe.utils import add_months, today


def run() -> None:
    frappe.flags.in_demo = True
    create_company()
    create_uoms()
    create_supplier_groups()
    create_item_groups()
    create_employees()
    create_suppliers()
    create_project()
    create_work_packages()
    create_tasks()
    create_daily_reports()
    create_acceptance()
    create_payment_request()
    frappe.db.commit()
    print("Demo seed complete.")


def _exists(doctype, name):
    return frappe.db.exists(doctype, name)


def _get_or_create(doctype, name, **kwargs):
    if _exists(doctype, name):
        return frappe.get_doc(doctype, name)
    doc = frappe.get_doc({"doctype": doctype, "name": name, **kwargs})
    doc.insert(ignore_permissions=True)
    return doc


def create_company():
    if not _exists("Company", "Demo Construction Corporation"):
        frappe.get_doc({
            "doctype": "Company",
            "company_name": "Demo Construction Corporation",
            "abbr": "DCC",
            "default_currency": "VND",
            "country": "Vietnam",
        }).insert(ignore_permissions=True)


def create_uoms():
    for uom in ["m2", "m3", "kg", "ton", "set", "day"]:
        if not _exists("UOM", uom):
            frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert(ignore_permissions=True)


def create_supplier_groups():
    for grp in ["Contractors", "Material Suppliers", "Equipment Suppliers"]:
        if not _exists("Supplier Group", grp):
            frappe.get_doc({"doctype": "Supplier Group", "supplier_group_name": grp}).insert(ignore_permissions=True)


def create_item_groups():
    for grp in ["Construction Materials", "MEP Materials", "Construction Equipment", "Subcontracted Services"]:
        if not _exists("Item Group", grp):
            parent = frappe.db.get_value("Item Group", {"parent_item_group": ""}, "name") or "All Item Groups"
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": grp,
                "parent_item_group": parent,
            }).insert(ignore_permissions=True)


def create_employees():
    employees = [
        {"employee_name": "Nguyen Van An", "gender": "Male", "date_of_birth": "1985-03-15", "date_of_joining": "2020-01-01", "company": "Demo Construction Corporation"},
        {"employee_name": "Tran Thi Bich", "gender": "Female", "date_of_birth": "1990-07-20", "date_of_joining": "2021-06-01", "company": "Demo Construction Corporation"},
        {"employee_name": "Le Van Cuong", "gender": "Male", "date_of_birth": "1988-11-05", "date_of_joining": "2019-03-15", "company": "Demo Construction Corporation"},
    ]
    for emp in employees:
        if not frappe.db.exists("Employee", {"employee_name": emp["employee_name"]}):
            frappe.get_doc({"doctype": "Employee", **emp}).insert(ignore_permissions=True)


def create_suppliers():
    suppliers = [
        {"supplier_name": "Cong Ty TNHH Xay Dung ABC", "supplier_group": "Contractors", "custom_is_contractor": 1},
        {"supplier_name": "Nha Thau Ket Cau XYZ", "supplier_group": "Contractors", "custom_is_contractor": 1},
        {"supplier_name": "Cong Ty Co Dien Lanh DEF", "supplier_group": "Contractors", "custom_is_contractor": 1},
    ]
    for sup in suppliers:
        if not frappe.db.exists("Supplier", {"supplier_name": sup["supplier_name"]}):
            frappe.get_doc({"doctype": "Supplier", **sup}).insert(ignore_permissions=True)


def create_project():
    if _exists("Project", "Green Tower"):
        return
    engineer = frappe.db.get_value("Employee", {"employee_name": "Nguyen Van An"}, "name")
    frappe.get_doc({
        "doctype": "Project",
        "project_name": "Green Tower",
        "status": "Open",
        "expected_start_date": today(),
        "expected_end_date": add_months(today(), 24),
        "custom_construction_code": "GT-2026-001",
        "custom_investor": "Tap Doan Green Future",
        "custom_site_location": "Quan 7, TP.HCM",
        "custom_project_category": "Commercial",
        "custom_site_manager": engineer,
        "custom_contract_value": 50_000_000_000,
        "custom_commencement_date": today(),
        "custom_handover_date": add_months(today(), 24),
        "custom_construction_status": "In Progress",
    }).insert(ignore_permissions=True)


def create_work_packages():
    project = "Green Tower"
    contractor_a = frappe.db.get_value("Supplier", {"supplier_name": "Cong Ty TNHH Xay Dung ABC"}, "name")
    contractor_b = frappe.db.get_value("Supplier", {"supplier_name": "Nha Thau Ket Cau XYZ"}, "name")
    contractor_c = frappe.db.get_value("Supplier", {"supplier_name": "Cong Ty Co Dien Lanh DEF"}, "name")

    packages = [
        {"package_name": "Phan Mong", "status": "Completed", "subcontractor": contractor_a, "contract_value": 8_000_000_000},
        {"package_name": "Ket Cau Khung", "status": "In Progress", "subcontractor": contractor_b, "contract_value": 20_000_000_000},
        {"package_name": "Dien Nuoc MEP", "status": "Draft", "subcontractor": contractor_c, "contract_value": 5_000_000_000},
    ]
    for pkg in packages:
        if not frappe.db.exists("Work Package", {"project": project, "package_name": pkg["package_name"]}):
            frappe.get_doc({
                "doctype": "Work Package",
                "project": project,
                "start_date": today(),
                "end_date": add_months(today(), 12),
                **pkg,
            }).insert(ignore_permissions=True)


def create_tasks():
    project = "Green Tower"
    engineer = frappe.db.get_value("Employee", {"employee_name": "Le Van Cuong"}, "name")
    pkg_mong = frappe.db.get_value("Work Package", {"project": project, "package_name": "Phan Mong"}, "name")

    tasks = [
        {"subject": "Ep coc be tong", "custom_planned_quantity": 500, "custom_completed_quantity": 500, "custom_uom": "m3", "custom_work_category": "Foundation"},
        {"subject": "Do be tong dai mong", "custom_planned_quantity": 800, "custom_completed_quantity": 720, "custom_uom": "m3", "custom_work_category": "Foundation"},
        {"subject": "Lap dung cot tang 1", "custom_planned_quantity": 200, "custom_completed_quantity": 180, "custom_uom": "m3", "custom_work_category": "Structure"},
        {"subject": "Lap dung san tang 1", "custom_planned_quantity": 1500, "custom_completed_quantity": 1200, "custom_uom": "m2", "custom_work_category": "Structure"},
        {"subject": "Lap dung cot tang 2", "custom_planned_quantity": 200, "custom_completed_quantity": 50, "custom_uom": "m3", "custom_work_category": "Structure"},
    ]
    for task in tasks:
        if not frappe.db.exists("Task", {"project": project, "subject": task["subject"]}):
            frappe.get_doc({
                "doctype": "Task",
                "project": project,
                "custom_work_package": pkg_mong,
                "custom_responsible_engineer": engineer,
                "status": "Working",
                "exp_start_date": today(),
                "exp_end_date": add_months(today(), 3),
                **task,
            }).insert(ignore_permissions=True)


def create_daily_reports():
    project = "Green Tower"
    engineer_emp = frappe.db.get_value("Employee", {"employee_name": "Nguyen Van An"}, "name")
    tasks = frappe.db.get_all("Task", filters={"project": project}, pluck="name", limit=3)

    if not tasks or frappe.db.exists("Site Daily Report", {"project": project}):
        return

    frappe.get_doc({
        "doctype": "Site Daily Report",
        "project": project,
        "report_date": today(),
        "prepared_by": engineer_emp,
        "weather": "Sunny",
        "workforce": [
            {"trade": "Mason", "worker_count": 15, "working_hours": 8},
            {"trade": "Ironworker", "worker_count": 10, "working_hours": 8},
        ],
        "work_progress": [
            {"task": tasks[0], "completed_today": 50, "uom": "m3"},
        ],
        "equipment_used": "Tower crane TCR 6040, Concrete pump",
    }).insert(ignore_permissions=True)


def create_acceptance():
    project = "Green Tower"
    contractor_a = frappe.db.get_value("Supplier", {"supplier_name": "Cong Ty TNHH Xay Dung ABC"}, "name")
    engineer = frappe.db.get_value("Employee", {"employee_name": "Nguyen Van An"}, "name")
    tasks = frappe.db.get_all("Task", filters={"project": project}, pluck="name", limit=2)

    if not tasks or frappe.db.exists("Progress Acceptance", {"project": project}):
        return

    frappe.get_doc({
        "doctype": "Progress Acceptance",
        "project": project,
        "subcontractor": contractor_a,
        "acceptance_date": today(),
        "engineer": engineer,
        "items": [
            {
                "task": tasks[0],
                "requested_quantity": 500,
                "accepted_quantity": 500,
                "unit_rate": 1_200_000,
                "result": "Accepted",
            },
        ],
    }).insert(ignore_permissions=True)


def create_payment_request():
    project = "Green Tower"
    contractor_a = frappe.db.get_value("Supplier", {"supplier_name": "Cong Ty TNHH Xay Dung ABC"}, "name")
    wp = frappe.db.get_value("Work Package", {"project": project, "package_name": "Phan Mong"}, "name")

    if not wp or frappe.db.exists("Contractor Payment Request", {"project": project}):
        return

    frappe.get_doc({
        "doctype": "Contractor Payment Request",
        "project": project,
        "work_package": wp,
        "subcontractor": contractor_a,
        "request_date": today(),
        "contract_value": 8_000_000_000,
        "approved_acceptance_value": 600_000_000,
        "previously_requested": 0,
        "gross_current_amount": 540_000_000,
        "tax_amount": 54_000_000,
        "deductions": [
            {"deduction_type": "Retention", "description": "5% bao hanh cong trinh", "amount": 30_000_000},
        ],
    }).insert(ignore_permissions=True)
