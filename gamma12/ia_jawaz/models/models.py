# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FleetVehicleLogJawaz(models.Model):
    _name = 'fleet.vehicle.jawaz'
    _description = 'Suivi de la carte jawaz'
    _inherits = {'fleet.vehicle.cost': 'cost_id'}
    _rec_name = 'vehicle_id'

    @api.model
    def default_get(self, default_fields):
        res = super(FleetVehicleLogJawaz, self).default_get(default_fields)
        service = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
        res.update({
            'date': fields.Date.context_today(self),
            'cost_subtype_id': service and service.id or False,
            'cost_type': 'fuel'
        })
        return res

    purchaser_id = fields.Many2one('res.partner', 'Acheteur',
                                   domain="['|',('customer','=',True),('employee','=',True)]")
    inv_ref = fields.Char('Invoice Reference', size=64)
    vendor_id = fields.Many2one('res.partner', 'Vendor', domain="[('supplier','=',True)]")
    notes = fields.Text()
    cost_id = fields.Many2one('fleet.vehicle.cost', 'Cost', required=True, ondelete='cascade')
    # we need to keep this field as a related with store=True because the graph view doesn't support
    # (1) to address fields from inherited table
    # (2) fields that aren't stored in database
    cost_amount = fields.Float(related='cost_id.amount', string='Amount', store=True, readonly=False)

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if self.vehicle_id:
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id


class NewModule(models.Model):
    _inherit = 'fleet.vehicle'

    jawaz_count = fields.Integer(compute="_compute_count_all_jawaz", string='Jawaz Count')

    @api.multi
    def return_action_to_open_jawaz(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('ia_jawaz', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    def _compute_count_all_jawaz(self):
        jawaz = self.env['fleet.vehicle.jawaz']
        for record in self:
            record.jawaz_count = jawaz.search_count([('vehicle_id', '=', record.id)])
