from odoo import fields, models, api
from odoo.exceptions import ValidationError

class Datafacility(models.Model):

    _name = "facility"

    name = fields.Char(required="1")
    charge = fields.Float(default="100",required="1")


    @api.constrains('charge')
    def _check_charge(self):
            if self.charge <= 0:
                raise ValidationError("Charge must be greater than zero.")


