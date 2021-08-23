from odoo import models,fields,api,exceptions


class Removing_locations(models.Model):

    _name="remove.location"

    def _get_default_location_dest(self):
        """get the default location_dest_id """

        return self.env['stock.location'].search([('is_location_of_fabrication_it', '=', True)], limit=1, order='id').id

    but = fields.Many2one('product.product',string='fix specified')
    remove_all = fields.Boolean(string='fix all')
    move = fields.Many2many('stock.move')
    date = fields.Date()
    location_id = fields.Many2one('stock.location')
    location_dest=fields.Many2one('stock.location',string='destination',default=_get_default_location_dest)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('stock.move'),
        index=True, required=True)

    @api.multi
    def fix(self):
        for rule in self.move:
            rule.quantity_done = rule.product_uom_qty
            rule._action_done()

        concerned=[]

        for item in self.move:
            concerned.append(item.product_id.id)

        records= self.env["stock.quant"].search([("location_id","=",15),("product_id","in",concerned)])
        for record in records:
                record.unlink()

    @api.multi
    def show_stuff(self):
        for line in self.move:
            line.unlink()
        stuffs = []
        if self.remove_all:
            records = self.env["stock.quant"].search([("location_id", "=", 15)])
            for record in records:
                if record.quantity > 0:
                    stuffs.append({'product_id':record.product_id.id,
                                   'product_uom_qty':record.quantity,
                                   'product_uom': record.product_id.uom_id.id,
                                   'name': record.product_id.name,
                                   'date': self.date,
                                   'location_dest_id': self.location_id.id,
                                   'location_id': self.location_dest.id,
                                   'date_expected': self.date,
                                   'company_id': self.company_id.id
                                   })
                else:
                    stuffs.append({'product_id': record.product_id.id,
                                   'product_uom_qty': -record.quantity,
                                   'product_uom': record.product_id.uom_id.id,
                                   'name': record.product_id.name,
                                   'date': self.date,
                                   'location_dest_id': self.location_dest.id,
                                   'location_id': self.location_id.id,
                                   'date_expected': self.date,
                                   'company_id': self.company_id.id
                                   })
            self.move=stuffs

        else:
            if self.but:
                records = self.env["stock.quant"].search([("location_id", "=", 15),("product_id", "=", self.but.id)])
                for record in records:
                    if record.quantity > 0:
                        stuffs.append({'product_id': record.product_id.id,
                                       'product_uom_qty': record.quantity,
                                       'product_uom': record.product_id.uom_id.id,
                                       'name': record.product_id.name,
                                       'date': self.date,
                                       'location_dest_id': self.location_id.id,
                                       'location_id': self.location_dest.id,
                                       'date_expected': self.date,
                                       'company_id': self.company_id.id
                                       })
                    else:
                        stuffs.append({'product_id': record.product_id.id,
                                       'product_uom_qty': -record.quantity,
                                       'product_uom': record.product_id.uom_id.id,
                                       'name': record.product_id.name,
                                       'date': self.date,
                                       'location_dest_id': self.location_dest.id,
                                       'location_id': self.location_id.id,
                                       'date_expected': self.date,
                                       'company_id': self.company_id.id
                                       })
            else:
                raise exceptions.ValidationError('Please choose one')
            self.move = stuffs





