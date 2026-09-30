"""
Marketplace Sync app install hooks.

Executed by Frappe's install machinery via the standard
``install.py`` convention for ``bench install-app``.
"""

import frappe


def after_install():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

    from marketplace_sync.marketplace_sync import hooks

    create_custom_fields(hooks.CUSTOM_FIELDS, ignore_validate=True, update=True)
