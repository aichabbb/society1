from odoo import fields, models, api


class inherit_res_company(models.Model):
    _inherit = 'res.company'
    Banque_populaire = fields.Char(string='Banque Populaire',required=False,placeholder="Adresse bureaux")
    Capital = fields.Char(string='Capital',required=False,placeholder="Capital")




