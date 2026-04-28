# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class CommercialRouteAddClients(models.TransientModel):
    _name = 'commercial.route.add.clients'
    _description = 'Add Customers to Route'

    route_id = fields.Many2one('commercial.route', required=True)
    city_filter = fields.Char(string='City (contains)')
    zone_filter = fields.Char(string='Zone (contains)')
    only_without_coords = fields.Boolean(
        string='Only without coordinates',
        help='Show only customers that have no lat/lon saved yet',
    )
    partner_ids = fields.Many2many('res.partner', string='Customers')

    def action_search(self):
        domain = [('active', '=', True), ('customer_rank', '>', 0)]
        if self.city_filter:
            domain.append(('city', 'ilike', self.city_filter))
        if self.zone_filter:
            domain.append(('x_zona', 'ilike', self.zone_filter))
        if self.only_without_coords:
            domain += ['|', ('x_latitude', '=', False), ('x_latitude', '=', 0.0)]
        existing = self.route_id.stop_ids.mapped('partner_id').ids
        if existing:
            domain.append(('id', 'not in', existing))
        self.partner_ids = self.env['res.partner'].search(domain, limit=300)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'commercial.route.add.clients',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_add_selected(self):
        current_max = max(self.route_id.stop_ids.mapped('sequence') or [0])
        for i, partner in enumerate(self.partner_ids, start=1):
            self.env['commercial.route.stop'].create({
                'route_id': self.route_id.id,
                'partner_id': partner.id,
                'sequence': current_max + i,
            })
        return {'type': 'ir.actions.act_window_close'}
