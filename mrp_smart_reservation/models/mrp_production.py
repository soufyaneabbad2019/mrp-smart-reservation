from odoo import api, fields, models
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    smart_force_reserved = fields.Boolean(
        string='Forced Reservation',
        default=False,
        copy=False,
    )

    smart_is_distant = fields.Boolean(
        string='Is Distant MO',
        compute='_compute_smart_is_distant',
        store=False,
    )

    smart_reservation_status = fields.Selection(
        selection=[
            ('forced', 'Forced'),
            ('urgent', 'Urgent'),
            ('distant', 'Distant'),
            ('na', 'N/A'),
        ],
        string='Reservation',
        compute='_compute_smart_reservation_status',
        store=False,
    )

    @api.depends('smart_force_reserved', 'date_start', 'date_deadline')
    def _compute_smart_is_distant(self):
        horizon = self._smart_get_horizon()
        date_limit = date.today() + timedelta(days=horizon)
        for rec in self:
            rec.smart_is_distant = (
                not rec.smart_force_reserved
                and rec._smart_get_date() > date_limit
            )

    @api.depends('smart_force_reserved', 'state', 'date_start', 'date_deadline')
    def _compute_smart_reservation_status(self):
        horizon = self._smart_get_horizon()
        date_limit = date.today() + timedelta(days=horizon)
        for rec in self:
            if rec.state not in ('confirmed', 'progress'):
                rec.smart_reservation_status = 'na'
            elif rec.smart_force_reserved:
                rec.smart_reservation_status = 'forced'
            elif rec._smart_get_date() <= date_limit:
                rec.smart_reservation_status = 'urgent'
            else:
                rec.smart_reservation_status = 'distant'

    def _smart_get_horizon(self):
        return int(self.env['ir.config_parameter'].sudo().get_param(
            'mrp_smart_reservation.horizon_days', default=30
        ))

    def _smart_get_date(self):
        target = self.date_deadline or self.date_start
        if not target:
            return date.today() + timedelta(days=999)
        if hasattr(target, 'date'):
            return target.date()
        return target

    @api.model
    def _smart_reequilibrer(self):
        horizon = self._smart_get_horizon()
        date_limit = date.today() + timedelta(days=horizon)
        all_mos = self.search([('state', 'in', ['confirmed', 'progress'])])
        if not all_mos:
            return {'forced': 0, 'urgent': 0, 'distant': 0}
        forced = all_mos.filtered(lambda m: m.smart_force_reserved).sorted(key=lambda m: m._smart_get_date())
        distant = all_mos.filtered(lambda m: not m.smart_force_reserved and m._smart_get_date() > date_limit)
        urgent = (all_mos - forced - distant).sorted(key=lambda m: m._smart_get_date())
        for mo in all_mos:
            mo._smart_liberer()
        for mo in list(forced) + list(urgent):
            try:
                mo.action_assign()
            except Exception as e:
                _logger.warning('Smart Reservation: cannot reserve %s — %s', mo.name, e)
        return {'forced': len(forced), 'urgent': len(urgent), 'distant': len(distant)}

    def _smart_liberer(self):
        moves = self.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel'))
        if not moves:
            return
        try:
            moves._do_unreserve()
        except Exception as e:
            _logger.warning('Smart Reservation: unreserve failed for %s — %s', self.name, e)

    def action_confirm(self):
        result = super().action_confirm()
        self.env['mrp.production']._smart_reequilibrer()
        return result

    def action_smart_force_reservation(self):
        self.ensure_one()
        self.smart_force_reserved = True
        self._smart_reequilibrer()
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Forced', 'message': f'{self.name} → top priority. Stock rebalanced.', 'type': 'success', 'sticky': False}}

    def action_smart_cancel_force(self):
        self.ensure_one()
        self.smart_force_reserved = False
        self._smart_liberer()
        self._smart_reequilibrer()
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Force Cancelled', 'message': f'{self.name} → normal priority. Stock rebalanced.', 'type': 'warning', 'sticky': False}}

    def action_smart_reequilibrer_selection(self):
        result = self._smart_reequilibrer()
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': 'Rebalancing Complete',
                           'message': f"✔ {result['forced']} forced | ✔ {result['urgent']} urgent | ⏸ {result['distant']} distant",
                           'type': 'success', 'sticky': True}}

    @api.model
    def _cron_smart_reequilibrer(self):
        self._smart_reequilibrer()


class StockSchedulerCompute(models.TransientModel):
    _inherit = 'stock.scheduler.compute'

    def procure_calculation(self):
        result = super().procure_calculation()
        self.env['mrp.production']._smart_reequilibrer()
        return result