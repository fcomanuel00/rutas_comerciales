# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    commercial_routes_google_api_key = fields.Char(
        string='Google Maps API Key',
        config_parameter='commercial_routes.google_maps_api_key',
        help='Required for address geocoding and route distance optimization.',
    )
