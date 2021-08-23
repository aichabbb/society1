from odoo import models, fields


class SaleOrderGammaProductionInherit(models.Model):
    _inherit = 'sale.order'

    production_ids = fields.One2many('launchmanufacturing', 'devis')
