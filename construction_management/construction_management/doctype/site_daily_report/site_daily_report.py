import frappe
from frappe import _
from frappe.model.document import Document


class SiteDailyReport(Document):
    def validate(self):
        if not self.work_progress:
            frappe.throw(_("Work Progress table cannot be empty."))

        for row in self.work_progress:
            if float(row.completed_today or 0) < 0:
                frappe.throw(
                    _("Completed Today cannot be negative in row {0}.").format(row.idx)
                )
