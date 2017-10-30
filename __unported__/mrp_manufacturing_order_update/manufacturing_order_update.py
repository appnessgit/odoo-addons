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

from openerp import fields, models, api, _

class MoUpdateMrpProduction(models.Model):
    _inherit = "mrp.production"

    product_lines = fields.One2many(readonly=False)
    bom_id = fields.Many2one('mrp.bom', readonly=False)

    @api.multi
    def update_moves(self):
        for mrp in self:
            post = ''
            changes_to_do = []
            list_products_to_change = []
            needed_new_moves = []
            useless_moves = mrp.move_lines.filtered(lambda m: m.product_id not in
                                                              [x.product_id for x in mrp.product_lines])
            for product in list(set([x.product_id for x in useless_moves])):
                post += _("Product %s: not needed anymore<br>") % (product.display_name)
            useless_moves.with_context({'cancel_procurement': True}).action_cancel()
            for item in mrp.move_lines:
                if not item.product_id in list_products_to_change:
                    total_old_need = sum([x.product_uom_qty for x in mrp.move_lines if x.product_id == item.product_id])
                    total_new_need = sum([x.product_qty for x in mrp.product_lines if x.product_id == item.product_id])
                    if total_new_need != total_old_need and total_new_need != 0:
                        changes_to_do += [(item.product_id, total_new_need - total_old_need, total_new_need,
                                           total_old_need)]
                        list_products_to_change += [item.product_id]
            for product, qty, total_new_need, total_old_need in changes_to_do:
                if qty > 0:
                    move = mrp._make_consume_line_from_data(mrp, product, product.uom_id.id, qty, False, 0)
                    self.env['stock.move'].browse(move).action_confirm()
                else:
                    moves = mrp.move_lines.filtered(lambda m: m.product_id==product).\
                        sorted(key=lambda m: m.product_qty, reverse=True)
                    _sum = sum([x.product_qty for x in moves])
                    while _sum > total_new_need:
                        moves[0].with_context({'cancel_procurement': True}).action_cancel()
                        _sum -= moves[0].product_qty
                        moves -= moves[0]
                    if _sum < total_new_need:
                        move = self._make_consume_line_from_data(mrp, product, product.uom_id.id,
                                                                 total_new_need - _sum, False, 0)
                        self.env['stock.move'].browse(move).action_confirm()
                post += _("Product %s: quantity changed from %s to %s<br>") % \
                        (product.display_name, total_old_need, total_new_need)

            for item in mrp.product_lines:
                if item.product_id not in [y.product_id for y in mrp.move_lines if y.state != 'cancel']:
                    needed_new_moves += [item]
                    post += _("Raw material move created of quantity %s for product %s<br>") % \
                            (item.product_qty, product.display_name)

            for item in needed_new_moves:
                product = item.product_id
                move = mrp._make_consume_line_from_data(mrp, product, product.uom_id.id, item.product_qty, False, 0)
                self.env['stock.move'].browse(move).action_confirm()
            mrp.message_post(post)

    @api.multi
    def write(self, vals):
        result = super(MoUpdateMrpProduction, self).write(vals)
        productions_to_update = self
        if vals.get('product_lines') and ((1 in [x[0] for x in vals.get('product_lines')])
                                          or (2 in [x[0] for x in vals.get('product_lines')])
                                          or (0 in [x[0] for x in vals.get('product_lines')])):
            productions_to_update.update_moves()
        return result

    @api.multi
    def button_update(self):
        self.ensure_one()
        self._action_compute_lines()
        self.update_moves()
