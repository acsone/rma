# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form, TransactionCase


class TestRmaBatchReason(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.reason = cls.env["rma.reason"].create(
            {
                "name": {"en_US": "Test Reason"},
            }
        )
        cls.other_reason = cls.env["rma.reason"].create(
            {
                "name": {"en_US": "Other Reason"},
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
            }
        )
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.location = cls.warehouse.lot_stock_id
        cls.operation = cls.env["rma.operation"].create(
            {
                "name": "Test Operation",
                "code": "TEST",
            }
        )

    def _create_batch(self, reason=None):
        """Helper to create a batch with optional reason."""
        vals = {
            "partner_id": self.partner.id,
            "partner_shipping_id": self.partner.id,
            "partner_invoice_id": self.partner.id,
            "company_id": self.env.company.id,
            "location_id": self.location.id,
            "operation_id": self.operation.id,
        }
        if reason:
            vals["reason_id"] = reason.id
        return self.env["rma.batch"].create(vals)

    def _create_rma(self, batch=None, reason=None):
        """Helper to create an RMA with optional batch and reason."""
        vals = {
            "partner_id": self.partner.id,
            "product_id": self.product.id,
            "product_uom_qty": 1.0,
        }
        if batch:
            vals["batch_id"] = batch.id
        if reason:
            vals["reason_id"] = reason.id
        return self.env["rma"].create(vals)

    def test_rma_creation_with_batch_reason(self):
        """Test that RMAs created in a batch inherit the reason."""
        batch = self._create_batch(reason=self.reason)
        rma = self._create_rma(batch=batch)
        self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_compute_reason_from_batch(self):
        """Test that assigning batch to RMA via form computes the reason."""
        batch = self._create_batch(reason=self.reason)
        with Form(self.env["rma"]) as rma_form:
            rma_form.partner_id = self.partner
            rma_form.product_id = self.product
            rma_form.product_uom_qty = 1.0
            rma_form.batch_id = batch
            rma = rma_form.save()
            self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_batch_reason_update(self):
        """Test that updating batch reason propagates to draft RMAs."""
        batch = self._create_batch()
        rma = self._create_rma(batch=batch)
        self.assertFalse(rma.reason_id)
        # Update batch reason
        with Form(batch) as batch_form:
            batch_form.reason_id = self.reason
            batch_form.save()
        # Invalidate cache and recompute
        rma.invalidate_recordset()
        self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_reason_not_updated_when_confirmed(self):
        """Test that compute does not change reason for non-draft RMAs."""
        batch = self._create_batch(reason=self.other_reason)
        rma = self._create_rma(batch=batch)
        # Simulate non-draft state
        rma.state = "confirmed"
        # Update batch reason via form
        with Form(batch) as batch_form:
            batch_form.reason_id = self.reason
            batch_form.save()
        # Invalidate cache to trigger recompute
        rma.invalidate_recordset()
        # Should keep original reason since not in draft
        self.assertEqual(rma.reason_id, self.other_reason)
