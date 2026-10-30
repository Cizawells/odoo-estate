from odoo import fields, models
from odoo import api
import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"

    price = fields.Float()
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused")], default=""
    )
    validity = fields.Integer(string="Validity (days)")
    date_deadline = fields.Date(
        compute="_compute_date_deadline", inverse="_inverse_validity", store=True
    )
    partner_id = fields.Many2one("res.partner", string="Buyer")
    property_id = fields.Many2one("estate.property", string="Property")

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            create_date = fields.Date.today()
            record.date_deadline = fields.Date.add(
                create_date,
                days=record.validity or 0,
            )

    def _inverse_validity(self):
        for record in self:
            if record.date_deadline:
                create_date = fields.Date.today()
                # Ensure both sides are date objects
                deadline = fields.Date.to_date(record.date_deadline)
                record.validity = (deadline - create_date).days
                _logger.info("VALIDITY SET TO: %s", record.validity)

    def action_confirm(self):

        _logger.info("action_confirm called for estate.property.offer ids=%s", self.ids)
        _logger.info("Partner ID IDddddddddddd: %s", self.partner_id.id)
        for record in self:
            if record.property_id.status == "Sold":
                raise UserError("Property is already sold.")
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price

    def action_cancel(self):
        for record in self:
            if record.property_id.status == "Sold":
                raise UserError("Sold properties cannot be canceled.")
            record.status = "refused"
        _logger.info("action_cancel called for estate.property.offer ids=%s", self.ids)
