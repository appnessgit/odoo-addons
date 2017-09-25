# -*- coding: utf8 -*-
#
#    Copyright (C) 2015 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp import fields, models, api, exceptions, _
from openerp.tools import float_compare


class QuantitiesModificationsSaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line = fields.One2many('sale.order.line', 'order_id', readonly=False,
                                 states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.multi
    def action_ship_create(self):
        """Create the required procurements to supply sales order lines, also connecting
        the procurements to appropriate stock moves in order to bring the goods to the
        sales order's requested location.

        :return: True
        """
        for order in self:
            vals = order._prepare_procurement_group(order)
            if not order.procurement_group_id:
                group = self.env['procurement.group'].create(vals)
                order.write({'procurement_group_id': group.id})
            procs_to_check = self.env['procurement.order'].search([('state', 'not in', ['cancel', 'done']),
                                                                   ('sale_line_id.order_id', '=', order.id)])
            if procs_to_check:
                procs_to_check.check()
            procurements = self.env['procurement.order'].search([('state', 'in', ['exception', 'cancel']),
                                                                 ('sale_line_id.order_id', '=', order.id)])
            if procurements:
                procurements.reset_to_confirmed()

            lines = order.order_line
            process_only_line_ids = self.env.context.get('process_only_line_ids')
            if process_only_line_ids:
                lines = self.env['sale.order.line'].search([('id', 'in', order.order_line.ids),
                                                            ('id', 'in', process_only_line_ids)])

            for line in lines:
                if line.state == 'cancel':
                    continue
                if not line.procurement_ids and line.need_procurement():
                    if (line.state == 'done') or not line.product_id:
                        continue
                    vals = self._prepare_order_line_procurement(order, line, group_id=order.procurement_group_id.id)
                    procurement = self.env['procurement.order']. \
                        with_context(procurement_autorun_defer=True).create(vals)
                    procurements |= procurement
            # Confirm procurement order such that rules will be applied on it
            # note that the workflow normally ensure proc_ids isn't an empty list
            procurements.run()

            # if shipping was in exception and the user choose to recreate the
            # delivery order, write the new status of SO
            if order.state == 'shipping_except':
                val = {'state': 'progress', 'shipped': False}

                if (order.order_policy == 'manual'):
                    for line in order.order_line:
                        if (not line.invoiced) and (line.state not in ('cancel', 'draft')):
                            val['state'] = 'manual'
                            break
                order.write(val)
        return True


class QuantitiesModificationsProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def compute_delivrered_ordered_quantities(self, line_uom_id):
        delivered_qty = 0
        ordered_qty = 0
        done_uom = []
        for procurement in self:
            if procurement.product_uom not in done_uom:
                procurements_done_current_uom = self.search([('id', 'in', self.ids),
                                                             ('product_uom', '=', procurement.product_uom.id),
                                                             ('state', '=', 'done')])
                procurements_not_cancel_current_uom = self.search([('id', 'in', self.ids),
                                                                   ('product_uom', '=', procurement.product_uom.id),
                                                                   ('state', '!=', 'cancel')])
                delivered_qty += self.env['product.uom']. \
                    _compute_qty(procurement.product_uom.id,
                                 sum([proc.product_qty for proc in procurements_done_current_uom]),
                                 to_uom_id=line_uom_id, round=True, rounding_method='UP')
                ordered_qty += self.env['product.uom']. \
                    _compute_qty(procurement.product_uom.id,
                                 sum([proc.product_qty for proc in procurements_not_cancel_current_uom]),
                                 to_uom_id=line_uom_id,
                                 round=True, rounding_method='UP')
                done_uom += [procurement.product_uom]
        return delivered_qty, ordered_qty


class QuantitiesModificationsSaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_uom_qty = fields.Float(readonly=False, states={'done': [('readonly', True)],
                                                           'cancel': [('readonly', True)]})
    price_unit = fields.Float(readonly=False, states={'done': [('readonly', True)],
                                                      'cancel': [('readonly', True)]})

    @api.multi
    def unlink(self):
        # Deletion of the corresponding procurements when deleting a sale order line.
        for rec in self:
            if rec.procurement_ids:
                rec.procurement_ids.cancel()
                rec.procurement_ids.unlink()
        self.button_cancel()
        return super(QuantitiesModificationsSaleOrderLine, self).unlink()

    @api.model
    def create(self, vals):
        # Creation of corresponding procurements when adding a sale order line.
        result = super(QuantitiesModificationsSaleOrderLine, self).create(vals)
        if result.order_id and result.order_id.state not in ['draft', 'done', 'cancel']:
            result.state = 'confirmed'
            # Lets's call 'action_ship_create' function using old api, in order to allow the system to change the
            # context (which is a frozendict in new api).
            context = self.env.context.copy()
            context['process_only_line_ids'] = result.ids
            # Creation of the corresponding procurement orders
            self.pool.get('sale.order').action_ship_create(self.env.cr, self.env.uid, [result.order_id.id], context)
        return result

    @api.model
    def _copy_procurement(self, proc, new_qty, new_uom_id):
        if not proc.product_uos or proc.product_uos.id == new_uom_id:
            product_uos_qty = new_qty
        else:
            product_uos_qty = self.env['product.uom']._compute_qty(new_uom_id, new_qty, proc.product_uos.id,
                                                                   rounding_method='HALF-UP')
        new_proc = proc.copy({
            'product_qty': new_qty,
            'product_uom': new_uom_id,
            'product_uos': proc.product_uos.id,
            'product_uos_qty': product_uos_qty,
        })
        new_proc.run()

    @api.multi
    def update_procurements_for_new_qty_or_uom(self, new_vals=None):
        for rec in self:
            if not new_vals:
                new_vals = {}
            proc_env = self.env['procurement.order']
            prec = rec.product_id.uom_id.rounding
            line_uom_id = new_vals.get('product_uom', rec.product_uom.id)
            product_uom_qty = new_vals.get('product_uom_qty', rec.product_uom_qty)
            procs_to_unlink = False
            delivered_qty, ordered_qty = rec.procurement_ids.compute_delivrered_ordered_quantities(line_uom_id)
            if rec.procurement_ids:
                if float_compare(product_uom_qty, ordered_qty, precision_rounding=prec) > 0:
                    # If the ordered_qty is too low, we increase the qty of the first procurement.
                    rec._copy_procurement(rec.procurement_ids[0], product_uom_qty - ordered_qty, line_uom_id)
                elif float_compare(product_uom_qty, ordered_qty, precision_rounding=prec) < 0:
                    if float_compare(product_uom_qty, delivered_qty, precision_rounding=prec) < 0:
                        raise exceptions.except_orm(_("Error!"), _("Impossible to set the line quantity lower "
                                                                   "than the delivered quantity."))
                    else:
                        # Let's remove undelivered procurements
                        procs_to_unlink = proc_env.search([('id', 'in', rec.procurement_ids.ids),
                                                           ('state', 'not in', ['cancel', 'done'])])
                        # Let's create a new procurement if needed
                        if float_compare(product_uom_qty, delivered_qty, precision_rounding=prec) > 0:
                            rec._copy_procurement(rec.procurement_ids[0], product_uom_qty - delivered_qty,
                                                  line_uom_id)
            if procs_to_unlink:
                procs_to_unlink.cancel()
                procs_to_unlink.unlink()
            elif float_compare(product_uom_qty, 0, precision_rounding=prec) == 0:
                # If the quantity of a line is zero, we delete the linked procurements and the line itself.
                if any([proc.state == 'done' for proc in rec.procurement_ids]):
                    raise exceptions.except_orm(_("Error!"),
                                                _("Impossible to cancel a procurement in state done."))
                elif rec.procurement_ids:
                    rec.procurement_ids.cancel()
                    rec.procurement_ids.unlink()
                rec.unlink()

    @api.multi
    def write(self, vals):
        result = super(QuantitiesModificationsSaleOrderLine, self).write(vals)
        # Overwriting the 'write' function, in order to deal with a modification of the quantity of a sale order line.
        lines_to_update = self.env['sale.order.line']
        for rec in self:
            prec = rec.product_id.uom_id.rounding
            if rec.order_id.state not in ['draft', 'cancel', 'done']:
                if vals.get('price_unit'):
                    active_moves = self.env['stock.move']. \
                        search([('product_id', '=', rec.product_id.id),
                                ('procurement_id', 'in', rec.procurement_ids.ids),
                                ('state', 'not in', ['draft', 'cancel', 'done'])])
                    active_moves.write({'price_unit': vals['price_unit']})
                chg_uom_or_qty_to_not_null = bool(vals.get('product_uom') or vals.get('product_uom_qty') and
                                                  float_compare(vals['product_uom_qty'], 0,
                                                                precision_rounding=prec) != 0)
                set_qty_to_zero = 'product_uom_qty' in vals.keys() and float_compare(vals['product_uom_qty'], 0,
                                                                                     precision_rounding=prec) == 0
                if chg_uom_or_qty_to_not_null or set_qty_to_zero:
                    lines_to_update += rec
        if lines_to_update:
            lines_to_update.update_procurements_for_new_qty_or_uom(new_vals=vals)
        return result
