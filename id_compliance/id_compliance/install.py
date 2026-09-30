"""
ID Compliance app install hooks.

Executed by Frappe's install machinery via the standard
``install.py`` convention for ``bench install-app``.
"""

import frappe


def after_install():
    from id_compliance.id_compliance.patches.setup_tax_templates import execute

    execute()
