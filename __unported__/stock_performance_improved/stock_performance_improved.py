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

from openerp.tools import drop_view_if_exists, flatten
from openerp import fields, models, api

from openerp.addons.scheduler_async import scheduler_async
from openerp.addons.connector.session import ConnectorSession

assign_moves = scheduler_async.assign_moves

MOVE_CHUNK = 100


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def assign_moves_to_picking(self):
        """Assign prereserved moves that do not belong to a picking yet to a picking by reconfirming them.
        """
        # We skip moves given in context not create infinite recursion
        skip_move_ids = self.env.context.get('skip_moves', [])
        prereservations = self.env['stock.prereservation'].search([('picking_id', '=', False),
                                                                   ('move_id', 'not in', skip_move_ids)])
        todo_moves = prereservations.mapped(lambda p: p.move_id)
        to_assign_moves = todo_moves.filtered(lambda m: m.state == 'assigned')
        if todo_moves:
            # We check if we have todo_moves to prevent infinite recursion
            todo_moves.action_confirm()
            # We reassign moves that were assigned beforehand because action_confirmed changed the state
            to_assign_moves.action_assign()

    @api.multi
    def action_assign(self):
        """Check availability of picking moves.

        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        Overridden here to assign prereserved moves to pickings beforehand.
        :return: True
        """
        self.assign_moves_to_picking()
        return super(StockPicking, self).action_assign()

    @api.multi
    def rereserve_pick(self):
        """
        This can be used to provide a button that rereserves taking into account the existing pack operations
        Overridden here to assign prereserved moves to pickings beforehand
        """
        self.assign_moves_to_picking()
        super(StockPicking, self).rereserve_pick()


class StockMove(models.Model):
    _inherit = 'stock.move'

    defer_picking_assign = fields.Boolean("Defer Picking Assignement", default=False,
                                          help="If checked, the stock move will be assigned to a picking only if there "
                                               "is available quants in the source location. Otherwise, it will be "
                                               "assigned a picking as soon as the move is confirmed.")

    @api.multi
    def _picking_assign(self, procurement_group, location_from, location_to):
        """Assigns these moves that share the same procurement.group, location_from and location_to to a stock picking.

        Overridden here to assign only if the move is prereserved.
        :<param procurement_group: The procurement.group of the moves
        :param location_from: The source location of the moves
        :param location_to: The destination lcoation of the moves
        """
        prereservations = self.env['stock.prereservation'].search([('move_id', 'in', self.ids)])
        prereserved_moves = prereservations.mapped(lambda p: p.move_id)
        not_deferred_moves = self.filtered(lambda m: m.defer_picking_assign is False)
        todo_moves = not_deferred_moves | prereserved_moves
        # Only assign prereserved or outgoing moves to pickings
        if todo_moves:
            # Use a SQL query as doing with the ORM will split it in different queries with id IN (,,)
            # In the next version, the locations on the picking should be stored again.
            query = """
                SELECT stock_picking.id FROM stock_picking, stock_move
                WHERE
                    stock_picking.state in ('draft','waiting','confirmed','partially_available','assigned') AND
                    stock_move.picking_id = stock_picking.id AND
                    stock_move.location_id = %s AND
                    stock_move.location_dest_id = %s AND
            """
            params = (location_from, location_to)
            if not procurement_group:
                query += "stock_picking.group_id IS NULL LIMIT 1"
            else:
                query += "stock_picking.group_id = %s LIMIT 1"
                params += (procurement_group,)
            self.env.cr.execute(query, params)
            [pick_id] = self.env.cr.fetchone() or [None]
            if not pick_id:
                move = self[0]
                values = {
                    'origin': move.origin,
                    'company_id': move.company_id and move.company_id.id or False,
                    'move_type': move.group_id and move.group_id.move_type or 'direct',
                    'partner_id': move.partner_id.id or False,
                    'picking_type_id': move.picking_type_id and move.picking_type_id.id or False,
                }
                pick = self.env['stock.picking'].create(values)
                pick_id = pick.id
            return self.write({'picking_id': pick_id})
        else:
            return True

    @api.multi
    def action_assign(self):
        """ Checks the product type and accordingly writes the state.
        Overridden here to also assign a picking if it is not done yet.
        """
        moves_no_pick = self.filtered(lambda m: m.picking_type_id and not m.picking_id)
        moves_no_pick.action_confirm()
        super(StockMove, self).action_assign()


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    defer_picking_assign = fields.Boolean("Defer Picking Assignement", default=False,
                                          help="If checked, the stock move generated by this rule will be assigned to "
                                               "a picking only if there is available quants in the source location. "
                                               "Otherwise, it will be assigned a picking as soon as the move is "
                                               "confirmed.")


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        res.update({'defer_picking_assign': procurement.rule_id.defer_picking_assign})
        return res

    @api.model
    def run_assign_moves(self):
        confirmed_moves = self.env['stock.prereservation'].search([('reserved', '=', False)]).mapped('move_id')
        cm_product_ids = confirmed_moves.read(['id', 'product_id'], load=False)

        # Create a dict of moves with same product {product_id: [move_id, move_id], product_id: []}
        result = dict()
        for row in cm_product_ids:
            if row['product_id'] not in result:
                result[row['product_id']] = list()
            result[row['product_id']].append(row['id'])
        product_ids = result.values()

        while product_ids:
            products = product_ids[:MOVE_CHUNK]
            product_ids = product_ids[MOVE_CHUNK:]
            move_ids = flatten(products)
            if self.env.context.get('jobify'):
                assign_moves.delay(ConnectorSession.from_env(self.env), 'stock.move', move_ids, self.env.context)
            else:
                assign_moves(ConnectorSession.from_env(self.env), 'stock.move', move_ids, self.env.context)


class StockPrereservation(models.Model):
    _name = 'stock.prereservation'
    _description = "Stock Pre-Reservation"
    _auto = False

    move_id = fields.Many2one('stock.move', readonly=True, index=True)
    picking_id = fields.Many2one('stock.picking', readonly=True, index=True)
    reserved = fields.Boolean("Move has reserved quants", readonly=True, index=True)

    def init(self, cr):
        drop_view_if_exists(cr, "stock_prereservation")
        cr.execute("""
        CREATE OR REPLACE VIEW stock_prereservation AS (
            WITH RECURSIVE top_parent(loc_id, top_parent_id) AS (
                    SELECT
                        sl.id AS loc_id, sl.id AS top_parent_id
                    FROM
                        stock_location sl
                        LEFT JOIN stock_location slp ON sl.location_id = slp.id
                    WHERE
                        sl.usage='internal'
                UNION
                    SELECT
                        sl.id AS loc_id, tp.top_parent_id
                    FROM
                        stock_location sl, top_parent tp
                    WHERE
                        sl.usage='internal' AND sl.location_id=tp.loc_id
            ), move_qties AS (
                SELECT
                    sm.id AS move_id,
                    sm.picking_id,
                    sm.location_id,
                    sm.product_id,
                    sum(sm.product_qty) OVER (
                        PARTITION BY sm.product_id, COALESCE(sm.picking_id, sm.location_id)
                        ORDER BY priority DESC, date_expected
                    ) - sm.product_qty AS qty
                FROM
                    stock_move sm
                WHERE
                    sm.state = 'confirmed'
                    AND sm.picking_type_id IS NOT NULL
                    AND sm.id NOT IN (
                    SELECT reservation_id FROM stock_quant WHERE reservation_id IS NOT NULL)
            )
            SELECT
                foo.move_id AS id,
                foo.move_id,
                foo.picking_id,
                foo.reserved
            FROM (
                    SELECT
                        sm.id AS move_id,
                        sm.picking_id AS picking_id,
                        TRUE AS reserved
                    FROM
                        stock_move sm
                    WHERE
                        sm.id IN (
                            SELECT sq.reservation_id FROM stock_quant sq WHERE sq.reservation_id IS NOT NULL)
                        AND sm.picking_type_id IS NOT NULL
                UNION ALL
                    SELECT DISTINCT
                        sm.id AS move_id,
                        sm.picking_id AS picking_id,
                        FALSE AS reserved
                    FROM
                        stock_move sm
                        LEFT JOIN stock_move smp ON smp.move_dest_id = sm.id
                        LEFT JOIN stock_move sms ON sm.split_from = sms.id
                        LEFT JOIN stock_move smps ON smps.move_dest_id = sms.id
                    WHERE
                        sm.state = 'waiting'
                        AND sm.picking_type_id IS NOT NULL
                        AND (smp.state = 'done' OR smps.state = 'done')
                UNION ALL
                    SELECT
                        mq.move_id,
                        mq.picking_id,
                        FALSE AS reserved
                    FROM
                        move_qties mq
                    WHERE
                        mq.qty <= (
                            SELECT
                                sum(qty)
                            FROM
                                stock_quant sq
                            WHERE
                                sq.reservation_id IS NULL
                                AND sq.location_id IN (
                                    SELECT loc_id FROM top_parent WHERE top_parent_id=mq.location_id
                                )
                                AND sq.product_id = mq.product_id)
            ) foo
        )
        """)
