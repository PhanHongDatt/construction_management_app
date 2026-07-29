from frappe.model.document import Document


class ProgressAcceptance(Document):
    """Validation logic is handled via doc_events hooks in events/acceptance.py."""
    pass
