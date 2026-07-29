// Client-side UX for Contractor Payment Request.
// Financial totals are enforced server-side; this script fetches computed
// read-only values from submitted acceptances and prior payment requests.

frappe.ui.form.on("Contractor Payment Request", {
  work_package(frm) {
    _fetch_payment_summary(frm);
  },

  refresh(frm) {
    if (frm.doc.work_package && !frm.doc.approved_acceptance_value) {
      _fetch_payment_summary(frm);
    }
    _show_remaining(frm);
  },

  gross_current_amount(frm) {
    _show_remaining(frm);
  },
});

function _fetch_payment_summary(frm) {
  if (!frm.doc.work_package) return;

  frappe.call({
    method: "construction_management.api.get_work_package_payment_summary",
    args: {
      work_package: frm.doc.work_package,
      exclude_name: frm.doc.name || "",
    },
    callback(r) {
      if (!r.message) return;
      frm.set_value("contract_value", r.message.contract_value);
      frm.set_value("approved_acceptance_value", r.message.approved_acceptance_value);
      frm.set_value("previously_requested", r.message.previously_requested);
      _show_remaining(frm);
    },
  });
}

function _show_remaining(frm) {
  const approved = frm.doc.approved_acceptance_value || 0;
  const previous = frm.doc.previously_requested || 0;
  const gross = frm.doc.gross_current_amount || 0;
  const remaining = Math.max(approved - previous, 0);

  if (approved > 0) {
    const used_pct = Math.min(Math.round(((previous + gross) / approved) * 100), 100);
    frm.dashboard.show_progress(
      __("Payment Utilisation"),
      used_pct,
      __("Remaining approved value: {0}", [
        format_currency(remaining, frm.doc.currency),
      ])
    );
  }
}
