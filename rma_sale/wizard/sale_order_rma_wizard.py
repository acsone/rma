# Copyright 2020 Tecnativa - Ernesto Tejeda
# Copyright 2022 Tecnativa - Víctor Martínez
# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class SaleOrderRmaWizard(models.TransientModel):
    _name = "sale.order.rma.wizard"
    _description = "Sale Order Rma Wizard"

    def _domain_location_id(self):
        sale = self.env["sale.order"].browse(self.env.context.get("active_id"))
        rma_loc = (
            self.env["stock.warehouse"]
            .search([("company_id", "=", sale.company_id.id)])
            .mapped("rma_loc_id")
        )
        return [("id", "child_of", rma_loc.ids)]

    operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Requested operation",
    )
    order_id = fields.Many2one(
        comodel_name="sale.order",
        default=lambda self: self.env.context.get("active_id", False),
    )
    line_ids = fields.One2many(
        comodel_name="sale.order.line.rma.wizard",
        inverse_name="wizard_id",
        string="Lines",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="RMA location",
        domain=_domain_location_id,
        default=lambda r: r.order_id.warehouse_id.rma_loc_id.id,
    )
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.partner_id.commercial_partner_id",
        string="Commercial entity",
    )
    partner_shipping_id = fields.Many2one(
        comodel_name="res.partner",
        string="Shipping Address",
        help="Will be used to return the goods when the RMA is completed",
    )
    custom_description = fields.Text(
        help="Values coming from portal RMA request form custom fields",
    )
    is_return_all = fields.Boolean(string="Return All?", default=True)

    def create_rma(self, from_portal=False):
        self.ensure_one()
        user_has_group_portal = self.env.user.has_group(
            "base.group_portal"
        ) or self.env.user.has_group("base.group_public")
        lines = self.line_ids.filtered(lambda r: r.quantity > 0.0)
        val_list = [line._prepare_rma_values() for line in lines]
        rma_model = (
            self.env["rma"].with_user(SUPERUSER_ID)
            if user_has_group_portal
            else self.env["rma"]
        )
        rma = rma_model.create(val_list)
        if from_portal:
            rma._add_message_subscribe_partner()
        # post messages
        msg_list = [
            '<a href="#" data-oe-model="rma" data-oe-id="%d">%s</a>' % (r.id, r.name)
            for r in rma
        ]
        msg = ", ".join(msg_list)
        if len(msg_list) == 1:
            self.order_id.message_post(body=_(msg + " has been created."))
        elif len(msg_list) > 1:
            self.order_id.message_post(body=_(msg + " have been created."))
        rma.message_post_with_view(
            "mail.message_origin_link",
            values={"self": rma, "origin": self.order_id},
            subtype_id=self.env.ref("mail.mt_note").id,
        )
        return rma

    def create_and_open_rma(self):
        self.ensure_one()
        rma = self.create_rma()
        if not rma:
            return
        for rec in rma:
            rec.action_confirm()
        action = self.sudo().env.ref("rma.rma_action").read()[0]
        if len(rma) > 1:
            action["domain"] = [("id", "in", rma.ids)]
        elif rma:
            action.update(
                res_id=rma.id,
                view_mode="form",
                view_id=False,
                views=False,
            )
        return action


class SaleOrderLineRmaWizard(models.TransientModel):
    _name = "sale.order.line.rma.wizard"
    _description = "Sale Order Line Rma Wizard"

    wizard_id = fields.Many2one(comodel_name="sale.order.rma.wizard", string="Wizard")
    order_id = fields.Many2one(
        comodel_name="sale.order",
        default=lambda self: self.env["sale.order"].browse(
            self.env.context.get("active_id", False)
        ),
    )
    allowed_product_ids = fields.Many2many(
        comodel_name="product.product", compute="_compute_allowed_product_ids"
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
        domain="[('id', 'in', allowed_product_ids)]",
    )
    uom_category_id = fields.Many2one(
        comodel_name="uom.category",
        related="product_id.uom_id.category_id",
    )
    quantity = fields.Float(
        digits="Product Unit of Measure",
        required=True,
        compute="_compute_quantity",
        store=True,
        readonly=False,
    )
    allowed_quantity = fields.Float(digits="Product Unit of Measure", readonly=True)
    uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
        domain="[('category_id', '=', uom_category_id)]",
        required=True,
    )
    allowed_picking_ids = fields.Many2many(
        comodel_name="stock.picking", compute="_compute_allowed_picking_ids"
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        string="Delivery order",
        domain="[('id', 'in', allowed_picking_ids)]",
    )
    move_id = fields.Many2one(comodel_name="stock.move", compute="_compute_move_id")
    operation_id = fields.Many2one(
        comodel_name="rma.operation",
        string="Requested operation",
        compute="_compute_operation_id",
        store=True,
        readonly=False,
    )
    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
    )
    description = fields.Text()

    # Replace fields, used when the delivery is created automatically
    replace_warehouse_id = fields.Many2one(
        "stock.warehouse",
        help="Warehouse from which the replacement product will be shipped.",
        compute="_compute_replace_warehouse_id",
        store=True,
        readonly=False,
    )

    replace_product_id = fields.Many2one(
        "product.product",
        help="Product to be used as the replacement for the returned item.",
    )

    replace_product_uom_qty = fields.Float(
        string="Replacement Quantity",
        help="Quantity of the replacement product to be delivered.",
    )

    replace_product_uom = fields.Many2one(
        "uom.uom",
        string="Replacement UOM",
        help="Unit of Measure for the replacement product.",
        default=lambda self: self.env.ref("uom.product_uom_unit").id,
        compute="_compute_replace_product_uom",
        store=True,
        readonly=False,
    )
    show_replacement_fields = fields.Boolean(compute="_compute_show_replacement_fields")

    @api.depends("operation_id")
    def _compute_replace_warehouse_id(self):
        warehouse_model = self.env["stock.warehouse"]
        for rec in self:
            rec.replace_warehouse_id = warehouse_model.search(
                [("company_id", "=", rec.order_id.company_id.id)], limit=1
            )

    @api.depends("replace_product_id")
    def _compute_replace_product_uom(self):
        for record in self:
            if record.product_id:
                record.replace_product_uom = record.replace_product_id.uom_id
            else:
                record.replace_product_uom = False

    @api.depends(
        "operation_id.action_create_delivery", "operation_id.different_return_product"
    )
    def _compute_show_replacement_fields(self):
        for rec in self:
            rec.show_replacement_fields = (
                rec.operation_id.different_return_product
                and rec.operation_id.action_create_delivery
                in (
                    "automatic_on_confirm",
                    "automatic_after_receipt",
                )
            )

    @api.depends("wizard_id.operation_id")
    def _compute_operation_id(self):
        for rec in self:
            if rec.wizard_id.operation_id:
                rec.operation_id = rec.wizard_id.operation_id

    @api.depends("wizard_id.is_return_all", "allowed_quantity")
    def _compute_quantity(self):
        for rec in self:
            if not rec.wizard_id.is_return_all:
                rec.quantity = 0
            else:
                rec.quantity = rec.allowed_quantity

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.picking_id = False
        self.uom_id = self.product_id.uom_id

    @api.depends("picking_id")
    def _compute_move_id(self):
        for record in self:
            move_id = False
            if record.picking_id:
                move_id = record.picking_id.move_ids.filtered(
                    lambda r: (
                        r.sale_line_id == record.sale_line_id
                        and r.sale_line_id.product_id == record.product_id
                        and r.sale_line_id.order_id == record.order_id
                        and r.state == "done"
                    )
                )
            record.move_id = move_id

    @api.depends("order_id")
    def _compute_allowed_product_ids(self):
        for record in self:
            product_ids = record.order_id.order_line.mapped("product_id.id")
            record.allowed_product_ids = product_ids

    @api.depends("product_id")
    def _compute_allowed_picking_ids(self):
        for record in self:
            line = record.order_id.order_line.filtered(
                lambda r: r.product_id == record.product_id
            )
            record.allowed_picking_ids = line.mapped("move_ids.picking_id").filtered(
                lambda x: x.state == "done"
            )

    @api.constrains("quantity", "allowed_quantity")
    def _check_quantity(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for rec in self:
            if (
                float_compare(
                    rec.quantity, rec.allowed_quantity, precision_digits=precision
                )
                == 1
            ):
                raise ValidationError(
                    _(
                        "You can't exceed the allowed quantity for returning product "
                        "%(product)s.",
                        product=rec.product_id.display_name,
                    )
                )

    def _prepare_rma_values(self):
        self.ensure_one()
        partner_shipping = (
            self.wizard_id.partner_shipping_id or self.order_id.partner_shipping_id
        )
        description = (self.description or "") + (
            self.wizard_id.custom_description or ""
        )
        return {
            "partner_id": self.order_id.partner_id.id,
            "partner_invoice_id": self.order_id.partner_invoice_id.id,
            "partner_shipping_id": partner_shipping.id,
            "origin": self.order_id.name,
            "company_id": self.order_id.company_id.id,
            "location_id": self.wizard_id.location_id.id,
            "order_id": self.order_id.id,
            "picking_id": self.picking_id.id,
            "move_id": self.move_id.id,
            "product_id": self.product_id.id,
            "product_uom_qty": self.quantity,
            "product_uom": self.uom_id.id,
            "operation_id": self.operation_id.id,
            "description": description,
            "replace_warehouse_id": self.replace_warehouse_id.id,
            "replace_product_id": self.replace_product_id.id,
            "replace_product_uom_qty": self.replace_product_uom_qty,
            "replace_product_uom": self.replace_product_uom.id,
        }
