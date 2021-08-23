from odoo import models,fields,api,exceptions


class Generator(models.Model):

    _name="generator"

    name = fields.Char('serves for nothing')

    @api.multi
    def generate_sequences(self):
        concerned_model = self.env['launchmanufacturing'].search([])
        for item in concerned_model:
            if item.name == 'New':
                item.name = self.env['ir.sequence'].next_by_code('fabrication.it') or '/'

    @api.multi
    def action_so(self):
        existed_sos = []
        records_production = self.env['launchmanufacturing'].search([])
        check_sos = self.env['launchmanufacturing'].search([])
        productions = []

        for rec in self.env['production.devis'].search([]):
            rec.unlink()

        for record in check_sos:
            if record.devis.id and record.devis.id not in existed_sos:
                existed_sos.append(record.devis.id)

        records = self.env['sale.order'].search([('id', 'in', existed_sos)])

        for record in records:
            self.env['production.devis'].create({'devis': record.id})

        for record in records_production:
            productions.append({'name' : record.name,
                                'devis': record.devis.id,
                                'date': record.date,
                                'client': record.client.id,
                                'state': record.state,
                                'operation': record.product.id,
                                'nomp': record.nomp})

        for record in self.env['production.devis'].search([]):
            for line in productions:
                if record.devis.id == line['devis']:
                    record.productions_ids = [line]
















