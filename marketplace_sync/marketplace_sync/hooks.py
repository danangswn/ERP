app_name = "marketplace_sync"
app_title = "Marketplace Sync"
app_publisher = "Distributor ERP Lite"
app_description = "Marketplace connector framework (Shopee/Tokopedia) for ERPNext"
app_email = "dev@distributor-erp-lite.example"
app_license = "MIT"

required_apps = ["erpnext"]

# ---------------------------------------------------------------------------
# Scheduled jobs — every job no-ops unless Marketplace Settings.enabled = 1
# ---------------------------------------------------------------------------

scheduler_events = {
    "cron": {
        "*/15 * * * *": [
            "marketplace_sync.jobs.sync_orders",
        ],
        "0 */4 * * *": [
            "marketplace_sync.jobs.push_stock_updates",
        ],
        "0 2 * * *": [
            "marketplace_sync.jobs.reconcile_settlements",
        ],
    },
}

CUSTOM_FIELDS = {
    ("Sales Order",): [
        dict(
            fieldname="marketplace_order_id",
            label="Marketplace Order ID",
            fieldtype="Data",
            insert_after="title",
            unique=1,
            description="External order id from Shopee/Tokopedia; used for idempotent imports.",
        ),
        dict(
            fieldname="marketplace",
            label="Marketplace",
            fieldtype="Select",
            options="\nShopee\nTokopedia",
            insert_after="marketplace_order_id",
        ),
    ],
}
