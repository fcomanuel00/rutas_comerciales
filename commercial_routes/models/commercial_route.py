# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
import math
import logging

_logger = logging.getLogger(__name__)


class CommercialRoute(models.Model):
    _name = 'commercial.route'
    _description = 'Commercial Route'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Route Name',
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        default=fields.Date.today,
        required=True,
        tracking=True,
    )
    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        required=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('in_progress', 'En curso'),
            ('done', 'Completada'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )
    city_filter = fields.Char(string='City Filter')
    zone_filter = fields.Char(string='Zone Filter')
    notes = fields.Text(string='General Notes')
    stop_ids = fields.One2many(
        'commercial.route.stop',
        'route_id',
        string='Stops',
    )
    stop_count = fields.Integer(compute='_compute_counts', string='Total paradas')
    visited_count = fields.Integer(compute='_compute_counts', string='Visitados')
    order_count = fields.Integer(compute='_compute_counts', string='Pedidos')
    google_maps_url = fields.Char(compute='_compute_maps_url', string='Google Maps URL')

    @api.depends('stop_ids', 'stop_ids.visited', 'stop_ids.result')
    def _compute_counts(self):
        for rec in self:
            rec.stop_count = len(rec.stop_ids)
            visited = rec.stop_ids.filtered('visited')
            rec.visited_count = len(visited)
            rec.order_count = len(visited.filtered(lambda s: s.result == 'order'))

    @api.depends('stop_ids.sequence', 'stop_ids.partner_id.x_latitude',
                 'stop_ids.partner_id.x_longitude')
    def _compute_maps_url(self):
        for rec in self:
            stops = rec.stop_ids.filtered(
                lambda s: s.partner_id.x_latitude and s.partner_id.x_longitude
            ).sorted('sequence')
            if not stops:
                rec.google_maps_url = False
                continue
            waypoints = '|'.join(
                f'{s.partner_id.x_latitude},{s.partner_id.x_longitude}'
                for s in stops
            )
            rec.google_maps_url = (
                f'https://www.google.com/maps/dir/?api=1'
                f'&waypoints={waypoints}&travelmode=driving'
            )

    # ── State transitions ────────────────────────────────────────────
    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    # ── Google Maps ──────────────────────────────────────────────────
    def action_open_google_maps(self):
        self.ensure_one()
        if not self.google_maps_url:
            raise UserError(
                'No stops have coordinates yet.\n'
                'Open each customer card and press "Get Coordinates".'
            )
        return {'type': 'ir.actions.act_url', 'url': self.google_maps_url, 'target': 'new'}

    # ── Add clients wizard ───────────────────────────────────────────
    def action_add_clients(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Customers to Route',
            'res_model': 'commercial.route.add.clients',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_route_id': self.id,
                'default_city_filter': self.city_filter or '',
                'default_zone_filter': self.zone_filter or '',
            },
        }

    # ── Route optimization ───────────────────────────────────────────
    def action_optimize_route(self):
        """Nearest-neighbour reordering. Requires coordinates on partners."""
        self.ensure_one()
        stops = self.stop_ids.filtered(
            lambda s: s.partner_id.x_latitude and s.partner_id.x_longitude
        )
        if len(stops) < 2:
            raise UserError(
                'You need at least 2 customers with coordinates to optimize.\n'
                'Use the "Get Coordinates" button on each customer card.'
            )

        stops_list = list(stops)
        optimized = [stops_list.pop(0)]
        while stops_list:
            current = optimized[-1]
            nearest = min(stops_list, key=lambda s: self._distance(
                current.partner_id.x_latitude, current.partner_id.x_longitude,
                s.partner_id.x_latitude, s.partner_id.x_longitude,
            ))
            optimized.append(nearest)
            stops_list.remove(nearest)

        for i, stop in enumerate(optimized, start=1):
            stop.sequence = i

        stops_no_coords = self.stop_ids - stops
        for j, stop in enumerate(stops_no_coords, start=len(optimized) + 1):
            stop.sequence = j

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Route optimized: {len(optimized)} stops reordered.',
                'type': 'success',
                'sticky': False,
            },
        }

    # ── Batch geocoding ──────────────────────────────────────────────
    def action_geocode_all(self):
        self.ensure_one()
        partners = self.stop_ids.mapped('partner_id').filtered(
            lambda p: not p.x_latitude or not p.x_longitude
        )
        if not partners:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'message': 'All customers already have coordinates.', 'type': 'info'},
            }
        ok, errors = 0, []
        for partner in partners:
            try:
                partner.action_geocode()
                ok += 1
            except Exception as e:
                errors.append(f'{partner.name}: {e}')

        msg = f'{ok} customers geocoded.'
        if errors:
            msg += f' Errors ({len(errors)}): ' + '; '.join(errors[:3])
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': msg,
                'type': 'success' if not errors else 'warning',
                'sticky': bool(errors),
            },
        }

    @staticmethod
    def _distance(lat1, lon1, lat2, lon2):
        return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)
