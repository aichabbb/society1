from odoo import models, api, fields, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('ia_fabrication', 'Production')])


class InheritStockProductionGamma(models.Model):
    _inherit = "stock.move"

    input_id = fields.Many2one('launchmanufacturing')
    output_id = fields.Many2one('launchmanufacturing')
    ret_id = fields.Many2one('launchmanufacturing', string="Return")
    qty_available = fields.Float(related='product_id.qty_available')
    uom = fields.Many2one('uom.uom', related="product_uom")
    product_fabrication_id = fields.Many2one(related='product_id')
    lot_id = fields.Many2one('stock.production.lot', string="Lot/Numéro de serie")
    default_code = fields.Char()
    locked_override = fields.Boolean(default=False)

    @api.depends('picking_id.is_locked')
    def _compute_is_locked(self):
        for move in self:
            if move.picking_id:
                move.is_locked = move.picking_id.is_locked
            if move.locked_override:
                move.is_locked = move.locked_override

    @api.multi
    def write(self, values):
        res = super(InheritStockProductionGamma, self).write(values)
        msg = ''
        strTable = "<html><ul>"
        if values.get('product_uom_qty'):
            msg = "<li>" + " Qté de l'article " + str(self.product_fabrication_id.name) + ' : ' + str(
                values.get('product_uom_qty')) + "</li>"
        if values.get('lot_id'):
            msg = msg + "<li>" + "\n Lot/numéro de serie  de l'article " + str(
                self.product_fabrication_id.name) + ' : ' + str(values.get('lot_id')) + "</li>"
        strTable = strTable + msg
        strTable = strTable + "</ul></html>"
        if "<li>" in strTable:
            if self.input_id:
                self.input_id.message_post(body=strTable)
            elif self.output_id:
                self.output_id.message_post(body=strTable)
        return res

    def populate_move_lines(self):
        rows = 1
        list_in = []
        if self.product_id.tracking == 'serial':
            rows = int(self.product_uom_qty)
        for row in range(rows):
            list_in.append(
                {'product_id': self.product_id.id, 'product_uom_id': self.product_id.uom_id.id,
                 'location_id': self.location_dest_id.id,
                 'location_dest_id': self.location_id.id, 'move_id': self.id})
        self.move_line_ids = [(5, 0, 0)]
        self.move_line_ids = [(0, 0, line) for line in list_in]
        return list_in

    def show_details_fabrication_IT(self):
        """ Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()
        print(self.env.context)
        if self.env.context['type'] == 'in' and (
                self.input_id.state in ['fait', 'enCours'] or self.ret_id.state in ['fait', 'enCours']):
            self.locked_override = True
        if self.env.context['type'] == 'out' and self.output_id.state in ['fait', 'enCours']:
            self.locked_override = True
        print(self.is_locked, self.state)
        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        view = self.env.ref('stock.view_stock_move_operations')
        picking_type_id = self.env.ref('fabrication.picking_type_fabrication')
        picking_type_id.use_existing_lots = False
        picking_type_id.use_create_lots = False
        if self.env.context['type'] == 'out':
            if self.product_id.tracking != 'serial':
                picking_type_id.use_existing_lots = True
            else:
                picking_type_id.use_create_lots = True
        else:
            picking_type_id.use_existing_lots = True
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_lots_m2o=self.has_tracking != 'none' and (
                        picking_type_id.use_existing_lots or self.state == 'done'),
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.location_id.child_ids and self.picking_type_id.code != 'incoming',
                show_destination_location=self.location_dest_id.child_ids and self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done'
            ),
        }
