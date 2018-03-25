# -*- coding: utf8 -*-
#
# Copyright (C) 2015 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

from openerp import fields, models, api, exceptions, _
from openerp.tools import float_compare


@job(default_channel='root.mrp.update')
def run_mrp_production_update(session, model_name, mrp_ids, context):
    mrp_orders = session.env[model_name].with_context(context).browse(mrp_ids)
    mrp_orders.button_update()
    return "End update"


class MoUpdateMrpProduction(models.Model):
    _inherit = "mrp.production"

    product_lines = fields.One2many(readonly=False)
    bom_id = fields.Many2one('mrp.bom', readonly=False, track_visibility='onchange')

    @api.multi
    def update_moves(self):
        for mrp in self:
            post = ''
            changes_to_do = []
            done_products = []
            needed_new_moves = []
            useless_moves = self.env['stock.move']
            wrong_location_moves = self.env['stock.move']
            needed_products = [x.product_id for x in mrp.product_lines]
            source_location = mrp.get_actual_location_src_and_routing()[0]
            for move in mrp.move_lines:
                if move.product_id not in needed_products:
                    useless_moves |= move
                if move.location_id != source_location:
                    wrong_location_moves |= move
            if useless_moves:
                for product in list(set([x.product_id for x in useless_moves])):
                    post += _("Product %s: not needed anymore<br>") % (product.display_name)
                useless_moves.with_context(cancel_procurement=True, forbid_unreserve_quants=True).action_cancel()
            if wrong_location_moves:
                for product in list(set([x.product_id for x in wrong_location_moves])):
                    post += _("Product %s: raw material move had wrong source location, it was cancelled<br>") % \
                        (product.display_name)
                wrong_location_moves.with_context(cancel_procurement=True, forbid_unreserve_quants=True).action_cancel()
            for item in mrp.move_lines:
                if not item.product_id in done_products:
                    total_done_moves = sum([x.product_qty for x in mrp.move_lines2 if x.product_id == item.product_id
                                            and x.state == 'done' and x.location_dest_id.usage == 'production'])
                    total_old_need = sum([x.product_qty for x in mrp.move_lines if x.product_id == item.product_id])
                    total_new_need = 0
                    for product_line in mrp.product_lines:
                        if product_line.product_id == item.product_id:
                            total_new_need += self.env['product.uom']._compute_qty_obj(
                                from_unit=product_line.product_uom,
                                qty=product_line.product_qty,
                                to_unit=product_line.product_id.uom_id)
                    prec = item.product_id.uom_id.rounding
                    if float_compare(total_new_need, total_done_moves, precision_rounding=prec) < 0:
                        raise exceptions.except_orm(_(u"Error!"),
                                                    _(u"Product %s on MO %s : %s %s where consumed, impossible to "
                                                      u"decrease this quantity to %s") %
                                                    (item.product_id.display_name, mrp.name, total_done_moves,
                                                     item.product_id.uom_id.display_name, total_new_need))
                    total_old_need += total_done_moves
                    if float_compare(total_new_need, total_old_need, precision_rounding=prec) != 0 \
                            and float_compare(total_new_need, 0, precision_rounding=prec) != 0:
                        changes_to_do += [(item.product_id, total_new_need, total_old_need, total_done_moves)]
                    done_products += [item.product_id]
            for product, total_new_need, total_old_need, total_done_moves in changes_to_do:
                qty = total_new_need - total_old_need
                if float_compare(qty, 0, precision_rounding=prec) > 0:
                    move = mrp._make_consume_line_from_data(mrp, product, product.uom_id.id, qty, False, 0)
                    self.env['stock.move'].browse(move).action_confirm()
                else:
                    final_running_qty = total_new_need - total_done_moves
                    moves = self.env['stock.move'].search([('raw_material_production_id', '=', mrp.id),
                                                           ('state', 'not in', ['done', 'cancel']),
                                                           ('product_id', '=', product.id)],
                                                          order='product_qty desc, id asc')
                    qty_ordered = sum([x.product_qty for x in moves])
                    while float_compare(qty_ordered, final_running_qty, precision_rounding=product.uom_id.rounding) > 0:
                        moves[0].with_context(cancel_procurement=True, forbid_unreserve_quants=True,
                                              new_target_qty=final_running_qty).action_cancel()
                        qty_ordered -= moves[0].product_qty
                        moves -= moves[0]
                    if float_compare(qty_ordered, final_running_qty, precision_rounding=product.uom_id.rounding) < 0:
                        move = self._make_consume_line_from_data(mrp, product, product.uom_id.id,
                                                                 final_running_qty - qty_ordered, False, 0)
                        self.env['stock.move'].browse(move).action_confirm()
                post += _("Product %s: quantity changed from %s to %s<br>") % \
                    (product.display_name, total_old_need, total_new_need)

            for item in mrp.product_lines:
                if item.product_id not in [y.product_id for y in mrp.move_lines if y.state != 'cancel']:
                    needed_new_moves += [item]
                    post += _("Raw material move created of quantity %s for product %s<br>") % \
                        (item.product_qty, item.product_id.display_name)

            for item in needed_new_moves:
                product = item.product_id
                move_id = mrp._make_consume_line_from_data(mrp, product, item.product_uom.id,
                                                           item.product_qty, False, 0)
                self.env['stock.move'].browse(move_id).action_confirm()
            if post:
                mrp.message_post(post)

    @api.multi
    def write(self, vals):
        result = super(MoUpdateMrpProduction, self).write(vals)
        if vals.get('product_lines') and ((1 in [x[0] for x in vals.get('product_lines')])
                                          or (2 in [x[0] for x in vals.get('product_lines')])
                                          or (0 in [x[0] for x in vals.get('product_lines')])):
            for rec in self:
                state = vals.get('state', rec.state)

                if state not in ['done', 'cancel']:
                    self.update_moves()
        return result

    @api.multi
    def button_update(self):
        self._action_compute_lines()
        self.update_moves()

    @api.model
    def get_mrp_ids_to_check(self):
        self.env.cr.execute("""WITH mrp_moves_details AS (
            SELECT
              mrp.id        AS mrp_id,
              sm.state      AS raw_move_state,
              sm_orig.state AS service_move_state
            FROM mrp_production mrp
              LEFT JOIN stock_move sm ON sm.raw_material_production_id = mrp.id
              LEFT JOIN stock_move sm_orig ON sm_orig.move_dest_id = sm.id
            WHERE mrp.state IN ('ready', 'confirmed'))

        SELECT mrp_id
        FROM mrp_moves_details
        GROUP BY mrp_id
        HAVING sum(CASE WHEN raw_move_state = 'done' OR
                             service_move_state = 'done'
          THEN 1
                   ELSE 0 END) <= 0""")
        return [item[0] for item in self.env.cr.fetchall()]

    @api.model
    def run_schedule_button_update(self, jobify=True):
        mrp_to_check_ids = self.get_mrp_ids_to_check()
        mrp_to_update_ids = []
        for mrp_id in mrp_to_check_ids:
            mrp = self.env['mrp.production'].search([('id', '=', mrp_id)])
            bom = mrp.bom_id
            if not bom:
                bom = bom._bom_find(product_id=mrp.product_id.id)
            if bom:
                mrp_to_update_ids += [mrp_id]
        chunk_number = 0
        while mrp_to_update_ids:
            chunk_number += 1
            mrp_chunk_ids = mrp_to_update_ids[:100]
            if jobify:
                run_mrp_production_update.delay(ConnectorSession.from_env(self.env), 'mrp.production', mrp_chunk_ids,
                                                dict(self.env.context),
                                                description=u"MRP Production Update (chunk %s)" % chunk_number)
            else:
                run_mrp_production_update(ConnectorSession.from_env(self.env), 'mrp.production', mrp_chunk_ids,
                                          dict(self.env.context))
            mrp_to_update_ids = mrp_to_update_ids[100:]


class UpdateChangeProductionQty(models.TransientModel):
    _inherit = 'change.production.qty'

    @api.multi
    def change_prod_qty(self):
        for rec in self:
            if self.env.context.get('active_id'):
                order = self.env['mrp.production'].browse(self.env.context.get('active_id'))
                # Check raw material moves
                if order.bom_id and float_compare(order.product_qty, rec.product_qty,
                                                  precision_rounding=order.product_id.uom_id.rounding) != 0:
                    order.product_qty = rec.product_qty
                    order.button_update()
                # Check production moves
                if order.move_prod_id:
                    order.move_prod_id.write({'product_uom_qty': rec.product_qty})
                self._update_product_to_produce(order, rec.product_qty)


class UpdateChangeStockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def action_cancel(self):
        consume_moves = self.env['stock.move'].search([('id', 'in', self.ids),
                                                       ('raw_material_production_id', '!=', False)])
        if self.env.context.get('forbid_unreserve_quants') and consume_moves:
            new_target_qty = self.env.context.get('new_target_qty', False)
            reserved_quant = self.env['stock.quant'].search([('reservation_id', 'in', consume_moves.ids)], limit=1)
            reserved_qty = sum([sum([quant.qty for quant in move.reserved_quant_ids]) for
                                    move in reserved_quant.reservation_id.raw_material_production_id.move_lines if
                                    move.product_id == reserved_quant.product_id])
            if new_target_qty:
                reserved_qty = reserved_qty - new_target_qty
            if reserved_quant:
                raise exceptions.except_orm(_(u"Error!"),
                                            _(u"Product %s in MO %s: forbidden to cancel a move with reserved quants "
                                              u"(quantity to unreserve: %s %s)") %
                                            (reserved_quant.product_id.display_name,
                                             reserved_quant.reservation_id.raw_material_production_id.display_name,
                                             reserved_qty,
                                             reserved_quant.product_id.uom_id.display_name))
        return super(UpdateChangeStockMove, self).action_cancel()
