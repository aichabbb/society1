# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
import lxml
from lxml import etree
from odoo import api, fields, models, exceptions, _


class Manufacture(models.Model):
    _name = "manufacture"
    _rec_name = "product"
    _description = 'manufacture'
    product = fields.Char(string='Opération')
    articles_id = fields.Many2many('product.template', string='Articles')

    _sql_constraints = [
        ('product_uniq', 'unique(product)', "This product is already exist !"),
    ]


class LaunchManufacturing(models.Model):
    _name = "launchmanufacturing"
    _description = 'Fabrication'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _default_picking_type_id(self):
        return self.env['stock.picking.type'].search([('code', '=', 'ia_fabrication')], limit=1).id
    # ,('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])
    def _get_default_location(self):
        """get the default location_id """
        return self.env['stock.location'].search([('usage', '=', 'internal')], limit=1, order='id').id

    def _get_default_location_dest(self):
        """get the default location_dest_id """
        return self.env['stock.location'].search([('is_location_of_fabrication_it', '=', True)], limit=1, order='id').id

    name = fields.Char(string="Ref", default='New', copy=False)
    articles = fields.Char(string="articles")
    product = fields.Many2one('manufacture', string='Opération', track_visibility=True)
    # product_order = fields.Many2one('order.fabrication')
    state = fields.Selection(
        [('brouillon', 'Brouillon'), ('confirmé', 'Confirmé'), ('enCours', 'en Cours de production'), ('fait', 'Fait')],
        string='Etat', default='brouillon', track_visibility=True, copy=False)
    nomp = fields.Char(string='Nom de production', track_visibility=True)
    client = fields.Many2one('res.partner', track_visibility=True)
    devis = fields.Many2one('sale.order', track_visibility=True, readonly=True)
    date = fields.Datetime(string='Date de production', track_visibility=True, default=fields.Datetime.now)
    names = fields.Char(string='Produits fabriqués', track_visibility=True)
    dechet_ids = fields.One2many('prepdechets', 'launchmanufacturing_id', string="Déchets")
    message = fields.Boolean(default=False)
    message_cnt = fields.Char()
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)

    move_fabrication_ids = fields.One2many('stock.move', 'input_id', string="Input", track_visibility=True)
    move_fabrication_return_ids = fields.One2many('stock.move', 'ret_id', string="Return", track_visibility=True)
    move_fabrication_output_ids = fields.One2many('stock.move', 'output_id', string="Output", track_visibility=True)
    stock_intern_id = fields.Many2one('stock.location', string='stock interne', default=_get_default_location)
    stock_externe_id = fields.Many2one('stock.location', string='stock externe', default=_get_default_location_dest)
    is_multi_warehouse = fields.Boolean(compute='check_warehouse_count')
    input_processed = fields.Boolean('input Readonly Field', default=False)
    output_processed = fields.Boolean('output Readonly Field', default=False)

    responsable = fields.Many2one('hr.employee', 'Responsable')
    plus_production = fields.Boolean(string='production Ajouter', default=False)
    order_fabrication_id = fields.Many2one('order.fabrication')
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', default=_default_picking_type_id, required=True)
    # picking_type_id = fields.Many2one(comodel_name='stock.picking.type', compute='get_picking_id',string='Picking_type_id', strore=True, required=False)

    def get_picking_id(self):
        self.picking_type_id = self.env.ref('fabrication.picking_type_fabrication')

    @api.one
    def check_warehouse_count(self):
        internal_warehouse_count = self.env['stock.location'].search_count([('usage', '=', 'internal')])
        for line in self:
            """check if the company is a multi warehouse"""
            if internal_warehouse_count > 1:
                line.is_multi_warehouse = True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fabrication.it') or '/'

        return super(LaunchManufacturing, self).create(vals)

    @api.onchange('stock_intern_id')
    def stock_interne(self):
        """select the default location_id in all the input products"""
        for line in self:
            for rule in line.move_fabrication_ids:
                rule.location_id = line.stock_intern_id.id

    @api.onchange('stock_externe_id')
    def stock_externe(self):
        """select the default location_dest_id  in all the input products"""
        for line in self:
            for rule in line.move_fabrication_ids:
                rule.location_dest_id = line.stock_externe_id.id

    @api.onchange('move_fabrication_output_ids')
    def move_fabrication_raw(self):
        """select the default location_id and location_dest_id in all the output products"""
        for line in self:
            for rule in line.move_fabrication_output_ids:
                rule.location_id = line.stock_externe_id.id
                rule.location_dest_id = line.stock_intern_id.id

    @api.multi
    def write(self, vals):

        x = vals.get('move_fabrication_ids')
        if x:
            ord = self.order_fabrication_id.product_list
        return super(LaunchManufacturing, self).write(vals)

    @api.onchange('move_fabrication_ids')
    def onchange_child(self):
        for line in self:
            """the return message will be gone when changing something in the input """
            line.message = False

    def check_quantity(self):
        list_of_insuffisante = []
        for rec in self.move_fabrication_ids:
            if rec.product_uom_qty and rec.product_uom_qty > rec.product_id.qty_available and rec.product_id.type == 'product':
                list_of_insuffisante.append(rec.product_id.partner_ref)
        return list_of_insuffisante

    @api.one
    def checkQuantity(self):
        """check if the quantity of each product is suffisant"""
        self.message = False
        self.move_fabrication_return_ids = [(5, 0, 0)]
        listReturn = []
        for move in self.move_fabrication_ids:
            listReturn.append(self._prepare_move_default_values_return(move))
        for ln in listReturn:
            self.move_fabrication_return_ids = [(0, 0, ln)]
        for rule in self.move_fabrication_return_ids:
            rule._action_confirm()._action_assign()
        result_final = ', '.join(map(str, self.check_quantity()))

        """append the insuffisante products in list_of_insuffisante"""
        if self.check_quantity():
            raise exceptions.ValidationError(_('Quantité insuffisante dans le stock : %s') % (result_final))

        """if none operation is selected then raise a message"""
        if not self.product:
            raise exceptions.ValidationError('Sélectionnez une opération')

        """if no quantity is reserved raise a message"""
        quantity_needed = 0
        for qty in self.move_fabrication_ids:
            quantity_needed = qty.product_uom_qty + quantity_needed
        if quantity_needed == 0 and not self.plus_production:
            raise exceptions.ValidationError(_("Aucune quantité n'a été saisie"))

        """if the date is not before this day raise a message"""
        today = fields.Datetime.now()
        if self.date:
            if self.date > today:
                self.state = 'brouillon'
                raise exceptions.ValidationError('la date doit être avant ce jour ! ')

        self.state = "confirmé"

        """if everything is fine and the process got in this line then reserve the quatities"""
        for rule in self.move_fabrication_ids:
            rule._action_confirm()
            rule._action_assign()

    @api.multi
    def annuler_reservation(self):
        """action to cancel the reservation"""
        for rule in self.move_fabrication_ids:
            rule._do_unreserve()
            rule._action_cancel()
            self.state = "brouillon"

    @api.multi
    def cancel_production(self):
        """action to cancel the production"""
        for rule in self.move_fabrication_ids:
            rule._do_unreserve()
            rule._action_cancel()

        for rule in self.move_fabrication_output_ids:
            rule._do_unreserve()
            rule._action_cancel()
        self.state = "brouillon"

    """ onchange_de and onchange_devis make the selection easier, if you select a client you'll have only the 
        the quotations draft and sent related to this client, and if you selected the devis you'll have the client 
        auto selected in the other field"""

    @api.one
    def validating(self):
        """function to validate the production"""
        self.message = False
        prods = self.env['launchmanufacturing'].search(
            [('order_fabrication_id', '=', self.order_fabrication_id.id), ('state', '=', 'enCours')])
        if prods:
            raise exceptions.ValidationError('Une Autre Production En cours')
        self.message_cnt = ', '.join(map(str, self.check_quantity()))
        if self.check_quantity():
            """show the insuffisant product in a message(you'll find it in manufacture.xml) and go back to draft and 
               cancel the production """
            self.message = True
            self.state = 'brouillon'
            for rule in self.move_fabrication_ids:
                rule._action_cancel()
            return
        for rule in self.move_fabrication_ids:
            for rec in rule.move_line_ids:
                rec._action_done()
                rec.write({'state': 'done', 'date': fields.Datetime.now()})
            rule.write({'state': 'done', 'date': fields.Datetime.now()})

        """if all alright, append the finished products in the list rell then to the field hta shows it (names)"""
        rell = []
        for child in self.move_fabrication_output_ids:
            rell.append(child.product_id.partner_ref)

        self.names = ", ".join(map(str, rell))

        """check if the there's  trash and output """

        ress = 0
        ress2 = 0
        for item in self.move_fabrication_output_ids:
            ress = item.product_uom_qty + ress
        for item1 in self.dechet_ids:
            ress2 = item1.pourcentage + ress2

        """check if the date is before this date"""

        today = fields.Datetime.now()
        if self.date:
            if self.date > today:
                raise exceptions.ValidationError('la date doit être avant ce jour ! ')
        """if there's an output or trash then add the quantity of output to estimated quantity of the product, 
           else show a message"""
        if (self.move_fabrication_output_ids and ress > 0) or (self.dechet_ids and ress2 > 0):
            self.state = 'enCours'
        else:
            raise exceptions.ValidationError('la sortie de la production est null, aucun output ou déchet')

        for move in self.move_fabrication_output_ids:
            if move.product_id.tracking == 'serial':
                for i in range(0, int(move.product_uom_qty)):
                    self.env['stock.move.line'].create(move._prepare_move_line_vals(quantity=1))
                move._action_confirm()
            else:
                move._action_confirm()._action_assign()

    def _prepare_move_default_values_return(self, return_line):
        vals = {
            'product_id': return_line.product_id.id,
            'name': return_line.product_id.name,
            'ret_id': self.id,
            'product_uom_qty': 0,
            'product_uom': return_line.product_id.uom_id.id,
            'state': 'draft',
            'date_expected': fields.Datetime.now(),
            'location_id': return_line.location_dest_id.id,
            'location_dest_id': return_line.location_id.id,
            'picking_type_id': return_line.picking_type_id.id,
            'origin_returned_move_id': return_line.id,
            'procure_method': 'make_to_stock',
        }
        return vals

    @api.one
    def mark_as_done(self):
        """add the quantity to stock of each output and substract from the input quantity in the stock, and add the
           trash if there's any, finnaly mark it as done"""
        self.message = False
        self.message_cnt = ', '.join(map(str, self.check_quantity()))

        for rule in self.move_fabrication_output_ids:
            rule.picking_type_id = self.env.ref('fabrication.picking_type_fabrication')
            for rec in rule.move_line_ids:
                rec.picking_type_id = self.env.ref('fabrication.picking_type_fabrication')
                if rec.product_id.tracking != 'serial':
                    rec.picking_type_id.use_existing_lots = True
                else:
                    rec.picking_type_id.use_create_lots = True
                rec._action_done()
            rule.write({'state': 'done', 'date': fields.Datetime.now()})

        if not sum(x.product_uom_qty for x in self.move_fabrication_return_ids) == 0:
            for rule in self.move_fabrication_return_ids:
                rule.picking_type_id = self.env.ref('fabrication.picking_type_fabrication')
                if rule.product_uom_qty != 0:
                    for rec in rule.move_line_ids:
                        rec.picking_type_id = self.env.ref('fabrication.picking_type_fabrication')
                        rec.picking_type_id.use_existing_lots = True
                        rec._action_done()
                        rec.write({'state': 'done', 'date': fields.Datetime.now()})
                rule.write({'state': 'done', 'date': fields.Datetime.now()})

        for qty_pr_out in self.move_fabrication_output_ids:
            prod = qty_pr_out.product_fabrication_id
            prod_traite = qty_pr_out.quantity_done
            for od_out in self.order_fabrication_id.product_list:
                if od_out.product_id == prod:
                    od_out.qty_done += prod_traite
        self.state = 'fait'

    @api.multi
    def unlink(self):
        """there's no way to delete a production if it'snt in draft state"""
        if any(move.state not in ['brouillon'] for move in self):
            raise UserError(_('Vous pouvez supprimer que les productions en etat brouillon'))
        return models.Model.unlink(self)

    @api.multi
    def print_ordre_production(self):
        return self.env.ref('fabrication.production_pdf').report_action(self)

    @api.multi
    def check_output_qty_reached(self):
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
            self.id_relation = prod_id
            if not line.product_list:
                raise UserError(_('Veuillez Ajouter Des Produit finis.'))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(LaunchManufacturing, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                  toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form' and 1==1:
            for node_form in doc.xpath("//form"):
                node_form.set("create", 'true')
            res['arch'] = etree.tostring(doc)
        return res
