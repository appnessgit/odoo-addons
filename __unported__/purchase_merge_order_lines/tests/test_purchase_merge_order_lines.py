# -*- coding: utf8 -*-
#
#    Copyright (C) 2016 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp.tests import common


class TestPurchaseMergeOrderLines(common.TransactionCase):

    def setUp(self):
        super(TestPurchaseMergeOrderLines, self).setUp()
        self.product = self.browse_ref('purchase_merge_order_lines.test_product')
        self.incoterm1 = self.browse_ref('stock.incoterm_EXW')
        self.incoterm2 = self.browse_ref('stock.incoterm_FCA')
        self.payment_term_1 = self.browse_ref('account.account_payment_term_15days')
        self.payment_term_2 = self.browse_ref('account.account_payment_term')
        self.stock = self.browse_ref('stock.stock_location_stock')
        self.buy_rule = self.browse_ref('purchase_merge_order_lines.buy_rule')

    def create_procurement_order_1(self):
        return self.env['procurement.order'].create({
            'name': 'Procurement order 5 (Sirail Achats)',
            'product_id': self.product.id,
            'product_qty': 80,
            'warehouse_id': self.ref('stock.warehouse0'),
            'location_id': self.stock.id,
            'date_planned': '2016-02-08 14:37:00',
            'product_uom': self.ref('product.product_uom_unit'),
            'rule_id': self.buy_rule.id
        })

    def create_procurement_order_2(self):
        return self.env['procurement.order'].create({
            'name': 'Procurement order 6 (Sirail Achats)',
            'product_id': self.product.id,
            'product_qty': 80,
            'warehouse_id': self.ref('stock.warehouse0'),
            'location_id': self.stock.id,
            'date_planned': '2015-02-08 14:37:00',
            'product_uom': self.ref('product.product_uom_unit'),
            'rule_id': self.buy_rule.id
        })

    def test_10_purchase_merge_order_lines(self):

        procurement1 = self.create_procurement_order_1()
        procurement2 = self.create_procurement_order_2()

        self.assertFalse(procurement1.purchase_line_id)
        self.assertFalse(procurement1.purchase_id)
        self.assertFalse(procurement2.purchase_line_id)
        self.assertFalse(procurement2.purchase_id)
        procurement1.run()
        self.assertTrue(procurement1.purchase_id)
        self.assertTrue(procurement1.purchase_line_id)
        order1 = procurement1.purchase_line_id.order_id
        self.assertEqual(order1, procurement1.purchase_id)

        procurement2.run()
        self.assertTrue(procurement2.purchase_line_id)
        order2 = procurement2.purchase_line_id.order_id
        self.assertNotEqual(order1, order2)
        self.assertEqual(len(order1.order_line), 1)
        self.assertEqual(order1.order_line.product_qty, 100)
        self.assertEqual(len(order2.order_line), 1)
        self.assertEqual(order2.order_line.product_qty, 100)
        self.assertEqual(order2, procurement2.purchase_id)

        self.assertEqual(order1.state, 'draft')
        self.assertEqual(order2.state, 'draft')
        order1.write({'incoterm_id': self.incoterm1.id, 'payment_term_id': self.payment_term_1.id})
        order2.write({'incoterm_id': self.incoterm2.id, 'payment_term_id': self.payment_term_2.id})
        self.assertGreater(order1.date_order, order2.date_order)

        result = order1.search([('id', 'in', [order1.id, order2.id])]). \
            with_context(merge_different_dates=True).do_merge()
        lst = result.get(order2.id + 1)
        self.assertEqual(len(lst), 2)
        self.assertIn(order1.id, lst)
        self.assertIn(order2.id, lst)
        merged_order = order1.search([('id', '=', order2.id + 1)])

        self.assertEqual(len(merged_order), 1)
        self.assertEqual(len(merged_order.order_line), 1)
        self.assertEqual(merged_order.order_line.product_qty, 160)
        self.assertEqual(len(merged_order.order_line.procurement_ids), 2)
        self.assertIn(procurement1, merged_order.order_line.procurement_ids)
        self.assertIn(procurement2, merged_order.order_line.procurement_ids)

        self.assertEqual(merged_order.incoterm_id, self.incoterm2)
        self.assertEqual(merged_order.payment_term_id, self.payment_term_2)
