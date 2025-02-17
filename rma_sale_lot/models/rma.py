# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class Rma(models.Model):

    _inherit = "rma"

    def action_confirm(self):
        res = super().action_confirm()
        for ml in self.reception_move_id.picking_id.move_line_ids:
            ml.lot_id = ml.move_id.restrict_lot_id
        return res
