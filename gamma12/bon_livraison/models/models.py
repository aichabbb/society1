# -*- coding: utf-8 -*-

from odoo import models, fields, api


class bon_livraison_inherit(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        if vals.get('echantillon_id'):
            defaults = self.default_get(['name', 'picking_type_id'])
            vals['name'] = self.env['stock.picking.type'].browse(
                vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
        return super(bon_livraison_inherit, self).create(vals)


class table_bon_livraison(models.Model):
    _inherit = 'stock.move'
    name = fields.Char('Description', index=True, required=False)
