# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma_repair.tests.test_rma_repair_order import RMARepairOrderTest


class TestRmaRepairFollowLotLocation(RMARepairOrderTest):
    def test_action_create_repair_order(self):
        action_result = self.rma.action_create_repair_order()
        self.assertEqual(
            action_result["context"],
            {
                "default_rma_ids": [self.rma.id],
                "default_product_id": self.rma.product_id.id,
                "default_location_id": self.rma.location_id.id,
                "default_partner_id": self.rma.partner_id.id,
                "default_product_qty": self.rma.product_uom_qty,
                "default_product_uom": self.rma.product_uom.id,
                "default_address_id": self.rma.partner_shipping_id.id,
                "default_partner_invoice_id": self.rma.partner_invoice_id.id,
                "default_picking_id": self.rma.reception_move_id.picking_id.id,
                "default_follow_lot_location": self.operation.repair_follow_lot_location,
            },
        )

    def test_create_repair_order_repair_follow_lot_location(self):
        self.operation.repair_follow_lot_location = True
        repair = self.rma_without_repair._create_repair()
        self.assertTrue(repair.follow_lot_location)

    def test_create_repair_order_repair_no_follow_lot_location(self):
        self.operation.repair_follow_lot_location = False
        repair = self.rma_without_repair._create_repair()
        self.assertFalse(repair.follow_lot_location)
