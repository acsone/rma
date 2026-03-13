# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _is_restocking_fee_chargeable(self):
        """
        super() method from sale_stock_restocking_fee_invoicing
        always returns False if move has no origin_returned_move_id.
        But for RMAs it may happen that we create a RMA from scratch, not linked
        to an origin move.
        """
        res = super()._is_restocking_fee_chargeable()
        if self.rma_receiver_ids and self.charge_restocking_fee:
            return True
        return res

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        chargeable_moves = self.filtered(
            lambda r: r.state == "done" and r._is_restocking_fee_chargeable()
        ).sudo()
        # Find the related RMAs by going back to the first move of the chain
        chargeable_moves.sudo().mapped(
            "first_move_id.rma_receiver_ids"
        )._create_restocking_fee_invoice()
        return res
