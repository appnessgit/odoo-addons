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

{
    'name': 'Stock Performance Improved',
    'version': '0.1',
    'author': 'NDP Systèmes',
    'maintainer': 'NDP Systèmes',
    'category': 'Technical Settings',
    'depends': ['scheduler_async'],
    'description': """
Stock Performance Improved
==========================
Odoo is naturally optimized for situations where the stock is plenty and moves made on request with a relatively short
notice. This is typically the case of a retail store or a logistics company.

However, there are other situations where the stock is kept to minimum but the forecast moves are known well in
advance. This is typically the case of an industrial company with a long term planning applying just-in-time
procurement.

This module applies performance improvements by giving the possibility to assign stock moves to a stock picking at
latest, that is only when it can be reserved. This is done by setting the defer_picking_assign parameter to True in a
stock picking. It can also be definied in procurement rules so that the resulting moves have this parameter set.

This module also removes the 'Run all schedulers' since this can lead to memory outages. Instead, we now have 3 new
menus to finely control the scheduler:
- one to run confirmed procurements,
- one to check running procurements,
- one to try to assign moves
""",
    'website': 'http://www.ndp-systemes.fr',
    'data': [
        'security/ir.model.access.csv',
        'stock_performance_improved_view.xml',
        'stock_performance_improved_data.xml',
    ],
    'demo': [
        'stock_performance_improved_demo.xml',
    ],
    'test': [],
    'installable': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}

