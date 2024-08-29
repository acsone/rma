# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE rma
        ADD COLUMN IF NOT EXISTS replace_warehouse_id INTEGER
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE rma
        ADD COLUMN IF NOT EXISTS replace_product_uom INTEGER
        """,
    )
