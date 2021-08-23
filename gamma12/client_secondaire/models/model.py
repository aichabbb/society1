from odoo import fields,models

class ClientSecondaire(models.Model):

    _inherit='sale.order'

    client_sec = fields.Many2one('client.secondaire',string='Client secondaire')

class ClientSecondaireTable(models.Model):

    _name='client.secondaire'

    name=fields.Char(string='Client secondaire')
    devis = fields.One2many('sale.order','client_sec',string='Devis liées')