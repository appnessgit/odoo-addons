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
    'name': 'Action Top Buttons For Views',
    'version': '0.1',
    'author': 'NDP Systèmes',
    'maintainer': 'NDP Systèmes',
    'category': 'Dependency',
    'depends': ['web'],
    'description': """
Action Top Buttons For Views
============================
This module enables action buttons to be put directly next to "Print" and "More" instead of having them necessarily
inside those menus.

Usage: set the usage to 'top_button' in an action that you have added to "Print" or "More" menus to have its button
directly displayed.

You can hide "Print" and "More" buttons. 
You have to add key 'hide_default_sidebar_buttons' in flags of the act_window
'flags': {
    'search_view': True,
    'sidebar': True,
    'hide_default_sidebar_buttons': True,
}
""",
    'website': 'http://www.ndp-systemes.fr',
    'data': [
        'web_action_top_button.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
    'application': False,
}
