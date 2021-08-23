# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class pièce(models.Model):
    _name = 'piece'
    
    
    document = fields.Char(
        string='DOCUMENT',
        required=False)

    numero = fields.Char(
        string='N°',
        required=False)
    frais_piece = fields.Many2one(
        comodel_name='hr.expense',
        string='Frais',
        required=False)
