# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPickingTypeFabrication(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('ia_fabrication', 'Production')])
    count_of_todo = fields.Integer(string="Number of Manufacturing Orders to Process",
        compute='_get_of_count') #compute='_get_of_count'
    count_of_waiting = fields.Integer(string="Number of Manufacturing Orders Waiting",
        compute='_get_of_count')
    count_of_late = fields.Integer(string="Number of Manufacturing Orders Late",
        compute='_get_of_count')

    def _get_of_count(self):
        of_picking_types = self.filtered(lambda picking: picking.code == 'ia_fabrication')
        if not of_picking_types:
            return
        domains = {
            'count_of_waiting': [('state', '=', 'confirmé')],
            'count_of_todo': [('state', 'in', ('confirmé', 'enCours'))],
            'count_of_late': [('date', '<', fields.Date.today()), ('state', '=', 'confirmé')],
        }
        for field in domains:
            data = self.env['launchmanufacturing'].read_group(domains[field] +
                [('state', 'not in', ('fait', 'cancel')), ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['picking_type_id'])
            count = {x['picking_type_id'] and x['picking_type_id'][0]: x['picking_type_id_count'] for x in data}
            for record in of_picking_types:
                record[field] = count.get(record.id, 0)

    def get_fabrication_stock_picking_action_picking_type(self):
        return self._get_action('fabrication.launchmanufacturing_action')
