# -*- coding: utf-8 -*-
# from odoo import api, fields, models, tools, _
# encoding: utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OrderFabrication(models.Model):
    _name = "order.fabrication"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    state = fields.Selection([('draft', 'Brouillon'), ('done', 'Envoyé')], string='État', default='draft')
    name = fields.Char('Nom', default='Nouveau', readonly=True)
    date_demande = fields.Datetime('Date de la Demande', required=True, default=fields.datetime.now(),
                                   track_visibility=True)
    demandeur = fields.Many2one('hr.employee', 'Demandeur', track_visibility=True)
    client_id = fields.Many2one('res.partner', 'Client', domain="[('customer', '=', True)]", track_visibility=True)
    date_fin_prevu = fields.Datetime('Date fin prévu', required=True, track_visibility=True)
    description = fields.Text('Motif de commande', track_visibility=True)
    articlel_list = fields.One2many('product.list', 'order_in_id', store=True, states={'draft': [('readonly', False)]})
    product_list = fields.One2many('product.list', 'order_out_id', store=True, states={'draft': [('readonly', False)]})
    operation = fields.Many2one('manufacture', string='Opération', track_visibility='onchange', required=True,
                                sotre=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)
    sale_order_id = fields.Many2one('sale.order', 'Devis', required=False)
    product_uom_id = fields.Many2one('uom.uom', 'Unité de mesure',
                                     default=lambda self: self.env['uom.uom'].search([], limit=1, order='id').id)
    stock_intern_id = fields.Many2one('stock.location', string='stock interne',
                                      default=lambda self: self.env['stock.location'].search(
                                          [('usage', '=', 'internal')], limit=1, order='id').id)
    stock_externe_id = fields.Many2one('stock.location', string='stock externe',
                                       default=lambda self: self.env['stock.location'].search(
                                           [('is_location_of_fabrication_it', '=', True)], limit=1, order='id').id)
    so_ids = fields.Many2many('sale.order', compute="get_sos")

    # TODO:To Remove
    id_relation = fields.Many2one(comodel_name='launchmanufacturing', string='production', required=False)
    related_move_fabrication_ids = fields.One2many(related='id_relation.move_fabrication_ids', string='in',
                                                   required=False)
    related_move_fabrication_out_ids = fields.One2many(related='id_relation.move_fabrication_output_ids', string='out',
                                                       required=False)

    # ==============================================
    is_production = fields.Boolean(string='Is_production', required=False, default=False)
    note_fab = fields.Text(string="Note", required=False)

    @api.one
    @api.depends('client_id')
    def get_sos(self):
        all_sales = self.env['sale.order'].search([]).ids
        if self.client_id:
            sales = self.env['sale.order'].search([('partner_id', '=', self.client_id.id)]).ids
            if self.sale_order_id and self.sale_order_id.id not in sales:
                self.sale_order_id = None
            self.so_ids = [(6, 0, sales)]
        else:
            self.so_ids = [(6, 0, all_sales)]

    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        """append the nomenclatures of the operation"""
        for line in self:
            line.product_list = ''
            listP = []
            if line.sale_order_id:
                if line.sale_order_id.order_line:
                    line.client_id = line.sale_order_id.partner_id
                    for prod in line.sale_order_id.order_line:
                        if prod.product_id.type != 'service':
                            listP.append({'product_id': prod.product_id.id,
                                          'order_out_id': self.id,
                                          'qty': prod.product_uom_qty})
                    line.product_list = listP

    @api.onchange('operation')
    def onchange_sale_operation(self):
        """append the nomenclatures of the operation"""
        for line in self:
            listP = []
            line.articlel_list = ''
            if line.operation:
                listProd = line.operation.articles_id
                if listProd:
                    for prodTmp in listProd:
                        for prod in self.env['product.product'].search([('product_tmpl_id', '=', prodTmp.id)]):
                            if prod.type != 'service':
                                listP.append({'product_id': prod.id,
                                              'product_uom': prodTmp.uom_id.id,
                                              'name': prodTmp.name,
                                              'qty_available': prodTmp.qty_available,
                                              'default_code': prodTmp.default_code,
                                              'order_in_id': self.id,
                                              })
                    line.articlel_list = listP

    @api.multi
    def production_views(self):
        return {
            'name': _('Production'),
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('order_fabrication_id', '=', self.id)],
            # 'res_id': self.env['launchmanufacturing'].search([('order_fabrication_id', '=', self.id)], limit=1).id,
            'res_model': 'launchmanufacturing',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('fabrication.launchmanufacturing_tree_OF').id, 'tree'),
                      (self.env.ref('fabrication.launchmanufacturing_form_OF').id, 'form')],
        }

    def onchange_product(self):
        for line in self:
            listP = []
            if line.articlel_list:
                for prod in line.articlel_list:
                    if prod.product_id.type != 'service':
                        listP.append({'product_id': prod.product_id.id,
                                      'product_uom': prod.product_id.uom_id.id,
                                      'name': prod.product_id.name,
                                      'qty_available': prod.qty_available,
                                      'product_uom_qty': prod.qty,
                                      'date': line.date_demande,
                                      'location_dest_id': line.stock_externe_id.id,
                                      'location_id': line.stock_intern_id.id,
                                      'date_expected': line.date_fin_prevu,
                                      'company_id': line.company_id.id})
                return listP

    @api.multi
    def confirm_order(self):
        if self.sale_order_id and self.sale_order_id.state != 'sale':
            raise UserError(_('Il faut d\'abord confirmer le devis.'))
        self.is_production = True
        for line in self:
            listP = []
            if line.product_list:
                for prod in line.product_list:
                    if prod.product_id.type != 'service':
                        listP.append({'product_id': prod.product_id.id,
                                      'product_uom': prod.product_id.uom_id.id,
                                      'product_uom_qty': prod.qty,
                                      'name': prod.product_id.name,
                                      'date': line.date_demande,
                                      'location_dest_id': line.stock_intern_id.id,
                                      'location_id': line.stock_externe_id.id,
                                      'date_expected': line.date_fin_prevu,
                                      'company_id': line.company_id.id})
            prod_id = self.env['launchmanufacturing'].create(
                {'nomp': line.name, 'client': line.client_id.id, 'product': line.operation.id, 'order_id': line.id,
                 'responsable': self.demandeur.id, 'devis': self.sale_order_id.id, 'order_fabrication_id': line.id})
            for ln in listP:
                prod_id.move_fabrication_output_ids = [(0, 0, ln)]
            for ln in line.onchange_product():
                prod_id.move_fabrication_ids = [(0, 0, ln)]
            # self.id_relation = prod_id
            if not line.product_list:
                raise UserError(_('Veuillez Ajouter Des Produit finis.'))
        line.state = "done"
        return {
            'name': _('Production'),
            'view_mode': 'form',
            'target': 'current',
            'domain': [('order_fabrication_id', '=', self.id)],
            'res_id': prod_id.id,
            'res_model': 'launchmanufacturing',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('fabrication.launchmanufacturing_form_OF').id, 'form')],
        }

    @api.multi
    def create_plus_production(self):
        self.is_production = True
        for line in self:
            list_out = []
            list_in = []
            if line.product_list:
                for prod in line.product_list:
                    if prod.product_id.type != 'service':
                        qty = prod.qty - prod.qty_done
                        list_out.append({'product_id': prod.product_id.id,
                                         'product_uom': prod.product_id.uom_id.id,
                                         'product_uom_qty': qty if qty >= 0 else 0,
                                         'name': prod.product_id.name,
                                         'date': line.date_demande,
                                         'location_dest_id': line.stock_intern_id.id,
                                         'location_id': line.stock_externe_id.id,
                                         'date_expected': line.date_fin_prevu,
                                         'company_id': line.company_id.id})
            if line.articlel_list:
                for prod in line.articlel_list:
                    if prod.product_id.type != 'service':
                        list_in.append({'product_id': prod.product_id.id,
                                        'product_uom': prod.product_id.uom_id.id,
                                        'name': prod.product_id.name,
                                        'qty_available': prod.qty_available,
                                        'product_uom_qty': 0,
                                        'date': line.date_demande,
                                        'location_dest_id': line.stock_externe_id.id,
                                        'location_id': line.stock_intern_id.id,
                                        'date_expected': line.date_fin_prevu,
                                        'company_id': line.company_id.id})
            prod_id = self.env['launchmanufacturing'].create(
                {'nomp': line.name, 'client': line.client_id.id, 'product': line.operation.id, 'order_id': line.id,
                 'responsable': self.demandeur.id, 'devis': self.sale_order_id.id, 'order_fabrication_id': line.id,
                 'plus_production': True})
            for ln in list_out:
                prod_id.move_fabrication_output_ids = [(0, 0, ln)]
            for ln in list_in:
                prod_id.move_fabrication_ids = [(0, 0, ln)]
            # self.id_relation = prod_id
            if not line.product_list:
                raise UserError(_('Veuillez Ajouter Des Produit finis.'))
        # line.state = "done"
            return {
                'name': _('Production'),
                'view_mode': 'form',
                'target': 'current',
                'domain': [('order_fabrication_id', '=', self.id)],
                'res_id': prod_id.id,
                'res_model': 'launchmanufacturing',
                'type': 'ir.actions.act_window',
                'views': [(self.env.ref('fabrication.launchmanufacturing_form_OF').id, 'form')],
            }

    @api.multi
    def brouillon(self):
        self.state = "draft"

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouveau') == 'Nouveau':
            vals['name'] = self.env['ir.sequence'].next_by_code('order.fabrication') or '/'
        print(vals.get('operation'))
        return super(OrderFabrication, self).create(vals)

    # function that prints the fabrication order
    @api.multi
    def print_ordre_fabrication(self):
        return self.env.ref('fabrication.order_fabrication_pdf').report_action(self)


class ProductList(models.Model):
    _name = "product.list"

    product_id = fields.Many2one('product.product', 'Article', store=True)  # 'Désignation'
    qty = fields.Integer('Quantité', store=True)
    qty_done = fields.Integer('Quantité traité', store=True)
    qty_available = fields.Integer('Quantité en stock', store=True)
    order_in_id = fields.Many2one('order.fabrication', store=True, ondelete="cascade")
    order_out_id = fields.Many2one('order.fabrication', store=True, ondelete="cascade")
