# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RmaBatch(models.Model):
    _inherit = "rma.batch"

    reason_id = fields.Many2one(
        "rma.reason",
        string="Reason",
        help="Reason for the return, applied to all RMAs in the batch.",
    )
