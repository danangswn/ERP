"""
Distributor Core app setup helpers.

Executed by Frappe's install machinery via the standard
``install.py`` convention for ``bench install-app``.
"""

import frappe


def after_install():
    create_credit_override_role()
    setup_custom_fields()


def create_credit_override_role():
    """Create the Credit Override role used to bypass credit limit checks."""
    if not frappe.db.exists("Role", "Credit Override"):
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": "Credit Override",
                "desk_access": 1,
            }
        ).insert(ignore_permissions=True)


def setup_custom_fields():
    """Create custom fields and property setters declared in hooks.py."""
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    from distributor_core.distributor_core import hooks

    create_custom_fields(hooks.CUSTOM_FIELDS, ignore_validate=True, update=True)
