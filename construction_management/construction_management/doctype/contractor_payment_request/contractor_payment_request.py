from frappe.model.document import Document


class ContractorPaymentRequest(Document):
    """Validation logic is handled via doc_events hooks in events/payment.py."""
    pass
