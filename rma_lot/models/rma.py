# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Rma(models.Model):

    _inherit = "rma"

    lot_id = fields.Many2one(comodel_name="stock.lot", string="Lot/Serial Number")

    def _prepare_reception_procurement_vals(self, group=None):
        vals = super()._prepare_reception_procurement_vals(group=group)
        vals["restrict_lot_id"] = self.lot_id.id
        return vals
