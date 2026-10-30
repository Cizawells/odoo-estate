from odoo import models, fields


class EstateBuyer(models.Model):
    _name = "estate.buyer"
    _description = "Estate Buyer"

    name = fields.Char(required=True)
