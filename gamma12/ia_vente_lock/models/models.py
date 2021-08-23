# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InheritModuleStockPicking(models.Model):
    _inherit = 'stock.picking'

    is_blocked = fields.Boolean(string='Is_blocked', required=False, compute='compute_state_blocked')

    @api.multi
    @api.depends('is_blocked')
    def compute_state_blocked(self):
        sale_order_id = self.env['sale.order'].search([('state', '=', 'done')])
        if sale_order_id:
            for line in sale_order_id:
                for id in line.picking_ids:
                    id.is_blocked = True


class InheritModuleSaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_done(self):
        for line in self.picking_ids:
            line.do_unreserve()
        return super(InheritModuleSaleOrder, self).action_done()
