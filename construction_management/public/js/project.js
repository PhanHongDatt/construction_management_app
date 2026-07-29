// Client-side UX enhancements for Project DocType.
// Business logic MUST remain server-side.

frappe.ui.form.on("Project", {
  refresh(frm) {
    // Highlight if construction project is delayed
    if (
      frm.doc.custom_construction_status === "Delayed" ||
      frm.doc.custom_construction_status === "On Hold"
    ) {
      frm.dashboard.set_headline_alert(
        __("This project is " + frm.doc.custom_construction_status),
        "yellow"
      );
    }

    // Show progress bar
    if (frm.doc.custom_actual_progress !== undefined) {
      frm.dashboard.show_progress(
        __("Construction Progress"),
        frm.doc.custom_actual_progress,
        __("Actual progress: {0}%", [frm.doc.custom_actual_progress])
      );
    }
  },

  custom_handover_date(frm) {
    // Warn if handover date is before commencement date
    if (
      frm.doc.custom_commencement_date &&
      frm.doc.custom_handover_date &&
      frm.doc.custom_handover_date < frm.doc.custom_commencement_date
    ) {
      frappe.msgprint(
        __("Expected Handover Date cannot be before Commencement Date."),
        __("Validation")
      );
      frm.set_value("custom_handover_date", null);
    }
  },
});
