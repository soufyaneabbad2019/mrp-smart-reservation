{
    'name': 'MRP Smart Reservation',
    'version': '17.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Intelligent stock reservation for Manufacturing Orders — priority-based rebalancing',
    'description': """
MRP Smart Reservation
=====================
Extends Odoo Manufacturing with intelligent, priority-based stock reservation for Manufacturing Orders.

While Odoo 17/18 natively supports reservation methods (at confirmation, manually, before scheduled date),
it does NOT manage conflicts when available stock is insufficient for all confirmed MOs.

This module adds:
- Configurable reservation horizon (e.g. 30 days): MOs beyond the horizon are NOT reserved
- Priority-based global rebalancing: forced > urgent > distant
- 'Force Reservation' button to manually prioritize a distant MO
- 'Rebalance' action button from MO list
- Daily cron for automatic overnight rebalancing
- Automatic rebalancing after each scheduler run
    """,
    'author': 'Soufyane Abbad',
    'website': '',
    'license': 'OPL-1',
    'price': 89.00,
    'currency': 'EUR',
    'depends': ['mrp', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron.xml',
        'views/res_config_settings_views.xml',
        'views/mrp_production_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
