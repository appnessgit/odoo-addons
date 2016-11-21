# -*- coding: utf8 -*-
#
# Copyright (C) 2016 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp.exceptions import UserError
from openerp.tests import common


class TestStockQuantPackagesMovingWizard(common.TransactionCase):
    def setUp(self):
        super(TestStockQuantPackagesMovingWizard, self).setUp()

        self.product_a = self.browse_ref("stock_quant_packages_moving_wizard.product_a")
        self.product_b = self.browse_ref("stock_quant_packages_moving_wizard.product_b")
        self.lot_a = self.browse_ref("stock_quant_packages_moving_wizard.lot_a")
        self.lot_b = self.browse_ref("stock_quant_packages_moving_wizard.lot_b")
        self.header = self.browse_ref("stock_quant_packages_moving_wizard.package_header")
        self.header_2 = self.browse_ref("stock_quant_packages_moving_wizard.package_header_2")
        self.empty_package_source = self.browse_ref("stock_quant_packages_moving_wizard.empty_package_source")
        self.empty_package_dest = self.browse_ref("stock_quant_packages_moving_wizard.empty_package_dest")
        self.child = self.browse_ref("stock_quant_packages_moving_wizard.package_child")
        self.stock = self.browse_ref("stock.stock_location_stock")
        self.location_source = self.browse_ref("stock_quant_packages_moving_wizard.stock_location_source")
        self.location_dest = self.browse_ref("stock_quant_packages_moving_wizard.stock_location_dest")
        self.location_dest_shelf = self.browse_ref("stock_quant_packages_moving_wizard.stock_location_dest_shelf")
        self.quant_header_a = self.browse_ref("stock_quant_packages_moving_wizard.quant_header_a")
        self.quant_header_b = self.browse_ref("stock_quant_packages_moving_wizard.quant_header_b")
        self.quant_header_2 = self.browse_ref("stock_quant_packages_moving_wizard.quant_header_2")
        self.quant_child_a = self.browse_ref("stock_quant_packages_moving_wizard.quant_child_a")
        self.quant_child_b = self.browse_ref("stock_quant_packages_moving_wizard.quant_child_b")
        self.quant_child_c = self.browse_ref("stock_quant_packages_moving_wizard.quant_child_c")
        self.quant_child_d = self.browse_ref("stock_quant_packages_moving_wizard.quant_child_d")
        self.quant_no_pack_a = self.browse_ref("stock_quant_packages_moving_wizard.quant_a")
        self.quant_no_pack_b = self.browse_ref("stock_quant_packages_moving_wizard.quant_b")
        self.quant_other_loc = self.browse_ref("stock_quant_packages_moving_wizard.quant_other_loc")
        self.picking_type = self.browse_ref("stock.picking_type_internal")
        self.unit = self.browse_ref('product.product_uom_unit')

        self.supplier = self.browse_ref('stock.stock_location_suppliers')
        self.product1_auto_move = self.browse_ref('stock_quant_packages_moving_wizard.product1')
        self.product2_auto_move = self.browse_ref('stock_quant_packages_moving_wizard.product2')
        self.location_1 = self.browse_ref("stock_quant_packages_moving_wizard.stock_location_a")
        self.location_2 = self.browse_ref("stock_quant_packages_moving_wizard.stock_location_b")
        self.inventory_location = self.browse_ref('stock.location_inventory')

        self.env['stock.location']._parent_store_compute()
        self.env['stock.quant.package']._parent_store_compute()

    def check_in(self, data_tuple, lines):
        list_results = [(line.product_id, line.package_id, line.lot_id, line.qty,
                         line.parent_id, line.location_id) for line in lines]
        self.assertIn(data_tuple, list_results)
        result = lines.filtered(lambda line: line.product_id == data_tuple[0] and
                                line.package_id == data_tuple[1] and
                                line.lot_id == data_tuple[2] and
                                line.qty == data_tuple[3] and
                                line.parent_id == data_tuple[4])
        self.assertTrue(result)
        self.assertEqual(len(result), 1)
        return result

    def prepare_test_move_quant_package(self):

        lines = self.env['stock.product.line'].search([('location_id', 'in',
                                                        [self.location_source.id, self.location_dest.id])])
        self.assertEqual(len(lines), 11)
        no_product = self.env['product.product']
        no_pack = self.env['stock.quant.package']
        no_lot = self.env['stock.production.lot']
        line_1 = self.check_in((self.product_a, no_pack, self.lot_b, 50.0, no_pack, self.location_source), lines)
        line_2 = self.check_in((self.product_b, no_pack, no_lot, 2.0, no_pack, self.location_source), lines)
        line_3 = self.check_in((self.product_a, self.header_2, self.lot_a, 25.0, no_pack, self.location_source), lines)
        line_4 = self.check_in((self.product_a, self.header, self.lot_a, 15.0, no_pack, self.location_source), lines)
        line_5 = self.check_in((self.product_b, self.header, self.lot_b, 7.0, no_pack, self.location_source), lines)
        line_6 = self.check_in((self.product_a, self.child, no_lot, 10.0, self.header, self.location_source), lines)
        line_7 = self.check_in((self.product_b, self.child, self.lot_b, 11.0, self.header, self.location_source), lines)
        line_8 = self.check_in((self.product_a, self.child, self.lot_a, 8.0, self.header, self.location_source), lines)
        line_9 = self.check_in((no_product, self.header, no_lot, 0, no_pack, self.location_source), lines)
        line_10 = self.check_in((no_product, self.child, no_lot, 0, self.header, self.location_source), lines)
        line_11 = self.check_in((self.product_b, no_pack, no_lot, 10.0, no_pack, self.location_dest), lines)

        self.assertTrue(
            all([line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11]))
        return [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11]

    def test_10_move_packages(self):
        self.assertEqual(self.header.location_id, self.location_source)
        self.assertEqual(self.child.location_id, self.location_source)
        self.assertEqual(self.quant_header_a.location_id, self.location_source)
        self.assertEqual(self.quant_header_a.location_id, self.location_source)
        self.assertEqual(self.quant_child_a.location_id, self.location_source)
        self.assertEqual(self.quant_child_b.location_id, self.location_source)
        self.assertEqual(self.quant_child_c.location_id, self.location_source)

        do_move_w = self.env['stock.quant.package.move'].with_context(active_ids=[self.header.id]).create({
            'global_dest_loc': self.location_dest.id,
            'picking_type_id': self.picking_type.id,
            'is_manual_op': False
        })
        do_move_w.do_detailed_transfer()

        self.assertEqual(self.header.location_id, self.location_dest)
        self.assertEqual(self.child.location_id, self.location_dest)
        self.assertEqual(self.quant_header_a.location_id, self.location_dest)
        self.assertEqual(self.quant_header_b.location_id, self.location_dest)
        self.assertEqual(self.quant_child_a.location_id, self.location_dest)
        self.assertEqual(self.quant_child_b.location_id, self.location_dest)
        self.assertEqual(self.quant_child_c.location_id, self.location_dest)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest)

    def test_20_move_quant_lines(self):
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)

        do_move_w = self.env['stock.quant.move']. \
            with_context(active_ids=[self.quant_no_pack_a.id, self.quant_no_pack_b.id]).create(
            {
                'global_dest_loc': self.location_dest.id,
                'picking_type_id': self.picking_type.id,
                'is_manual_op': False
            })
        for item in do_move_w.pack_move_items:
            if item.quant == self.quant_no_pack_b:
                item.qty = 1
        do_move_w.do_transfer()

        self.assertEqual(self.quant_no_pack_a.location_id, self.location_dest)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_dest)
        self.assertEqual(self.quant_no_pack_a.qty, 50.0)
        self.assertEqual(self.quant_no_pack_b.qty, 1.0)

    def test_21_move_quant_lines_with_chain(self):

        move_a_1 = self.env['stock.move'].create({
            'name': "First move for product A",
            'product_id': self.product_a.id,
            'product_uom_qty': 10,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
            'priority': '0',
        })

        supply_move_a_1 = self.env['stock.move'].create({
            'name': "First supply move for product A",
            'product_id': self.product_a.id,
            'product_uom_qty': 10,
            'picking_type_id': self.picking_type.id,
            'location_id': self.supplier.id,
            'location_dest_id': self.location_source.id,
            'product_uom': self.unit.id,
            'move_dest_id': move_a_1.id,
        })

        move_a_2 = self.env['stock.move'].create({
            'name': "Second move for product A",
            'product_id': self.product_a.id,
            'product_uom_qty': 20,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
            'priority': '1',
        })

        supply_move_a_2 = self.env['stock.move'].create({
            'name': "Second supply move for product A",
            'product_id': self.product_a.id,
            'product_uom_qty': 20,
            'picking_type_id': self.picking_type.id,
            'location_id': self.supplier.id,
            'location_dest_id': self.location_source.id,
            'product_uom': self.unit.id,
            'move_dest_id': move_a_2.id,
        })

        move_a_1.action_confirm()
        supply_move_a_1.action_confirm()
        supply_move_a_1.action_assign()
        self.assertEqual(supply_move_a_1.state, 'assigned')
        supply_move_a_1.action_done()
        supply_quant_1 = supply_move_a_1.quant_ids
        self.assertEqual(len(supply_quant_1), 1)
        self.assertEqual(move_a_1.state, 'assigned')
        self.assertEqual(move_a_1.reserved_quant_ids, supply_quant_1)
        move_a_1.do_unreserve()
        self.assertFalse(move_a_1.reserved_quant_ids)

        move_a_2.action_confirm()
        supply_move_a_2.action_confirm()
        supply_move_a_2.action_assign()
        self.assertEqual(supply_move_a_2.state, 'assigned')
        supply_move_a_2.action_done()
        supply_quant_2 = supply_move_a_2.quant_ids
        self.assertEqual(len(supply_quant_2), 1)
        self.assertEqual(move_a_2.state, 'assigned')
        self.assertEqual(move_a_2.reserved_quant_ids, supply_quant_2)
        move_a_2.do_unreserve()
        self.assertFalse(move_a_2.reserved_quant_ids)

        do_move_w = self.env['stock.quant.move']. \
            with_context(active_ids=[supply_quant_1.id, self.quant_no_pack_b.id]).create(
            {
                'global_dest_loc': self.location_dest.id,
                'picking_type_id': self.picking_type.id,
                'is_manual_op': False
            })

        do_move_w.do_transfer()

        self.assertEqual(supply_quant_1.location_id, self.location_dest)
        self.assertEqual(supply_quant_1.qty, 10.0)
        self.assertEqual(supply_quant_2.location_id, self.location_source)
        self.assertEqual(supply_quant_2.qty, 20.0)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_dest)
        self.assertEqual(self.quant_no_pack_b.qty, 2.0)

        self.assertEqual(move_a_1.product_uom_qty, 10)
        self.assertEqual(move_a_1.state, 'done')
        self.assertEqual(move_a_1.quant_ids, supply_quant_1)
        self.assertEqual(move_a_2.product_uom_qty, 20)
        self.assertEqual(move_a_2.state, 'waiting')
        self.assertFalse(move_a_2.quant_ids)

    def test_30_move_quants_different_locations(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # We should not be able to move products from different locations
        with self.assertRaises(UserError):
            self.env['stock.product.line'].browse([line_1.id, line_11.id]).move_products()

    def test_31_move_entirely_quant_without_package(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_11.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.stock.id})
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertFalse(wizard.package_line_ids)
        self.assertEqual(wizard.quant_line_ids.qty, 10)
        wizard.move_products()
        self.assertEqual(self.quant_other_loc.location_id, self.stock)
        self.assertEqual(self.quant_other_loc.qty, 10)

    def test_32_move_partially_quants_without_packages(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_1.id, line_2.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertFalse(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 2)
        self.assertFalse(wizard.package_line_ids)
        [wizard_line_1, wizard_line_2] = [False] * 2
        for quant_line in wizard.quant_line_ids:
            if quant_line.product_id == self.product_a:
                wizard_line_1 = quant_line
            if quant_line.product_id == self.product_b:
                wizard_line_2 = quant_line
        self.assertTrue(wizard_line_1 and wizard_line_2)
        self.assertEqual(wizard_line_1.qty, 50)
        self.assertEqual(wizard_line_2.qty, 2)
        wizard_line_2.qty = 10
        # We should not be able to move more than available qty
        with self.assertRaises(UserError):
            wizard.move_products()
        wizard_line_1.qty = 20
        wizard_line_2.qty = 1.5
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertFalse(wizard.is_manual_op)
        result = wizard.move_products()
        self.assertTrue(result)
        picking = result[0].picking_id
        self.assertTrue(picking)
        self.assertEqual(picking.state, 'done')
        self.assertFalse(picking.backorder_id)
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_dest)
        self.assertEqual(self.quant_no_pack_a.qty, 20)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', False),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_b.id),
                                                        ('qty', '=', 30)]))
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_dest)
        self.assertEqual(self.quant_no_pack_b.qty, 1.5)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', False),
                                                        ('product_id', '=', self.product_b.id),
                                                        ('lot_id', '=', False),
                                                        ('qty', '=', 0.5)]))

    def test_33_move_entirely_quants_without_parents(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_4.id, line_5.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        # Let's force onchange to check field 'is_manual_op'. Here, the package has children, so it should be True
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 2)
        self.assertFalse(wizard.package_line_ids)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_header_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_a.qty, 15)
        self.assertFalse(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                         ('package_id', '=', self.header.id),
                                                         ('product_id', '=', self.product_a.id)]))
        self.assertEqual(self.quant_header_b.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_b.qty, 7)
        self.assertFalse(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                         ('package_id', '=', self.header.id),
                                                         ('product_id', '=', self.product_b.id)]))

    def test_34_move_partially_quants_without_parents(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_4.id, line_5.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 2)
        self.assertFalse(wizard.package_line_ids)
        [wizard_line_1, wizard_line_2] = [False] * 2
        for quant_line in wizard.quant_line_ids:
            if quant_line.product_id == self.product_a:
                wizard_line_1 = quant_line
            if quant_line.product_id == self.product_b:
                wizard_line_2 = quant_line
        self.assertTrue(wizard_line_1 and wizard_line_2)
        self.assertEqual(wizard_line_1.qty, 15)
        self.assertEqual(wizard_line_2.qty, 7)
        wizard_line_1.qty = 10
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_header_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_a.qty, 10)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.header.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 5)]))
        self.assertEqual(self.quant_header_b.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_b.qty, 7)
        self.assertFalse(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                         ('package_id', '=', self.header.id),
                                                         ('product_id', '=', self.product_b.id)]))
        self.assertEqual(self.header.location_id, self.location_source)

    def test_35_move_partially_quants_with_parents(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_6.id, line_7.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 2)
        self.assertFalse(wizard.package_line_ids)
        [wizard_line_1, wizard_line_2] = [False] * 2
        for quant_line in wizard.quant_line_ids:
            if quant_line.product_id == self.product_a:
                wizard_line_1 = quant_line
            if quant_line.product_id == self.product_b:
                wizard_line_2 = quant_line
        self.assertTrue(wizard_line_1 and wizard_line_2)
        self.assertEqual(wizard_line_1.qty, 10)
        self.assertEqual(wizard_line_2.qty, 11)
        wizard_line_1.qty = 5
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_child_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_a.qty, 5)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.child.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', False),
                                                        ('qty', '=', 5)]))
        self.assertEqual(self.quant_child_b.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_b.qty, 11)
        self.assertFalse(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                         ('package_id', '=', self.child.id),
                                                         ('product_id', '=', self.product_b.id),
                                                         ('lot_id', '=', self.lot_b.id)]))

    def test_36_move_entirely_line_with_several_quants(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertEqual(wizard.quant_line_ids.qty, 8)
        self.assertFalse(wizard.package_line_ids)
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.qty, 2)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.qty, 6)
        self.assertFalse(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                         ('package_id', '=', self.child.id),
                                                         ('product_id', '=', self.product_b.id),
                                                         ('lot_id', '=', self.lot_a.id)]))

    def test_37_move_partially_line_with_several_quants(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertEqual(wizard.quant_line_ids.qty, 8)
        wizard.quant_line_ids.qty = 6
        self.assertFalse(wizard.package_line_ids)
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.qty, 2)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.qty, 4)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.child.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 2)]))

    def test_38_move_quant_with_brother_quants(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_6.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        # Let's force onchange to check field 'is_manual_op'. Here, the package has children, so it should be True
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertFalse(wizard.package_line_ids)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_child_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_a.qty, 10)
        self.assertEqual(self.quant_child_b.location_id, self.location_source)
        self.assertEqual(self.quant_child_b.qty, 11)

    def test_39_move_partially_quant_no_parent_package(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_3.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        # Let's force onchange to check field 'is_manual_op'. Here, the package has children, so it should be True
        wizard.onchange_is_manual_op()
        self.assertFalse(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertEqual(wizard.quant_line_ids.qty, 25)
        wizard.quant_line_ids.qty = 15
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertFalse(wizard.package_line_ids)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
        picking.do_transfer()
        self.assertEqual(self.quant_header_2.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_2.qty, 15)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.header_2.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 10)]))

    def test_40_move_package_without_parent(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_9.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertFalse(wizard.is_manual_op)
        self.assertFalse(wizard.quant_line_ids)
        self.assertEqual(len(wizard.package_line_ids), 1)
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertFalse(wizard.is_manual_op)
        moves = wizard.move_products()
        self.assertTrue(moves)
        picking = moves[0].picking_id
        self.assertTrue(picking)
        self.assertEqual(picking.state, 'done')
        self.assertFalse(picking.backorder_id)
        self.assertEqual(len(moves), 2)
        [move1, move2] = [False] * 2
        for move in moves:
            self.assertEqual(move.state, 'done')
            self.assertEqual(move.remaining_qty, 0)
            if move.product_id == self.product_a:
                move1 = move
            if move.product_id == self.product_b:
                move2 = move
        self.assertTrue(move1 and move2)
        self.assertEqual(move1.product_uom_qty, 33)
        self.assertEqual(move2.product_uom_qty, 18)
        self.assertIn(self.quant_header_a, move1.quant_ids)
        self.assertIn(self.quant_header_b, move2.quant_ids)
        self.assertIn(self.quant_child_a, move1.quant_ids)
        self.assertIn(self.quant_child_b, move2.quant_ids)
        self.assertIn(self.quant_child_c, move1.quant_ids)
        self.assertIn(self.quant_child_d, move1.quant_ids)
        quants_a_dest_lot_a = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest.id),
                    ('lot_id', '=', self.lot_a.id)])
        quants_a_dest_no_lot = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest.id),
                    ('lot_id', '=', False)])
        quants_b_dest_lot_b = self.env['stock.quant']. \
            search([('product_id', '=', self.product_b.id),
                    ('location_id', '=', self.location_dest.id),
                    ('lot_id', '=', self.lot_b.id)])
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_lot_a]), 23)
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_no_lot]), 10)
        self.assertEqual(sum([quant.qty for quant in quants_b_dest_lot_b]), 18)
        for quant in quants_a_dest_lot_a:
            self.assertTrue(quant in [self.quant_child_c, self.quant_child_d, self.quant_header_a] or
                            move1 in quant.history_ids)
        for quant in quants_a_dest_no_lot:
            self.assertTrue(quant == self.quant_child_a or move1 in quant.history_ids)
        for quant in quants_b_dest_lot_b:
            self.assertTrue(quant in [self.quant_child_b, self.quant_header_b] or move2 in quant.history_ids)
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)
        self.assertEqual(self.quant_header_2.location_id, self.location_source)
        self.assertEqual(self.header.location_id, self.location_dest)
        self.assertEqual(self.child.location_id, self.location_dest)

    def test_41_move_package_with_parent(self):
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_10.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertFalse(wizard.quant_line_ids)
        self.assertEqual(len(wizard.package_line_ids), 1)
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertNotEqual(picking.state, 'done')
        self.assertEqual(len(picking.move_lines), 2)
        [move1, move2] = [False] * 2
        for move in picking.move_lines:
            self.assertEqual(move.state, 'assigned')
            self.assertEqual(move.remaining_qty, 0)
            if move.product_id == self.product_a:
                move1 = move
            if move.product_id == self.product_b:
                move2 = move
        self.assertTrue(move1 and move2)
        self.assertEqual(move1.product_uom_qty, 18)
        self.assertEqual(move2.product_uom_qty, 11)
        picking.do_transfer()
        self.assertIn(self.quant_child_a, move1.quant_ids)
        self.assertIn(self.quant_child_b, move2.quant_ids)
        self.assertIn(self.quant_child_c, move1.quant_ids)
        self.assertIn(self.quant_child_d, move1.quant_ids)
        quants_a_dest_lot_a = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', self.lot_a.id)])
        quants_a_dest_no_lot = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', False)])
        quants_b_dest_lot_b = self.env['stock.quant']. \
            search([('product_id', '=', self.product_b.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', self.lot_b.id)])
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_lot_a]), 8)
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_no_lot]), 10)
        self.assertEqual(sum([quant.qty for quant in quants_b_dest_lot_b]), 11)
        for quant in quants_a_dest_lot_a:
            self.assertTrue(quant in [self.quant_child_c, self.quant_child_d] or
                            move1 in quant.history_ids)
        for quant in quants_a_dest_no_lot:
            self.assertTrue(quant == self.quant_child_a or move1 in quant.history_ids)
        for quant in quants_b_dest_lot_b:
            self.assertTrue(quant == self.quant_child_b or move2 in quant.history_ids)
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)
        self.assertEqual(self.quant_header_2.location_id, self.location_source)
        self.assertEqual(self.header.location_id, self.location_source)
        self.assertEqual(self.child.location_id, self.location_dest_shelf)

    def test_42_two_included_lines(self):
        # line_9 countains line_4
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_4.id, line_9.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertEqual(len(wizard.package_line_ids), 1)
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertNotEqual(picking.state, 'done')
        picking.do_transfer()
        self.assertEqual(len(picking.move_lines), 2)
        [move1, move2] = [False] * 2
        for move in picking.move_lines:
            self.assertEqual(move.state, 'done')
            self.assertEqual(move.remaining_qty, 0)
            if move.product_id == self.product_a:
                move1 = move
            if move.product_id == self.product_b:
                move2 = move
        self.assertTrue(move1 and move2)
        self.assertEqual(move1.product_uom_qty, 33)
        self.assertEqual(move2.product_uom_qty, 18)
        self.assertIn(self.quant_header_a, move1.quant_ids)
        self.assertIn(self.quant_header_b, move2.quant_ids)
        self.assertIn(self.quant_child_a, move1.quant_ids)
        self.assertIn(self.quant_child_b, move2.quant_ids)
        self.assertIn(self.quant_child_c, move1.quant_ids)
        self.assertIn(self.quant_child_d, move1.quant_ids)
        quants_a_dest_lot_a = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', self.lot_a.id)])
        quants_a_dest_no_lot = self.env['stock.quant']. \
            search([('product_id', '=', self.product_a.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', False)])
        quants_b_dest_lot_b = self.env['stock.quant']. \
            search([('product_id', '=', self.product_b.id),
                    ('location_id', '=', self.location_dest_shelf.id),
                    ('lot_id', '=', self.lot_b.id)])
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_lot_a]), 23)
        self.assertEqual(sum([quant.qty for quant in quants_a_dest_no_lot]), 10)
        self.assertEqual(sum([quant.qty for quant in quants_b_dest_lot_b]), 18)
        for quant in quants_a_dest_lot_a:
            self.assertTrue(quant in [self.quant_child_c, self.quant_child_d, self.quant_header_a] or
                            move1 in quant.history_ids)
        for quant in quants_a_dest_no_lot:
            self.assertTrue(quant == self.quant_child_a or move1 in quant.history_ids)
        for quant in quants_b_dest_lot_b:
            self.assertTrue(quant in [self.quant_child_b, self.quant_header_b] or move2 in quant.history_ids)
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)
        self.assertEqual(self.quant_header_2.location_id, self.location_source)
        self.assertEqual(self.header.location_id, self.location_dest_shelf)
        self.assertEqual(self.child.location_id, self.location_dest_shelf)

    def test_43_change_move_of_picking(self):
        # Testing the recuperation of existing move
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        existing_move = self.env['stock.move'].create({
            'name': "Existing move",
            'product_id': self.product_a.id,
            'product_uom_qty': 1000,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
        })
        existing_move.action_confirm()
        self.quant_no_pack_a.quants_reserve([(self.quant_child_c, 2)], existing_move)

        existing_move.action_assign()
        self.assertEqual(existing_move.state, 'confirmed')
        existing_picking = existing_move.picking_id
        self.assertTrue(existing_picking)
        self.assertEqual(len(existing_picking.move_lines), 1)
        existing_picking.do_prepare_partial()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertFalse(wizard.package_line_ids)
        self.assertEqual(wizard.quant_line_ids.qty, 8)
        wizard.quant_line_ids.qty = 7
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)

        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertNotEqual(picking.state, 'done')
        self.assertEqual(len(picking.move_lines), 1)
        self.assertEqual(picking.move_lines, existing_move)

        # Testing that existing_move was indeed splitted, as quant_child_b (7 units asked instead of 8 or 1000)
        self.assertEqual(existing_move.product_uom_qty, 7)
        picking.do_transfer()
        self.assertEqual(existing_move.state, 'done')
        self.assertEqual(len(existing_move.quant_ids), 2)
        self.assertIn(self.quant_child_c, existing_move.quant_ids)
        self.assertIn(self.quant_child_d, existing_move.quant_ids)
        self.assertEqual(picking.state, 'done')
        self.assertFalse(picking.backorder_id)
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.qty, 2)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.qty, 5)
        self.assertEqual(existing_move.product_uom_qty, 7)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.child.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 1)]))

    def test_44_change_quant_to_a_new_move(self):
        # Same kind of test as last one, but now, the existing move does not match the requirements
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        existing_move = self.env['stock.move'].create({
            'name': "Existing move",
            'product_id': self.product_a.id,
            'product_uom_qty': 1000,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.stock.id,
            'product_uom': self.unit.id,
        })

        existing_move.action_confirm()
        self.quant_no_pack_a.quants_reserve([(self.quant_child_d, 6)], existing_move)

        existing_move.action_assign()
        self.assertEqual(existing_move.state, 'confirmed')
        existing_picking = existing_move.picking_id
        self.assertTrue(existing_picking)
        self.assertEqual(len(existing_picking.move_lines), 1)
        existing_picking.do_prepare_partial()
        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertFalse(wizard.package_line_ids)
        self.assertEqual(wizard.quant_line_ids.qty, 8)
        wizard.quant_line_ids.qty = 7
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)

        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertNotEqual(picking.state, 'done')
        self.assertEqual(len(picking.move_lines), 1)
        self.assertNotEqual(picking.move_lines, existing_move)
        new_move = picking.move_lines
        self.assertEqual(new_move.product_uom_qty, 7)

        picking.do_transfer()
        self.assertEqual(new_move.state, 'done')
        self.assertEqual(len(new_move.quant_ids), 2)
        self.assertIn(self.quant_child_c, new_move.quant_ids)
        self.assertIn(self.quant_child_d, new_move.quant_ids)
        self.assertEqual(picking.state, 'done')
        self.assertFalse(picking.backorder_id)
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.qty, 2)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.qty, 5)
        self.assertEqual(new_move.product_uom_qty, 7)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.child.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 1)]))

    def test_45_change_quant_of_move(self):
        # Same kind of test as last one: the existing move does not match the requirements, but it can now be attached
        # to another existing move
        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()
        not_corresponding_move = self.env['stock.move'].create({
            'name': "Existing move",
            'product_id': self.product_a.id,
            'product_uom_qty': 1000,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.stock.id,
            'product_uom': self.unit.id,
        })

        not_corresponding_move.action_confirm()
        self.quant_no_pack_a.quants_reserve([(self.quant_child_d, 6)], not_corresponding_move)

        not_corresponding_move.action_assign()
        self.assertEqual(not_corresponding_move.state, 'confirmed')
        existing_picking = not_corresponding_move.picking_id
        self.assertTrue(existing_picking)
        self.assertEqual(len(existing_picking.move_lines), 1)
        existing_picking.do_prepare_partial()

        corresponding_move = self.env['stock.move'].create({
            'name': "Existing move",
            'product_id': self.product_a.id,
            'product_uom_qty': 1000,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
        })
        corresponding_move.action_confirm()
        self.assertTrue(corresponding_move.picking_id)

        # Partial move
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
            create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)
        self.assertEqual(len(wizard.quant_line_ids), 1)
        self.assertFalse(wizard.package_line_ids)
        self.assertEqual(wizard.quant_line_ids.qty, 8)
        wizard.quant_line_ids.qty = 7
        # Let's force onchange to check field 'is_manual_op'
        wizard.onchange_is_manual_op()
        self.assertTrue(wizard.is_manual_op)

        action = wizard.move_products()
        picking_id = action.get('res_id')
        self.assertTrue(picking_id)
        picking = self.env['stock.picking'].browse(picking_id)
        self.assertNotEqual(picking.state, 'done')
        self.assertEqual(len(picking.move_lines), 1)
        self.assertNotEqual(picking.move_lines, not_corresponding_move)
        self.assertEqual(picking.move_lines, corresponding_move)
        self.assertEqual(corresponding_move.product_uom_qty, 7)

        picking.do_transfer()
        self.assertEqual(corresponding_move.state, 'done')
        self.assertEqual(len(corresponding_move.quant_ids), 2)
        self.assertIn(self.quant_child_c, corresponding_move.quant_ids)
        self.assertIn(self.quant_child_d, corresponding_move.quant_ids)
        self.assertEqual(picking.state, 'done')
        self.assertFalse(picking.backorder_id)
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.qty, 2)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.qty, 5)
        self.assertEqual(corresponding_move.product_uom_qty, 7)
        self.assertTrue(self.env['stock.quant'].search([('location_id', '=', self.location_source.id),
                                                        ('package_id', '=', self.child.id),
                                                        ('product_id', '=', self.product_a.id),
                                                        ('lot_id', '=', self.lot_a.id),
                                                        ('qty', '=', 1)]))

    # TODO: porter stock_performance_imroved en 9.0 puis rajouter ce test
    # def test_46_change_quant_of_move(self):
    #     # Reserving a big quant on a small move
    #
    #     [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
    #         self.prepare_test_move_quant_package()
    #     existing_move_1 = self.env['stock.move'].create({
    #         'name': "Existing move",
    #         'product_id': self.product_a.id,
    #         'product_uom_qty': 5,
    #         'picking_type_id': self.picking_type.id,
    #         'location_id': self.location_source.id,
    #         'location_dest_id': self.location_dest.id,
    #         'product_uom': self.unit.id,
    #     })
    #
    #     existing_move_2 = self.env['stock.move'].create({
    #         'name': "Existing move 2",
    #         'product_id': self.product_a.id,
    #         'product_uom_qty': 2,
    #         'picking_type_id': self.picking_type.id,
    #         'location_id': self.location_source.id,
    #         'location_dest_id': self.location_dest.id,
    #         'product_uom': self.unit.id,
    #     })
    #
    #     existing_move_1.action_confirm()
    #     existing_move_2.action_confirm()
    #
    #     wizard = self.env['product.move.wizard'].with_context(active_ids=[line_8.id]). \
    #         create({'picking_type_id': self.picking_type.id, 'global_dest_loc': self.location_dest.id})
    #
    #     wizard.onchange_is_manual_op()
    #     self.assertTrue(wizard.is_manual_op)
    #     self.assertEqual(len(wizard.quant_line_ids), 1)
    #     self.assertFalse(wizard.package_line_ids)
    #     self.assertEqual(wizard.quant_line_ids.qty, 8)
    #     # Let's force onchange to check field 'is_manual_op'
    #     wizard.onchange_is_manual_op()
    #     self.assertTrue(wizard.is_manual_op)
    #
    #     action = wizard.move_products()
    #     picking_id = action.get('res_id')
    #     self.assertTrue(picking_id)
    #     picking = self.env['stock.picking'].browse(picking_id)
    #     self.assertNotEqual(picking.state, 'done')
    #     self.assertEqual(len(picking.move_lines), 3)
    #     self.assertIn(existing_move_1, picking.move_lines)
    #     self.assertIn(existing_move_2, picking.move_lines)
    #     new_move = picking.move_lines.filtered(lambda move: move not in [existing_move_1, existing_move_2])
    #     self.assertEqual(new_move.product_uom_qty, 1)
    #
    #     picking.do_transfer()
    #     self.assertEqual(existing_move_1.state, 'done')
    #     # self.assertEqual(self.quant_child_a, existing_move_1.quant_ids)
    #     self.assertEqual(existing_move_2.state, 'done')
    #     self.assertEqual(new_move.state, 'done')
    #     self.assertEqual(picking.state, 'done')
    #     self.assertFalse(picking.backorder_id)
    #     self.assertEqual(self.quant_child_a.location_id, self.location_source)
    #     self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
    #     self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
    #     self.assertEqual(self.quant_child_a.qty, 10)
    #
    #     quants = self.env['stock.quant'].search([('location_id', '=', self.location_dest_shelf.id),
    #                                              ('package_id', '=', False),
    #                                              ('product_id', '=', self.product_a.id)])
    #
    #     self.assertEqual(sum([quant.qty for quant in quants]), 8)

    def test_47_moves_reconciliation(self):
        """
        Testing quants reconciliation for not synchronized auto moves
        """

        move_to_set_auto = self.env["stock.move"].create({
            'name': "Auto move",
            'product_id': self.product1_auto_move.id,
            'product_uom': self.unit.id,
            'product_uom_qty': 30,
            'location_id': self.location_1.id,
            'location_dest_id': self.location_2.id,
            'picking_type_id': self.picking_type.id,
            # 'auto_move': False,
            'picking_id': False
        })
        move_to_set_auto.action_confirm()
        self.assertTrue(move_to_set_auto.picking_id)

        move_neg = self.env["stock.move"].create({
            'name': "Move 2",
            'product_id': self.product1_auto_move.id,
            'product_uom': self.unit.id,
            'product_uom_qty': 30,
            'location_id': self.location_2.id,
            'location_dest_id': self.inventory_location.id,
            'picking_type_id': self.picking_type.id,
            # 'auto_move': False,
            'picking_id': False
        })
        move_neg.action_done()
        neg_quant = move_neg.quant_ids.filtered(lambda quant: quant.qty < 0)
        pos_quant_linked_to_neg = move_neg.quant_ids.filtered(lambda quant: quant.qty > 0)
        self.assertEqual(len(neg_quant), 1)
        self.assertEqual(len(pos_quant_linked_to_neg), 1)
        # print 'neg_pos', neg_quant, pos_quant_linked_to_neg

        move_pos = self.env["stock.move"].create({
            'name': "Move 2",
            'product_id': self.product1_auto_move.id,
            'product_uom': self.unit.id,
            'product_uom_qty': 30,
            'location_id': self.supplier.id,
            'location_dest_id': self.location_1.id,
            'picking_type_id': self.picking_type.id,
            'move_dest_id': move_to_set_auto.id,
            # 'auto_move': False,
            'picking_id': False
        })
        move_pos.action_done()
        pos_quant = move_pos.quant_ids.filtered(lambda quant: quant.qty > 0)
        self.assertEqual(len(pos_quant), 1)
        # print 'pos_quant', pos_quant

        move_to_set_auto.do_unreserve()
        self.assertEqual(move_to_set_auto.state, 'waiting')

        # print 'move_to_set_auto', move_to_set_auto, move_to_set_auto.state
        moves2 = pos_quant.move_to(self.location_2, self.picking_type,
                                   move_items={self.product1_auto_move: [{'quants': pos_quant, 'qty': 30}]})
        # print 'moves2', moves2
        picking2 = moves2[0].picking_id
        # print 'picking2', picking2.state, picking2.move_lines
        self.assertTrue(picking2)

        # print 'quants_result'
        # print pos_quant_linked_to_neg, pos_quant_linked_to_neg.qty
        # for quant in self.env['stock.quant'].search([('product_id', '=', self.product1_auto_move.id)]):
        #     print quant, quant.qty, quant.location_id.display_name

        # Let's test that quants were reconcilied
        self.assertFalse(self.env['stock.quant'].search([('product_id', '=', self.product1_auto_move.id),
                                                         ('location_id', 'not in',
                                                          [self.inventory_location.id, self.supplier.id])]))

    def test_60_move_to_package(self):
        """
        Put alone quants and a package into another one
        """

        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()

        # Test moving only a part of a package
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_4.id]). \
            create({'move_to': 'package', 'package_id': self.empty_package_source.id})
        with self.assertRaises(UserError):
            wizard.move_products()

        # Test implicit unpacking
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_4.id]). \
            create({'move_to': 'package', 'package_id': self.empty_package_source.id})
        with self.assertRaises(UserError):
            wizard.move_products()

        # Test moving to wrong location
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_1.id, line_2.id, line_9.id]). \
            create({'move_to': 'package', 'package_id': self.empty_package_dest.id})
        with self.assertRaises(UserError):
            wizard.move_products()

        # Real test
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_1.id, line_2.id, line_9.id]). \
            create({'move_to': 'package', 'package_id': self.empty_package_source.id})
        wizard.move_products()
        self.assertEqual(self.empty_package_source.location_id, self.location_source)

        # Let's check quants no packages
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_a.package_id, self.empty_package_source)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)
        self.assertEqual(self.quant_no_pack_b.package_id, self.empty_package_source)

        # Let's check quants header 2
        self.assertEqual(self.header_2.location_id, self.location_source)
        self.assertFalse(self.header_2.parent_id)
        self.assertEqual(self.quant_header_2.location_id, self.location_source)
        self.assertEqual(self.quant_header_2.package_id, self.header_2)

        # Let's check quants header
        self.assertEqual(self.header.location_id, self.location_source)
        self.assertEqual(self.header.parent_id, self.empty_package_source)
        self.assertEqual(self.quant_header_a.location_id, self.location_source)
        self.assertEqual(self.quant_header_a.package_id, self.header)
        self.assertEqual(self.quant_header_b.location_id, self.location_source)
        self.assertEqual(self.quant_header_b.package_id, self.header)

        # Let's check quants child
        self.assertEqual(self.child.location_id, self.location_source)
        self.assertEqual(self.child.parent_id, self.header)
        self.assertEqual(self.quant_child_a.location_id, self.location_source)
        self.assertEqual(self.quant_child_a.package_id, self.child)
        self.assertEqual(self.quant_child_b.location_id, self.location_source)
        self.assertEqual(self.quant_child_b.package_id, self.child)
        self.assertEqual(self.quant_child_c.location_id, self.location_source)
        self.assertEqual(self.quant_child_c.package_id, self.child)
        self.assertEqual(self.quant_child_d.location_id, self.location_source)
        self.assertEqual(self.quant_child_d.package_id, self.child)

    def test_70_execute_packops(self):
        """
        Executing packops with quants and packages lines and creating a backorder
        """

        [line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8, line_9, line_10, line_11] = \
            self.prepare_test_move_quant_package()

        move1 = self.env['stock.move'].create({
            'name': "Existing move",
            'product_id': self.product_a.id,
            'product_uom_qty': 108,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
        })

        move2 = self.env['stock.move'].create({
            'name': "Existing move 2",
            'product_id': self.product_b.id,
            'product_uom_qty': 20,
            'picking_type_id': self.picking_type.id,
            'location_id': self.location_source.id,
            'location_dest_id': self.location_dest.id,
            'product_uom': self.unit.id,
        })
        move1.action_confirm()
        move2.action_confirm()
        picking = move1.picking_id
        self.assertTrue(picking)
        self.assertEqual(move2.picking_id, picking)

        picking.action_assign()
        self.assertEqual(picking.state, 'assigned')
        self.assertEqual(move1.state, 'assigned')
        self.assertEqual(move2.state, 'assigned')
        self.assertEqual(len(move1.reserved_quant_ids), 6)
        self.assertIn(self.quant_no_pack_a, move1.reserved_quant_ids)
        self.assertIn(self.quant_header_2, move1.reserved_quant_ids)
        self.assertIn(self.quant_header_a, move1.reserved_quant_ids)
        self.assertIn(self.quant_child_a, move1.reserved_quant_ids)
        self.assertIn(self.quant_child_c, move1.reserved_quant_ids)
        self.assertIn(self.quant_child_d, move1.reserved_quant_ids)
        self.assertEqual(len(move2.reserved_quant_ids), 3)
        self.assertIn(self.quant_no_pack_b, move2.reserved_quant_ids)
        self.assertIn(self.quant_header_b, move2.reserved_quant_ids)
        self.assertIn(self.quant_child_b, move2.reserved_quant_ids)

        self.assertEqual(len(picking.pack_operation_ids), 4)
        self.assertIn([self.product_a, self.env['stock.quant.package'], 50],
                      [[op.product_id, op.package_id, op.product_qty] for op in picking.pack_operation_ids])
        self.assertIn([self.product_b, self.env['stock.quant.package'], 2],
                      [[op.product_id, op.package_id, op.product_qty] for op in picking.pack_operation_ids])
        self.assertIn([self.env['product.product'], self.header, 1],
                      [[op.product_id, op.package_id, op.product_qty] for op in picking.pack_operation_ids])
        self.assertIn([self.env['product.product'], self.header_2, 1],
                      [[op.product_id, op.package_id, op.product_qty] for op in picking.pack_operation_ids])

        # Let's execute packop of package header
        wizard = self.env['product.move.wizard'].with_context(active_ids=[line_9.id]). \
            create({'move_to': 'execute_packops'})
        wizard.move_products()

        # Let's check quants no packages
        self.assertEqual(self.quant_no_pack_a.location_id, self.location_source)
        self.assertFalse(self.quant_no_pack_a.package_id)
        self.assertEqual(self.quant_no_pack_b.location_id, self.location_source)
        self.assertFalse(self.quant_no_pack_b.package_id)

        # Let's check quants header 2
        self.assertEqual(self.header_2.location_id, self.location_source)
        self.assertFalse(self.header_2.parent_id)
        self.assertEqual(self.quant_header_2.location_id, self.location_source)
        self.assertEqual(self.quant_header_2.package_id, self.header_2)

        # Let's check quants header
        self.assertEqual(self.header.location_id, self.location_dest_shelf)
        self.assertFalse(self.header.parent_id)
        self.assertEqual(self.quant_header_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_a.package_id, self.header)
        self.assertEqual(self.quant_header_b.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_header_b.package_id, self.header)

        # Let's check quants child
        self.assertEqual(self.child.location_id, self.location_dest_shelf)
        self.assertEqual(self.child.parent_id, self.header)
        self.assertEqual(self.quant_child_a.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_a.package_id, self.child)
        self.assertEqual(self.quant_child_b.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_b.package_id, self.child)
        self.assertEqual(self.quant_child_c.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_c.package_id, self.child)
        self.assertEqual(self.quant_child_d.location_id, self.location_dest_shelf)
        self.assertEqual(self.quant_child_d.package_id, self.child)
