app_name = "construction_management"
app_title = "Construction Management"
app_publisher = "Construction Management Team"
app_description = "Construction management extension for ERPNext"
app_email = "dev@construction-mgmt.example.com"
app_license = "MIT"

required_apps = ["erpnext"]

# ------ Lifecycle hooks ------

after_install = "construction_management.setup.install.after_install"
after_migrate = "construction_management.migrate.after_migrate"

# ------ Document Events ------

doc_events = {
    "Task": {
        "validate": "construction_management.events.task.validate_task",
    },
    "Progress Acceptance": {
        "validate": "construction_management.events.acceptance.validate_acceptance",
        "on_submit": "construction_management.events.acceptance.on_submit",
    },
    "Contractor Payment Request": {
        "validate": "construction_management.events.payment.validate_payment_request",
    },
}

# ------ Client Scripts ------

doctype_js = {
    "Project": "public/js/project.js",
    "Task": "public/js/task.js",
    "Contractor Payment Request": "public/js/contractor_payment_request.js",
}

# ------ Fixtures ------
# export via: bench --site <site> export-fixtures

fixtures = [
    {"dt": "Role", "filters": [["name", "like", "Construction%"]]},
    {"dt": "Workflow", "filters": [["name", "like", "Construction%"]]},
    {"dt": "Workflow State", "filters": [["name", "like", "Construction%"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Construction Management"]]},
]
