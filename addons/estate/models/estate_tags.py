from odoo import models, fields


class EstateTags(models.Model):
    _name = "estate.tags"
    _description = "Estate Tags"

    name = fields.Char(required=True)
    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(name)",
            "The name of the tag must be unique.",
        )
    ]
