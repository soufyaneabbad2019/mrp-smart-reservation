from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mrp_smart_horizon_days = fields.Integer(
        string='Reservation Horizon (days)',
        default=30,
        config_parameter='mrp_smart_reservation.horizon_days',
        help=(
            'MOs scheduled beyond this number of days will NOT have stock reserved. '
            'Stock remains available for urgent MOs within the horizon. '
            'Recommended: 30 days.'
        ),
    )
