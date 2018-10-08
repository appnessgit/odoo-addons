# -*- coding: utf8 -*-
#
# Copyright (C) 2014 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from datetime import datetime

from openerp import fields, models, api
from openerp.osv import fields as old_api_fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

QUERY_MIN_PROC = """
SELECT
  p.id as id,
  min(p.date_planned) as date
FROM procurement_order p
WHERE p.purchase_line_id = %s 
AND p.state not in ('done', 'cancel')
GROUP BY p.id
ORDER BY p.date_planned ASC 
LIMIT 1
"""


class ProcurementOrderPurchasePlanningImproved(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def action_reschedule(self):
        """Reschedules the moves associated to this procurement."""
        for proc in self:
            if proc.state not in ['done', 'cancel', 'exception'] and proc.rule_id and proc.rule_id.action == 'buy' and \
                    not self.env.context.get('do_not_propagate_rescheduling'):
                schedule_date = self._get_purchase_schedule_date(proc, proc.company_id)
                order_date = self._get_purchase_order_date(proc, proc.company_id, schedule_date)
                # We sudo because the user has not necessarily the rights to update PO and PO lines
                proc = proc.sudo()
                # If the purchase line is not confirmed yet, try to set planned date to schedule_date
                if proc.purchase_id.state in ['sent', 'bid'] and order_date > datetime.now() and not \
                        self.env.context.get('do_not_reschedule_bigd_and_sent') or proc.purchase_id.state == 'draft':
                    proc.purchase_line_id.date_planned = fields.Date.to_string(schedule_date)
                if proc.purchase_id and fields.Datetime.from_string(proc.purchase_id.date_order) > order_date and not \
                        self.env.context.get('do_not_move_purchase_order'):
                    proc.purchase_id.date_order = fields.Datetime.to_string(order_date)
                proc.purchase_line_id.set_moves_dates(proc.purchase_line_id.date_required)
        return super(ProcurementOrderPurchasePlanningImproved, self).action_reschedule()

    @api.model
    def _get_po_line_values_from_proc(self, procurement, partner, company, schedule_date):
        """Overridden to set date_required."""
        res = super(ProcurementOrderPurchasePlanningImproved, self)._get_po_line_values_from_proc(
            procurement, partner, company, schedule_date)
        res.update({
            'requested_date': schedule_date.strftime(DEFAULT_SERVER_DATE_FORMAT),
        })
        return res


class PurchaseOrderLinePlanningImproved(models.Model):
    _inherit = 'purchase.order.line'

    @api.cr_uid_ids_context
    def _compute_dates(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.search_read(cr, uid,
                                     domain=[('id', 'in', ids)],
                                     fields=['date_planned', 'date_required', 'limit_order_date',
                                             'order_id', 'company_id', 'id'],
                                     context=context):
            company = self.pool.get('res.company').browse(cr, uid, line['company_id'][0], context=context)
            partner_id = self.pool.get('purchase.order').search_read(cr, uid,
                                                                     domain=[('id', '=', line['order_id'][0])],
                                                                     fields=['partner_id'],
                                                                     limit=1,
                                                                     context=context)[0]['partner_id'][0]
            line_data = {'date_required': line['date_required'], 'limit_order_date': line['limit_order_date']}
            cr.execute(QUERY_MIN_PROC, [line['id']])
            vals = cr.dictfetchone()
            if vals:
                min_date = vals['date']
                min_proc = self.pool.get('procurement.order').browse(cr, uid, [vals['id']], context=context)
                if min_proc.rule_id:
                    context = dict(context, do_not_save_result=True, force_partner_id=partner_id)
                    date_required = self.pool.get('procurement.order'). \
                        _get_purchase_schedule_date(cr, uid, min_proc, company, context=context)
                    date_planned = fields.Datetime.from_string(line['date_planned'])
                    limit_order_date = self.pool.get('procurement.order'). \
                        _get_purchase_order_date(cr, uid, min_proc, company,
                                                 date_planned , context=context)
                    limit_order_date = limit_order_date and fields.Datetime.to_string(limit_order_date) or False
                    date_required = date_required and fields.Datetime.to_string(date_required) or False
                else:
                    date_required = min_date
                    limit_order_date = min_date
            else:
                date_required = line['date_planned']
                limit_order_date = line['date_planned']
            target_data = {'date_required': date_required and date_required[:10] or False,
                           'limit_order_date': limit_order_date and limit_order_date[:10] or False}
            if target_data != line_data:
                res[line['id']] = target_data
        return res

    @api.cr_uid_ids_context
    def _compute_has_procurements(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if ids:
            cr.execute("""SELECT pol.id
FROM purchase_order_line pol
  INNER JOIN procurement_order po ON po.purchase_line_id = pol.id
WHERE pol.id IN %s
GROUP BY pol.id""", (tuple(ids),))
            line_with_proc_ids = [item[0] for item in cr.fetchall()]
            for line in self.browse(cr, uid, ids, context=context):
                if line.id in line_with_proc_ids and not line.has_procurements:
                    res[line.id] = True
                elif line.id not in line_with_proc_ids and line.has_procurements:
                    res[line.id] = False
        return res

    @api.cr_uid_ids_context
    def _get_order_lines(self, cr, uid, ids, context=None):
        res = set()
        for proc in self.browse(cr, uid, ids, context=context):
            if proc.purchase_line_id:
                res.add(proc.purchase_line_id.id)
        return list(res)

    _columns = {
        'date_required': old_api_fields.function(_compute_dates, type='date', string=u"Required Date",
                                                 help=u"Required date for this purchase line. "
                                                      "Computed as planned date of the first proc - supplier purchase "
                                                      "lead time - company purchase lead time",
                                                 multi="compute_dates",
                                                 store={
                                                     'purchase.order.line': (lambda self, cr, uid, ids, ctx: ids,
                                                                             ['order_id', 'date_planned'], 20),
                                                     'procurement.order': (_get_order_lines,
                                                                           ['date_planned', 'purchase_line_id'], 20)
                                                 }, readonly=True),
        'limit_order_date': old_api_fields.function(_compute_dates, type='date', string=u"Limit Order Date",
                                                    help=u"Limit order date to be late :required date - supplier delay",
                                                    multi="compute_dates",
                                                    store={
                                                        'purchase.order.line': (lambda self, cr, uid, ids, ctx: ids,
                                                                                ['order_id', 'date_planned'], 20),
                                                        'procurement.order': (_get_order_lines,
                                                                              ['date_planned', 'purchase_line_id'], 20)
                                                    }, readonly=True),
        'has_procurements': old_api_fields.function(_compute_has_procurements, type='boolean',
                                                    string=u"Has procurements", readonly=True,
                                                    store={'procurement.order': (_get_order_lines,
                                                                                 ['purchase_line_id'], 20)}),
    }

    confirm_date = fields.Datetime(string=u"Confirm date", readonly=True)
    requested_date = fields.Date("Requested date", help="The line was required to the supplier at that date",
                                 default=fields.Date.context_today, states={'sent': [('readonly', True)],
                                                                            'bid': [('readonly', True)],
                                                                            'confirmed': [('readonly', True)],
                                                                            'approved': [('readonly', True)],
                                                                            'except_picking': [('readonly', True)],
                                                                            'except_invoice': [('readonly', True)],
                                                                            'done': [('readonly', True)],
                                                                            'cancel': [('readonly', True)],
                                                                            })

    @api.multi
    def set_moves_dates(self, date_required):
        for rec in self:
            moves = rec.move_ids.filtered(lambda m: m.state not in ['draft', 'cancel'])
            moves.filtered(lambda move: move.date != date_required).write({'date': date_required})

    @api.model
    def create(self, vals):
        if vals.get('date_planned'):
            vals['requested_date'] = vals['date_planned']
        return super(PurchaseOrderLinePlanningImproved, self).create(vals)

    @api.multi
    def write(self, vals):
        """write method overridden here to propagate date_planned to the stock_moves of the receipt."""
        if vals.get('date_planned'):
            for line in self:
                if line.state == "draft" and vals.get('status', 'draft') == 'draft':
                    vals['requested_date'] = vals['date_planned']
        result = super(PurchaseOrderLinePlanningImproved, self).write(vals)
        if vals.get('date_planned'):
            date = vals.get('date_planned') + " 12:00:00"
            for line in self:
                moves = self.env['stock.move'].search([('purchase_line_id', '=', line.id),
                                                       ('state', 'not in', ['done', 'cancel'])])
                if line.procurement_ids:
                    moves.write({'date_expected': date})
                else:
                    moves.write({'date_expected': date, 'date': date})
        return result


class PurchaseOrderPlanningImproved(models.Model):
    _inherit = 'purchase.order'

    confirm_date = fields.Datetime(string=u"Confirm date", readonly=True)
    limit_order_date = fields.Date(string=u"Limit order date to be late", readonly=True)

    @api.model
    def cron_compute_limit_order_date(self):
        self.env.cr.execute("""SELECT
  po.id                     AS order_id,
  min(pol.limit_order_date) AS new_limit_order_date
FROM purchase_order po
  INNER JOIN purchase_order_line pol ON pol.order_id = po.id AND pol.limit_order_date IS NOT NULL
GROUP BY po.id
ORDER BY po.id""")
        result = self.env.cr.dictfetchall()
        order_with_limit_dates_ids = []
        for item in result:
            order = self.search([('id', '=', item['order_id'])])
            if order.limit_order_date != item['new_limit_order_date']:
                order.limit_order_date = item['new_limit_order_date']
            order_with_limit_dates_ids += [item['order_id']]
        self.search([('id', 'not in', order_with_limit_dates_ids)]).write({'limit_order_date': False})

    @api.multi
    def write(self, vals):
        """write method overridden here to propagate date_planned to the stock_moves of the receipt."""
        if vals.get('state') == 'approved':
            date_now = fields.Datetime.now()
            vals['confirm_date'] = date_now
            order_lines = self.env['purchase.order.line'].search([('order_id', 'in', self.ids)])
            if order_lines:
                order_lines.write({'confirm_date': date_now})
        if vals.get('state') in ['draft', 'cancel']:
            vals['confirm_date'] = False
            order_lines = self.env['purchase.order.line'].search([('order_id', 'in', self.ids)])
            if order_lines:
                order_lines.write({'confirm_date': False})
        return super(PurchaseOrderPlanningImproved, self).write(vals)
