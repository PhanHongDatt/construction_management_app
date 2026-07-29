"""Test suite for construction_management app.

Tests T01–T12 per Phase 2 runbook.

Run:
    bench --site <site> run-tests --app construction_management
"""

import frappe
from frappe.tests.utils import FrappeTestCase


class TestConstructionManagement(FrappeTestCase):
    """Tests T01–T12 for construction_management app."""

    # ------------------------------------------------------------------ setup

    def setUp(self):
        frappe.set_user("Administrator")
        self._ensure_dependencies()

    def _ensure_dependencies(self):
        """Create minimal master data required by all tests."""
        if not frappe.db.exists("Company", "Test Construction Co"):
            frappe.get_doc({
                "doctype": "Company",
                "company_name": "Test Construction Co",
                "abbr": "TCC",
                "default_currency": "VND",
                "country": "Vietnam",
            }).insert(ignore_permissions=True)

        if not frappe.db.exists("Supplier", {"supplier_name": "Test Contractor"}):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": "Test Contractor",
                "supplier_group": frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups",
            }).insert(ignore_permissions=True)

        if not frappe.db.exists("Employee", {"employee_name": "Test Engineer"}):
            frappe.get_doc({
                "doctype": "Employee",
                "employee_name": "Test Engineer",
                "gender": "Male",
                "date_of_birth": "1990-01-01",
                "date_of_joining": "2020-01-01",
                "company": "Test Construction Co",
            }).insert(ignore_permissions=True)

        if not frappe.db.exists("Project", "Test Project"):
            frappe.get_doc({
                "doctype": "Project",
                "project_name": "Test Project",
                "status": "Open",
                "expected_start_date": frappe.utils.today(),
                "expected_end_date": frappe.utils.add_months(frappe.utils.today(), 6),
            }).insert(ignore_permissions=True)

    def _make_task(self, planned=100.0, completed=0.0):
        return frappe.get_doc({
            "doctype": "Task",
            "subject": frappe.generate_hash(length=8),
            "project": "Test Project",
            "status": "Open",
            "exp_start_date": frappe.utils.today(),
            "exp_end_date": frappe.utils.add_months(frappe.utils.today(), 1),
            "custom_planned_quantity": planned,
            "custom_completed_quantity": completed,
        })

    # ------------------------------------------------------------------ T01
    def test_t01_custom_fields_are_created(self):
        """T01: Custom fields exist on Project, Task, Supplier."""
        from construction_management.setup.custom_fields import create_construction_custom_fields
        create_construction_custom_fields()

        for doctype, expected_fields in [
            ("Project", ["custom_construction_code", "custom_investor", "custom_construction_status"]),
            ("Task", ["custom_planned_quantity", "custom_completed_quantity", "custom_acceptance_status"]),
            ("Supplier", ["custom_is_contractor", "custom_contractor_license"]),
        ]:
            meta = frappe.get_meta(doctype)
            existing = {f.fieldname for f in meta.fields}
            for field in expected_fields:
                self.assertIn(field, existing, f"{field} missing from {doctype}")

    # ------------------------------------------------------------------ T02
    def test_t02_roles_are_idempotent(self):
        """T02: Creating roles twice does not raise and does not duplicate."""
        from construction_management.setup.roles import create_construction_roles, ROLES
        create_construction_roles()
        create_construction_roles()  # Second call must not fail

        for role in ROLES:
            count = frappe.db.count("Role", {"name": role})
            self.assertEqual(count, 1, f"Role {role} duplicated")

    # ------------------------------------------------------------------ T03
    def test_t03_task_completed_cannot_exceed_planned(self):
        """T03: Saving a task where completed > planned must raise."""
        task = self._make_task(planned=100.0, completed=150.0)
        with self.assertRaises(frappe.exceptions.ValidationError):
            task.insert(ignore_permissions=True)

    # ------------------------------------------------------------------ T04
    def test_t04_task_progress_is_calculated(self):
        """T04: progress = (completed / planned) * 100 on save."""
        task = self._make_task(planned=200.0, completed=50.0)
        task.insert(ignore_permissions=True)
        self.assertAlmostEqual(task.progress, 25.0, places=1)

    # ------------------------------------------------------------------ T05
    def test_t05_accepted_qty_cannot_exceed_requested(self):
        """T05: accepted_quantity > requested_quantity raises on PA validate."""
        task = self._make_task(planned=100.0, completed=80.0)
        task.insert(ignore_permissions=True)

        engineer = frappe.db.get_value("Employee", {"employee_name": "Test Engineer"}, "name")
        contractor = frappe.db.get_value("Supplier", {"supplier_name": "Test Contractor"}, "name")

        pa = frappe.get_doc({
            "doctype": "Progress Acceptance",
            "project": "Test Project",
            "subcontractor": contractor,
            "acceptance_date": frappe.utils.today(),
            "engineer": engineer,
            "items": [{
                "task": task.name,
                "requested_quantity": 50.0,
                "accepted_quantity": 99.0,  # > requested
                "unit_rate": 100_000,
                "result": "Accepted",
            }],
        })
        with self.assertRaises(frappe.exceptions.ValidationError):
            pa.insert(ignore_permissions=True)

    # ------------------------------------------------------------------ T06
    def test_t06_accepted_amount_is_calculated(self):
        """T06: accepted_amount = accepted_quantity * unit_rate."""
        task = self._make_task(planned=100.0, completed=80.0)
        task.insert(ignore_permissions=True)

        engineer = frappe.db.get_value("Employee", {"employee_name": "Test Engineer"}, "name")
        contractor = frappe.db.get_value("Supplier", {"supplier_name": "Test Contractor"}, "name")

        pa = frappe.get_doc({
            "doctype": "Progress Acceptance",
            "project": "Test Project",
            "subcontractor": contractor,
            "acceptance_date": frappe.utils.today(),
            "engineer": engineer,
            "items": [{
                "task": task.name,
                "requested_quantity": 80.0,
                "accepted_quantity": 60.0,
                "unit_rate": 500_000,
                "result": "Accepted",
            }],
        })
        pa.insert(ignore_permissions=True)
        self.assertAlmostEqual(pa.items[0].accepted_amount, 60.0 * 500_000)
        self.assertAlmostEqual(pa.total_accepted_amount, 60.0 * 500_000)

    # ------------------------------------------------------------------ T07
    def test_t07_payment_cannot_exceed_remaining_accepted_value(self):
        """T07: gross_current_amount > (approved - previously_requested) raises."""
        contractor = frappe.db.get_value("Supplier", {"supplier_name": "Test Contractor"}, "name")
        # Make a Work Package first
        wp = frappe.get_doc({
            "doctype": "Work Package",
            "project": "Test Project",
            "package_name": frappe.generate_hash(length=6),
            "status": "In Progress",
            "start_date": frappe.utils.today(),
            "end_date": frappe.utils.add_months(frappe.utils.today(), 3),
        }).insert(ignore_permissions=True)

        cpr = frappe.get_doc({
            "doctype": "Contractor Payment Request",
            "project": "Test Project",
            "work_package": wp.name,
            "subcontractor": contractor,
            "request_date": frappe.utils.today(),
            "approved_acceptance_value": 1_000_000,
            "previously_requested": 800_000,
            "gross_current_amount": 300_000,  # 800+300 > 1_000_000
        })
        with self.assertRaises(frappe.exceptions.ValidationError):
            cpr.insert(ignore_permissions=True)

    # ------------------------------------------------------------------ T08
    def test_t08_net_payment_is_calculated(self):
        """T08: net = gross - total_deduction + tax."""
        contractor = frappe.db.get_value("Supplier", {"supplier_name": "Test Contractor"}, "name")
        wp = frappe.get_doc({
            "doctype": "Work Package",
            "project": "Test Project",
            "package_name": frappe.generate_hash(length=6),
            "status": "In Progress",
            "start_date": frappe.utils.today(),
            "end_date": frappe.utils.add_months(frappe.utils.today(), 3),
        }).insert(ignore_permissions=True)

        cpr = frappe.get_doc({
            "doctype": "Contractor Payment Request",
            "project": "Test Project",
            "work_package": wp.name,
            "subcontractor": contractor,
            "request_date": frappe.utils.today(),
            "approved_acceptance_value": 5_000_000,
            "previously_requested": 0,
            "gross_current_amount": 1_000_000,
            "tax_amount": 100_000,
            "deductions": [{"deduction_type": "Retention", "amount": 50_000}],
        })
        cpr.insert(ignore_permissions=True)
        # net = 1_000_000 - 50_000 + 100_000 = 1_050_000
        self.assertAlmostEqual(cpr.net_payment_amount, 1_050_000)

    # ------------------------------------------------------------------ T09
    def test_t09_contractor_user_cannot_approve_payment(self):
        """T09: Contractor User role should not have submit permission on CPR."""
        meta = frappe.get_meta("Contractor Payment Request")
        contractor_perms = [
            p for p in meta.permissions
            if p.role == "Construction Contractor User"
        ]
        has_submit = any(getattr(p, "submit", 0) for p in contractor_perms)
        self.assertFalse(has_submit, "Contractor User must not have submit permission on CPR")

    # ------------------------------------------------------------------ T10
    def test_t10_demo_seed_is_idempotent(self):
        """T10: Running demo seed twice does not duplicate records."""
        from construction_management.setup.demo import run
        run()
        run()  # Second run must not raise or duplicate
        count = frappe.db.count("Project", {"project_name": "Green Tower"})
        self.assertEqual(count, 1, "Green Tower project duplicated")

    # ------------------------------------------------------------------ T11
    def test_t11_custom_fields_are_idempotent(self):
        """T11: create_construction_custom_fields twice does not raise."""
        from construction_management.setup.custom_fields import create_construction_custom_fields
        create_construction_custom_fields()
        create_construction_custom_fields()  # Must not raise

    # ------------------------------------------------------------------ T12
    def test_t12_after_migrate_is_idempotent(self):
        """T12: after_migrate runs twice without error."""
        from construction_management.migrate import after_migrate
        after_migrate()
        after_migrate()
