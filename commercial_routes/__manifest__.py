# -*- coding: utf-8 -*-
# Part of Framarketing. See LICENSE file for full copyright and licensing details.
{
    'name': 'Commercial Routes',
    'version': '19.0.1.0.0',
    'summary': 'Plan, optimize and track field sales visits with route management',
    'description': """
Commercial Routes for Field Sales Teams
========================================

Plan your field sales visits efficiently:

* Filter customers by city and custom zone
* Build visit routes manually or auto-optimize by distance
* Record visit results (order placed, no order, not available, callback)
* Save notes per visit — visible in the customer profile
* One-tap Google Maps integration with all waypoints
* Batch geocoding of customer addresses
* Full visit history per customer
* Configurable Google Maps API key in Settings
    """,
    'author': 'Framarketing',
    'website': 'https://framarketing.es',
    'support': 'info@framarketing.es',
    'license': 'OPL-1',
    'currency': 'EUR',
    'price': 29.0,
    'category': 'Sales/Sales',
    'depends': ['base', 'contacts', 'mail', 'base_geolocalize'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/commercial_routes_security.xml',
        'security/ir.model.access.csv',
        'data/config_data.xml',
        'views/res_partner_views.xml',
        'views/commercial_route_views.xml',
        'wizards/wizard_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
