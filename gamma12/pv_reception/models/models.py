# -*- coding: utf-8 -*-

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo import api, fields, models, exceptions, _
from datetime import datetime, time


class ligne_pv_reception(models.Model):
    _name = 'pv.line'
    _description = "PV DE RECEPTION"

    virtual_list = fields.Many2one('pv.reception')

    id_order_line = fields.Integer()
    des = fields.Char(string="Designation")
    qte = fields.Float(string="Quantité", )
    lot_ids = fields.Many2one(comodel_name='stock.production.lot', string='Lot/numéro de série',
                              required=False)


class pv_reception(models.Model):
    _name = 'pv.reception'
    _description = "PV DE RECEPTION"
    _rec_name = "num_pv"

    num_pv = fields.Char(required=True, index=True, copy=False, default='Nouveau', readonly=True)
    num_commande = fields.Many2one('sale.order', string="N° commande", readonly=True)
    nclient = fields.Many2one('res.partner', 'N° client', readonly=True)
    lieu_livraison = fields.Text(string="Lieu de livraison")
    ligne_commande = fields.One2many('pv.line', 'virtual_list')
    state = fields.Selection([
        ('brouillon', 'À soumettre'),
        ('confirmer', 'confirmé')], default="brouillon")
    # adress_pv = fields.Char(string='Lieu de livraison', required=False)
    adress_pv = fields.Char('Lieu de livraison', related='nclient2.address_client', readonly=False)
    # adress_pv = fields.Many2one('res.partner', 'Lieu de livraison',)
    # contact_client = fields.char(string='Lieu de livraison', related="contact_client.street2")compute='compute_contact_client'

    nclient2 = fields.Many2one('res.partner', 'N° client ', domain="[('id', 'in',client_m2m)]")
    client_m2m = fields.Many2many(comodel_name='res.partner', string='')

    @api.model
    def create(self, values):
        if values.get('num_pv', 'Nouveau') == 'Nouveau':
            values['num_pv'] = self.env['ir.sequence'].next_by_code('pv.reception') or '/'
        res = super(pv_reception, self).create(values)
        for lines in res:
            data = self.env['sale.order'].search([('id', '=', lines.num_commande.id)])
            if data:
                for line in data.order_line:
                    for lin_t in lines.ligne_commande:
                        if lin_t.id_order_line == line.id:
                            if lin_t.qte > line.product_uom_qty - line.qte_pv_fait:
                                raise ValidationError("La quantité saisie a dépassé le montant restant")

        return res

    def valider(self):
        total_pv = 0.0
        for lines in self:
            data = self.env['sale.order'].search([('id', '=', lines.num_commande.id)])
            if data:
                for line in data.order_line:
                    if line.product_uom_qty != line.qte_pv_fait:
                        for lin_t in lines.ligne_commande:
                            if lin_t.id_order_line == line.id:

                                if lin_t.qte > line.product_uom_qty - line.qte_pv_fait:
                                    raise ValidationError("La quantité saisie a dépassé le montant restant")
                                else:
                                    lines.state = "confirmer"
                                    if line.qte_pv_fait != 0.0:
                                        total_pv = line.qte_pv_fait + lin_t.qte
                                    else:
                                        total_pv = lin_t.qte
                                line.write({'qte_pv_fait': total_pv})
            else:
                data.order_line.write({'qte_pv_fait': 0.0})


class line_bon_commande(models.Model):
    _inherit = 'sale.order.line'
    qte_pv_fait = fields.Float()
    pt = fields.Float()


class bon_commande(models.Model):
    _inherit = 'sale.order'

    num_pv = fields.One2many('pv.reception', 'num_commande')
    qte_pv_fait = fields.Float()
    bool_pv = fields.Boolean(compute="bool_botton_pv")
    is_pv = fields.Boolean(compute="pv_invisible")

    def pv_invisible(self):
        reception = self.env['pv.reception'].search([('num_commande', '=', self.id)])
        if len(reception) >= 1:
            self.is_pv = True

    def bool_botton_pv(self):
        for lin in self:
            for line in lin.order_line:
                # print(line.qte_pv_fait)
                # qte_t_pv=line.product_uom_qty-line.qte_pv_fait
                if line.product_uom_qty != line.qte_pv_fait:
                    lin.bool_pv = True

    @api.multi
    def liste_pv(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'PV de reception',
            'res_model': 'pv.reception',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('num_commande', '=', self.id)]
        }

    def pv_button(self):
        liste_order = []
        list_client = []
        for lin in self:
            for line in lin.order_line:
                lots = self.env['stock.production.lot'].search([('id', '=', line.product_id.id)])
                # print(line.qte_pv_fait)
                qte_t_pv = line.product_uom_qty - line.qte_pv_fait
                if line.qte_pv_fait != 0:
                    if qte_t_pv > 0:
                        liste_order.append({'id_order_line': line.id, 'des': line.name, 'qte': qte_t_pv,
                                            'lot_ids': lots.id if lots else False})
                else:
                    liste_order.append({'id_order_line': line.id, 'des': line.name, 'qte': line.product_uom_qty,
                                        'lot_ids': lots.id if lots else False})
            for i in lin.partner_id.child_ids:
                list_client.append(i.id)
            list_client.append(lin.partner_id.id)
            print(list_client)
            return {
                'name': ("PV"),
                'domain': [('num_pv', '=', self.id)],
                'view_type': 'form',
                'res_model': 'pv.reception',
                'view_id': False,
                'view_mode': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'default_num_commande': self.id, 'default_nclient': self.partner_id.id,
                            'default_nclient2': self.partner_id.id, 'default_client_m2m': [(6, 0, list_client)],
                            'default_ligne_commande': [(0, 0, line_liste) for line_liste in liste_order]
                            }
            }


class NewModuleRespartner(models.Model):
    _inherit = 'res.partner'

    address_client = fields.Char('Address', compute='compute_contact_client')

    @api.multi
    def compute_contact_client(self):
        for line in self.search([]):
            address_street = ''
            address_street2 = ''
            address_city = ''
            address_zip = ''
            address_country = ''
            if line:
                if line.street:
                    address_street = line.street
                if line.street2:
                    address_street2 = line.street2
                if line.city:
                    address_city = line.city
                if line.zip:
                    address_zip = line.zip
                if line.country_id:
                    address_country = line.country_id.name

            line.address_client = address_street + ' ' + address_street2 + ' ' + address_city + ' ' + address_zip + ' ' + address_country
