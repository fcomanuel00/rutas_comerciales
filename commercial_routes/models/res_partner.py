# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_zona = fields.Char(
        string='Zona',
        help='Zona de visita comercial (ej: Centro, Polígono Norte, Triana)',
    )
    x_has_coords = fields.Boolean(
        string='Tiene coordenadas',
        compute='_compute_has_coords',
        store=False,
    )
    route_stop_ids = fields.One2many(
        'commercial.route.stop',
        'partner_id',
        string='Visitas comerciales',
    )
    route_visit_count = fields.Integer(
        string='Visitas',
        compute='_compute_visit_count',
    )

    @api.depends('partner_latitude', 'partner_longitude')
    def _compute_has_coords(self):
        for rec in self:
            rec.x_has_coords = bool(rec.partner_latitude and rec.partner_longitude)

    def _compute_visit_count(self):
        for rec in self:
            rec.route_visit_count = len(rec.route_stop_ids.filtered('visited'))

    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Visitas – {self.name}',
            'res_model': 'commercial.route.stop',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id), ('visited', '=', True)],
            'context': {'default_partner_id': self.id},
        }
