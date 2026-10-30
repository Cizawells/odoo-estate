from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    name = fields.Char(required=True, default="Name")
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        copy=False,
        default=lambda self: self.env.user,
    )
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(Copy=False, default=fields.Datetime.now)
    last_seen = fields.Date("Last Seen", default=fields.Datetime.now)
    expected_price = fields.Float()
    selling_price = fields.Float(Copy=False)
    bedrooms = fields.Integer()
    status = fields.Char(default="New")
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    active = fields.Boolean(default=True)
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tags_ids = fields.Many2many("estate.tags", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    garden_orientation = fields.Selection(
        [("north", "North"), ("south", "South"), ("east", "East"), ("west", "West")]
    )
    total_area = fields.Float(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    _sql_constraints = [
        (
            "check_expected_price",
            "CHECK(expected_price > 0)",
            "Expected price must be greater than 0.",
        ),
        (
            "check_selling_price",
            "CHECK(selling_price >= 0)",
            "Selling price must be greater than or equal to 0.",
        ),
    ]

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_status_sold(self):
        for record in self:
            if record.status == "refused":
                raise UserError("Refused properties cannot be sold.")
            record.status = "accepted"
        return True

    def action_status_cancel(self):
        for record in self:
            if record.status == "accepted":
                raise UserError("Sold properties cannot be canceled.")
            record.status = "refused"
        return True
