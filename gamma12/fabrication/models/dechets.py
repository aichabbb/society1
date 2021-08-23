# -*- coding: utf-8 -*-
from odoo import models, fields


class Preparedechets(models.Model):
    _name = "prepdechets"
    _description = 'preparation déchets'
    name = fields.Many2one('product.product', string='Article')
    # dechets_unit = fields.Many2one('product.uom.categ', string='Catégorie d\'unité de mesure')
    pourcentage = fields.Float(string='Pourcentage (%)')
    product_nomenclature = fields.Many2one('manufacture', string='Opération', related="launchmanufacturing_id.product")
    nomps = fields.Char('Nom de production', related="launchmanufacturing_id.nomp")
    launchmanufacturing_id = fields.Many2one('launchmanufacturing')
    state = fields.Selection(
        [('brouillon', 'Brouillon'), ('confirmé', 'Confirmé'), ('enCours', 'en Cours de production'), ('fait', 'Fait')],
        string='Etat', related="launchmanufacturing_id.state", track_visibility=True, copy=False)
    production_ref = fields.Char(string="Référence de production", related='launchmanufacturing_id.name')
