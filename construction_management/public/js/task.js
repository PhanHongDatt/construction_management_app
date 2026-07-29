// Client-side UX for Task DocType — construction extensions.
// Quantity validation is enforced server-side.

frappe.ui.form.on("Task", {
  refresh(frm) {
    // Show progress indicator based on quantities
    const planned = frm.doc.custom_planned_quantity || 0;
    const completed = frm.doc.custom_completed_quantity || 0;
    if (planned > 0) {
      const pct = Math.min(Math.round((completed / planned) * 100), 100);
      frm.dashboard.show_progress(
        __("Work Progress"),
        pct,
        __("{0}% complete ({1} / {2})", [pct, completed, planned])
      );
    }

    // Show delay reason field prominently when critical
    if (
      frm.doc.custom_risk_level === "Critical" ||
      frm.doc.status === "Overdue"
    ) {
      frm.get_field("custom_delay_reason").df.bold = 1;
      frm.refresh_field("custom_delay_reason");
    }
  },

  custom_completed_quantity(frm) {
    // Visual feedback — server does actual enforcement
    const planned = frm.doc.custom_planned_quantity || 0;
    const completed = frm.doc.custom_completed_quantity || 0;
    if (planned && completed > planned) {
      frappe.show_alert(
        {
          message: __("Completed quantity exceeds planned. Will be rejected on save."),
          indicator: "red",
        },
        5
      );
    }
  },
});
