from odoo import models,fields

class Createlocation(models.Model):
    _inherit="stock.location"

    is_location_of_fabrication_it=fields.Boolean()


