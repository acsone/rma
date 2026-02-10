# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from .common import TestRmaBatchReasonCommon


@tagged("-at_install", "post_install")
class TestRmaBatchReason(TestRmaBatchReasonCommon):
    def test_rma_creation_with_batch_reason(self):
        """Test that RMAs created in a batch inherit the reason."""
        batch = self._create_batch(reason=self.reason)
        rma = self._create_rma(batch=batch)
        self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_batch_reason_update(self):
        """Test that updating batch reason propagates to draft RMAs without reason."""
        batch = self._create_batch()
        rma = self._create_rma(batch=batch, reason=self.reason)
        rma_without_reason = self._create_rma(batch=batch, reason=None)
        batch.reason_id = self.other_reason
        rma._compute_reason_id()
        rma_without_reason._compute_reason_id()
        self.assertEqual(rma.reason_id, batch.reason_id)
        self.assertEqual(rma_without_reason.reason_id, self.other_reason)

    def test_rma_form_batch_reason_update_when_not_draft(self):
        """Test that updating batch reason does not propagate to non-draft RMAs."""
        batch = self._create_batch(reason=self.reason)
        rma = self._create_rma(batch=batch)
        batch.action_confirm()
        batch.reason_id = self.other_reason
        rma._compute_reason_id()
        self.assertEqual(rma.reason_id, self.reason)
        batch.action_cancel()
        batch.reason_id = self.other_reason
        rma._compute_reason_id()
        self.assertEqual(rma.reason_id, self.reason)
