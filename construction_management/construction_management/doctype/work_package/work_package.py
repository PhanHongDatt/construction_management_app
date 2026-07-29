import frappe
from frappe import _
from frappe.model.document import Document


class WorkPackage(Document):
    def validate(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            frappe.throw(_("End Date cannot be before Start Date."))
        if self.contract_value and self.contract_value < 0:
            frappe.throw(_("Contract Value cannot be negative."))
        if self.budget and self.budget < 0:
            frappe.throw(_("Budget cannot be negative."))
