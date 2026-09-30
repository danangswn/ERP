app_name = "distributor_core"
app_title = "Distributor Core"
app_publisher = "Distributor ERP Lite"
app_description = "Core distributor operations layer for Indonesian distribution/wholesale SMBs"
app_email = "dev@distributor-erp-lite.example"
app_license = "MIT"

required_apps = ["erpnext"]

scheduler_events = {
    "daily": [
        "distributor_core.tasks.update_visit_statuses",
    ],
}

# ---------------------------------------------------------------------------
# Custom fields
# ---------------------------------------------------------------------------

CUSTOM_FIELDS = {
    ("Customer",): [
        dict(
            fieldname="id_npwp",
            label="NPWP",
            fieldtype="Data",
            insert_after="tax_id",
            description="Indonesian taxpayer identification number (15 or 16 digits).",
        ),
        dict(
            fieldname="sb_distributor_core_section",
            label="Distributor Credit & Terms",
            fieldtype="Section Break",
            insert_after="id_npwp",
        ),
        dict(
            fieldname="credit_limit_idr",
            label="Credit Limit (IDR)",
            fieldtype="Currency",
            options="Company:company_currency",
            insert_after="sb_distributor_core_section",
            description="Maximum outstanding receivable allowed for this customer.",
        ),
        dict(
            fieldname="payment_terms_days",
            label="Payment Terms (Days)",
            fieldtype="Int",
            insert_after="credit_limit_idr",
        ),
        dict(
            fieldname="price_tier",
            label="Price Tier",
            fieldtype="Select",
            options="\nRetail\nGrosir\nSub-distributor",
            insert_after="payment_terms_days",
        ),
        dict(
            fieldname="default_sales_rep",
            label="Default Sales Rep",
            fieldtype="Link",
            options="User",
            insert_after="price_tier",
        ),
        dict(
            fieldname="shipping_area",
            label="Shipping Area",
            fieldtype="Data",
            insert_after="default_sales_rep",
        ),
    ],
    ("Item",): [
        dict(
            fieldname="barcode_ean",
            label="Barcode (EAN)",
            fieldtype="Data",
            insert_after="item_barcode",
        ),
        dict(
            fieldname="unit_conversions",
            label="Unit Conversions",
            fieldtype="Table",
            options="Unit Conversion",
            insert_after="barcode_ean",
        ),
    ],
    ("Sales Invoice",): [
        dict(
            fieldname="terbilang",
            label="Terbilang (Amount in Words)",
            fieldtype="Data",
            read_only=1,
            no_copy=1,
            print_hide=0,
            insert_after="base_rounded_total",
        ),
        dict(
            fieldname="faktur_pajak_no",
            label="Faktur Pajak No",
            fieldtype="Data",
            insert_after="tax_id",
            description="16-digit e-Faktur number issued by DJP.",
        ),
    ],
}

# Child table custom field linked from Item.unit_conversions is a doctype
# (Unit Conversion) shipped with this app, no additional custom fields needed.

PROPERTY_SETTERS = [
    # IDR formatting property setters are applied on Sales Invoice money fields.
    dict(doctype_or_field="DocType:Sales Invoice", property="currency_precision", value="0"),
    dict(
        doctype_or_field="DocField:Sales Invoice.base_grand_total",
        property="options",
        value="currency\nCompany:company_currency",
    ),
]

TRANSLATIONS = [
    {"language": "id", "data": "distributor_core/translations/id.csv"},
]
