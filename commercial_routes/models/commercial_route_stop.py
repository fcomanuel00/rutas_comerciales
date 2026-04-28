# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CommercialRouteStop(models.Model):
    _name = 'commercial.route.stop'
    _description = 'Commercial Route Stop'
    _order = 'route_id, sequence, id'

    route_id = fields.Many2one(
        'commercial.route',
        string='Route',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(string='Order', default=10)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        domain=[('active', '=', True)],
    )
    partner_city = fields.Char(related='partner_id.city', string='City', store=True)
    partner_zone = fields.Char(related='partner_id.x_zona', string='Zone', store=True)
    partner_phone = fields.Char(related='partner_id.phone', string='Phone')
    partner_has_coords = fields.Boolean(
        related='partner_id.x_has_coords',
        string='GPS',
    )
    visited = fields.Boolean(string='Visited', default=False)
    visit_date = fields.Datetime(string='Visit Date')
    result = fields.Selection(
        selection=[
            ('pending', 'Pendiente'),
            ('order', 'Pedido realizado'),
            ('no_order', 'Sin pedido'),
            ('not_home', 'No estaba'),
            ('callback', 'Volver a llamar'),
        ],
        string='Result',
        default='pending',
    )
    notes = fields.Text(string='Notes')

    @api.onchange('visited')
    def _onchange_visited(self):
        if self.visited and not self.visit_date:
            self.visit_date = fields.Datetime.now()
        if not self.visited:
            self.visit_date = False
            self.result = 'pending'
