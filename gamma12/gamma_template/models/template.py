# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import exceptions
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError, UserError, RedirectWarning


class template(models.Model):
    _inherit = 'hr.expense'

    cin = fields.Char(related='employee_id.CIN',
                      string='Cin',
                      required=False)
    nombre_personnne = fields.Integer(
        string='Nombre de personne',
        required=False)
    Désignation = fields.Char(
        string='Désignation',
        required=False)

    Projet = fields.Many2one(
        comodel_name='project.project',
        string='Projet',
        required=False)

    Montant_total = fields.Monetary(compute='_amount_all', store=True,
                                    string='Montant total',
                                    required=False)

    @api.depends('depence.montant')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = 0.0
            for line in order.depence:
                amount_untaxed += line.montant

            order.update({

                'Montant_total': amount_untaxed,
            })
     
    total_amount = fields.Monetary("Total", compute='_compute_amount', store=True, currency_field='currency_id', tracking=True)

    tst_mantant = fields.Boolean(compute='_mantant',
        string='Tst_mantant',
        required=False)

    @api.depends('total_amount','Montant_total')
    def _mantant(self):
        for var in self:
            if var.Montant_total == var.total_amount or var.Montant_total == 0:
               var.tst_mantant = True
            else:
                var.tst_mantant = False







    depence = fields.One2many(
        comodel_name='depence',
        inverse_name='frais',
        string='Depence')
    piece = fields.One2many(
        comodel_name='piece',
        inverse_name='frais_piece',
        string='Depence')

    moyen_trasport = fields.Char(
        string='Moyen de transport ',
        required=False)

    Mission = fields.Text(
        string=' Mission',
        required=False)
    cheque = fields.Char(
        string='Chéque',
        required=False)
    pv = fields.Char(
        string='PV de reception',
        required=False)
    effect = fields.Char(
        string='Effet',
        required=False)
