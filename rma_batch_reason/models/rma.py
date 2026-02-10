# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Rma(models.Model):
    _inherit = "rma"

    @api.model_create_multi
    def create(self, vals_list):
        rmas = super().create(vals_list)
        for rma in rmas:
            if rma.batch_id and rma.batch_id.reason_id and not rma.reason_id:
                rma.reason_id = rma.batch_id.reason_id
        return rmas

    @api.depends("batch_id.reason_id")
    def _compute_reason_id(self):
        for rec in self:
            if rec.state != "draft":
                continue
            if rec.batch_id.reason_id:
                rec.reason_id = rec.batch_id.reason_id
