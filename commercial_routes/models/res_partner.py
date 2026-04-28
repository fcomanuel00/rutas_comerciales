# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_zona = fields.Char(
        string='Zone',
        help='Commercial visit zone (e.g. City Centre, North Industrial, Triana)',
    )
    x_latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
    )
    x_longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
    )
    x_has_coords = fields.Boolean(
        string='Has Coordinates',
        compute='_compute_has_coords',
        store=False,
    )
    route_stop_ids = fields.One2many(
        'commercial.route.stop',
        'partner_id',
        string='Commercial Visits',
    )
    route_visit_count = fields.Integer(
        string='Visits',
        compute='_compute_visit_count',
    )

    @api.depends('x_latitude', 'x_longitude')
    def _compute_has_coords(self):
        for rec in self:
            rec.x_has_coords = bool(rec.x_latitude and rec.x_longitude)

    def _compute_visit_count(self):
        for rec in self:
            rec.route_visit_count = len(rec.route_stop_ids.filtered('visited'))

    def action_geocode(self):
        """Calls Google Geocoding API to get lat/lon from the partner address."""
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'commercial_routes.google_maps_api_key', ''
        )
        if not api_key:
            raise UserError(
                'No Google Maps API key configured.\n'
                'Go to Settings → Commercial Routes → Google Maps API Key.'
            )
        parts = [
            self.street or '',
            self.city or '',
            self.state_id.name if self.state_id else '',
            self.country_id.name if self.country_id else '',
        ]
        address = ', '.join(p for p in parts if p)
        if not address.strip(', '):
            raise UserError('Partner has no address. Fill in at least city or street first.')

        try:
            import requests
            response = requests.get(
                'https://maps.googleapis.com/maps/api/geocode/json',
                params={'address': address, 'key': api_key},
                timeout=10,
            )
            data = response.json()
        except Exception as e:
            raise UserError(f'Connection error with Google: {e}')

        if data.get('status') == 'OK':
            location = data['results'][0]['geometry']['location']
            self.x_latitude = location['lat']
            self.x_longitude = location['lng']
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Coordinates saved: {self.x_latitude:.5f}, {self.x_longitude:.5f}',
                    'type': 'success',
                    'sticky': False,
                },
            }
        else:
            raise UserError(
                f'Google could not find address "{address}".\n'
                f'Status: {data.get("status")}'
            )

    def action_view_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Visits – {self.name}',
            'res_model': 'commercial.route.stop',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id), ('visited', '=', True)],
            'context': {'default_partner_id': self.id},
        }
