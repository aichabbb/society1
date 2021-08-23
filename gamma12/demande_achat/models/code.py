from odoo import fields,api,models,_
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang



class DemandeAchat(models.Model):
    _name='demande.achat'
    _description="Demande d'achat"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name=fields.Char(string='Référence',index=True, default='New')
    partner_id = fields.Many2one('res.partner',domain=[('supplier','=',True)], string="Fournisseur",track_visibility=True)
    date_commande = fields.Datetime(string="Date de la demande",default=fields.Datetime.now,track_visibility=True)
    demande_line = fields.Many2many('demande.achat.line',string='Articles',track_visibility=True)
    demandeur = fields.Many2one('hr.employee',string='Demandeur',track_visibility=True)
    note = fields.Html('Note',track_visibility=True)
    etat = fields.Selection(
        [('brouillon', 'Brouillon'), ('envoyé', 'Envoyé'), ('validé', 'Validé'), ('annulé', 'Annulé'), ('refusé', 'Refusé')], string='Etat', default="brouillon",
        track_visibility=True)
    date_planned = fields.Datetime(string='Date prévue', compute='_compute_date_planned', store=True, index=True)

    motif_refus = fields.Many2one('motifs.refus',string='Motif de refus')

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id.id)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('demande.achat') or '/'
        return super(DemandeAchat, self).create(vals)

    @api.depends('demande_line.date_planned')
    def _compute_date_planned(self):
        for order in self:
            min_date = False
            for line in order.demande_line:
                if not min_date or line.date_planned < min_date:
                    min_date = line.date_planned
            if min_date:
                order.date_planned = min_date

    @api.multi
    def action_envoyer(self):
        self.etat="envoyé"

    @api.multi
    def action_valider(self):
            self.etat = "validé"

    @api.multi
    def action_refuser(self):
        self.etat = "refusé"

    @api.multi
    def print_demande_d_achat(self):
        return self.env.ref('demande_achat.report_purchase_request').report_action(self)



class DemandeAchatLine(models.Model):
    _name='demande.achat.line'

    name = fields.Text(string='Description', required=True)
    order_id = fields.Many2one('demande.achat')
    product_qty = fields.Float(default=1,string='Quantité', digits=dp.get_precision('Product Unit of Measure'), required=True)
    date_planned = fields.Datetime(string='Date prévue', required=True, index=True)
    product_id = fields.Many2one('product.product', string='Article', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', string='Partner', readonly=True,
                                 store=True)


    @api.multi
    @api.onchange('product_id')
    def onchange_product_id_context(self):
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase


class MotifsRefus(models.Model):
    _name='motifs.refus'

    name = fields.Char()

class MotifsWizard(models.Model):
    _name='motifs.refus.wizard'

    motif = fields.Many2one('motifs.refus')

    @api.multi
    def action_refus_reason_apply(self):
        motif = self.env['demande.achat'].browse(self.env.context.get('active_ids'))
        motif.write({'motif_refus': self.motif.id})
        return motif.action_refuser()
