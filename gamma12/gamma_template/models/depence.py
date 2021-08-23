# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class depence(models.Model):
    _name = 'depence'

    Désignation = fields.Char(
        string=' Désignation',
        required=True)
    montant = fields.Integer(
        string='Montant', 
        required=False)
    frais = fields.Many2one(
        comodel_name='hr.expense',
        string='Frais',
        required=False)
    # def write(self,vals):
    #
    #     result = super(depence, self).write(vals)
    #
    #
    #     return result
    #
    # @api.model
    # def create(self, vals):
    #
    #
    #     result = super(depence, self).create(vals)
    #     vals.get('frais')
    #     print(vals.get('frais'))
    #
    #
    #
    #     return  result




    