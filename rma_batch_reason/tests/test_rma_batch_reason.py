# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form

from .common import TestRmaBatchReasonCommon


class TestRmaBatchReason(TestRmaBatchReasonCommon):
    def test_rma_creation_with_batch_reason(self):
        """Test that RMAs created in a batch inherit the reason."""
        batch = self._create_batch(reason=self.reason)
        rma = self._create_rma(batch=batch)
        # Initial propagation on creation
        self.assertEqual(rma.reason_id, self.reason)

    def test_rma_form_batch_reason_update(self):
        """Test that updating batch reason propagates to draft RMAs."""
        batch = self._create_batch(reason=self.reason)
        rma = self._create_rma(batch=batch)
        batch.reason_id = self.other_reason
        rma._compute_reason_id()
        # Reason has been set on creation, should not be overridden by compute
        self.assertEqual(rma.reason_id, batch.reason_id)
