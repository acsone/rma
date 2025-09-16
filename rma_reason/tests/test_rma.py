# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.tests.test_rma import TestRma as TestRmaBase


class TestRma(TestRmaBase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.rma_operation_allowed_for_reason = cls.env["rma.operation"].create(
            {"name": "Allowed"}
        )
        cls.rma_operation_forbidden_for_reason = cls.env["rma.operation"].create(
            {"name": "Forbidden"}
        )
        cls.rma_reason = cls.env["rma.reason"].create(
            {
                "name": "Reason",
                "allowed_operation_ids": [(4, cls.rma_operation_allowed_for_reason.id)],
            }
        )
        return res

    def test_allowed_operations(self):
        rma = self._create_rma(partner=self.partner, product=self.product)
        # No reason -> all are allowed
        self.assertEqual(
            set(self.env["rma.operation"].search(rma.operation_domain).ids),
            {
                self.rma_operation_allowed_for_reason.id,
                self.rma_operation_forbidden_for_reason.id,
            },
        )
        # Set a reason -> take only the operations allowed on the reason
        rma.reason_id = self.rma_reason
        self.assertEqual(
            self.env["rma.operation"].search(rma.operation_domain).ids,
            [self.rma_operation_allowed_for_reason.id],
        )
