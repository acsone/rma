# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma_repair.tests.test_rma_repair_order import RMARepairOrderTest


class TestRmaRepairFollowLotLocation(RMARepairOrderTest):
    def test_action_create_repair_order_follow_lot_location(self):
        self.operation.repair_follow_lot_location = True
        action_result = self.rma.action_create_repair_order()
        ctx = action_result.get("context", {})
        key = "default_follow_lot_location"
        self.assertIn(key, ctx)
        self.assertTrue(ctx[key])

    def test_action_create_repair_order_no_follow_lot_location(self):
        self.operation.repair_follow_lot_location = False
        action_result = self.rma.action_create_repair_order()
        ctx = action_result.get("context", {})
        key = "default_follow_lot_location"
        self.assertIn(key, ctx)
        self.assertFalse(ctx[key])

    def test_create_repair_order_repair_follow_lot_location(self):
        self.operation.repair_follow_lot_location = True
        repair = self.rma_without_repair._create_repair()
        self.assertTrue(repair.follow_lot_location)

    def test_create_repair_order_repair_no_follow_lot_location(self):
        self.operation.repair_follow_lot_location = False
        repair = self.rma_without_repair._create_repair()
        self.assertFalse(repair.follow_lot_location)
