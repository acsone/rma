# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .common import TestRmaBatchReasonCommon


class TestRmaBatchReason(TestRmaBatchReasonCommon):
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
        with Form(batch) as batch_form:
            batch_form.reason_id = self.reason
            batch_form.save()
            self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_reason_not_updated_when_confirmed(self):
        """Test that compute does not change reason for non-draft RMAs."""
        batch = self._create_batch(reason=self.other_reason)
        rma = self._create_rma(batch=batch)
        rma.state = "confirmed"
        with Form(batch) as batch_form:
            batch_form.reason_id = self.reason
            batch_form.save()
            # Should keep original reason since not in draft
            self.assertEqual(rma.reason_id, self.other_reason)
