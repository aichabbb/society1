from odoo import models,fields


class DemandeInPurchseOrder(models.Model):
    _inherit = 'purchase.order'

    demande_achat = fields.Many2one('demande.achat',"Demande d'achat")



