# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import _, api, fields, models
from odoo.osv.expression import AND


class RmaOperation(models.Model):
    _name = "rma.operation"
    _description = "RMA requested operation"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, translate=True)
    color = fields.Integer()
    count_rma_draft = fields.Integer(compute="_compute_count_rma_draft")
    count_rma_awaiting_action = fields.Integer(
        compute="_compute_count_rma_awaiting_action"
    )
    count_rma_processed = fields.Integer(compute="_compute_count_rma_processed")

    _sql_constraints = [
        ("name_uniq", "unique (name)", "That operation name already exists !"),
    ]

    @api.model
    def _get_rma_draft_domain(self):
        return [("state", "=", "draft")]

    @api.model
    def _get_rma_awaiting_action_domain(self):
        return [("state", "in", ["waiting_return", "waiting_replacement", "confirmed"])]

    @api.model
    def _get_rma_processed_domain(self):
        return [
            (
                "state",
                "in",
                [("state", "in", ["received", "refunded", "replaced", "finished"])],
            )
        ]

    def _compute_count_rma_draft(self):
        self.update({"count_rma_draft": 0})
        for group in self.env["rma"].read_group(
            AND(
                [
                    [("operation_id", "!=", False)],
                    self._get_rma_draft_domain(),
                ]
            ),
            groupby=["operation_id"],
            fields=["id"],
        ):
            operation_id = group.get("operation_id")[0]
            self.browse(operation_id).count_rma_draft = group.get("operation_id_count")

    def _compute_count_rma_awaiting_action(self):
        self.update({"count_rma_awaiting_action": 0})
        for group in self.env["rma"].read_group(
            AND(
                [
                    [("operation_id", "!=", False)],
                    self._get_rma_awaiting_action_domain(),
                ]
            ),
            groupby=["operation_id"],
            fields=["id"],
        ):
            operation_id = group.get("operation_id")[0]
            self.browse(operation_id).count_rma_awaiting_action = group.get(
                "operation_id_count"
            )

    def _compute_count_rma_processed(self):
        self.update({"count_rma_processed": 0})
        for group in self.env["rma"].read_group(
            AND(
                [
                    [("operation_id", "!=", False)],
                    self._get_rma_processed_domain(),
                ]
            ),
            groupby=["operation_id"],
            fields=["id"],
        ):
            operation_id = group.get("operation_id")[0]
            self.browse(operation_id).count_rma_processed = group.get(
                "operation_id_count"
            )

    def _get_action(self, name, domain):
        action = self.env["ir.actions.actions"]._for_xml_id("rma.rma_action")
        action["display_name"] = name
        context = {
            "search_default_operation_id": [self.id],
            "default_operation_id": self.id,
        }
        action_context = literal_eval(action["context"])
        context = {**action_context, **context}
        action["context"] = context
        action["domain"] = domain
        return action

    def get_action_rma_tree_confirmed(self):
        self.ensure_one()
        name = self.display_name + ": " + _("Confirmed")
        return self._get_action(
            name,
            domain=[("operation_id", "=", self.id), ("state", "=", "confirmed")],
        )

    def get_action_rma_tree_draft(self):
        self.ensure_one()
        name = self.display_name + ": " + _("Draft")
        return self._get_action(
            name,
            domain=AND(
                [
                    [("operation_id", "=", self.id)],
                    self._get_rma_draft_domain(),
                ]
            ),
        )

    def get_action_rma_tree_awaiting_action(self):
        self.ensure_one()
        name = self.display_name + ": " + _("Awaiting Action")
        return self._get_action(
            name,
            domain=AND(
                [
                    [("operation_id", "=", self.id)],
                    self._get_rma_awaiting_action_domain(),
                ]
            ),
        )

    def get_action_rma_tree_processed(self):
        self.ensure_one()
        name = self.display_name + ": " + _("Processed")
        return self._get_action(
            name,
            domain=AND(
                [
                    [("operation_id", "=", self.id)],
                    self._get_rma_processed_domain(),
                ]
            ),
        )

    def get_action_all_rma(self):
        self.ensure_one()
        name = self.display_name
        return self._get_action(name, domain=[("operation_id", "=", self.id)])
