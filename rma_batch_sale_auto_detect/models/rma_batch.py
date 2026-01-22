# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RmaBatch(models.Model):
    _inherit = "rma.batch"

    state = fields.Selection(
        selection_add=[("manual", "Manual Treatment")],
        help=(
            "Represents the preparation and validation progress of the RMA batch:\n"
            "- Draft: RMAs are being prepared\n"
            "- Manual Treatment: One or more RMAs require manual matching\n"
            "- Ready: All RMAs are completed and batch is ready to be confirmed\n"
            "- Confirmed: The batch is validated and all RMAs are confirmed\n"
            "- Cancelled: The batch is cancelled"
        ),
    )

    quick_confirm = fields.Boolean(
        string="Bypass Sale Link Check",
        compute="_compute_quick_confirm",
        help=(
            "If enabled, allows confirming RMA batches in ready state when "
            "all RMAs are unlinked with sale order lines."
        ),
    )

    def _compute_quick_confirm(self):
        for batch in self:
            batch.quick_confirm = False
            valid = all([not rma.sale_line_id for rma in batch.rma_ids])
            batch.quick_confirm = batch.state == "ready" and valid

    def action_quick_confirm(self):
        """Confirm the RMA batch even when all RMAs are not linked to sale order lines
        and batch is ready."""
        for batch in self:
            if not batch.quick_confirm:
                raise ValueError(
                    f"Cannot confirm the RMA batch {batch.name}: "
                    "some RMAs are linked to sale order lines"
                )
        self.mapped("rma_ids").write({"ignore_sale_auto_detect": True})
        return super().action_confirm()

    def action_link_rma_to_sale_line(self):
        self.rma_ids.action_link_rma_to_sale_line()

    def action_ready(self):
        res = super().action_ready()
        self.rma_ids.has_sale_auto_detect_issue = False
        self.action_link_rma_to_sale_line()
        for rec in self:
            if any(rec.rma_ids.mapped("has_sale_auto_detect_issue")):
                rec.state = "manual"
        return res
