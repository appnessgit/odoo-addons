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

from odoo import models, api
from odoo.tools import float_compare


class FixNullQuantsStockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _quant_split(self, qty):
        # Is split qty is almost 0, we return an empty quant recordset
        # We will have to check if this does not break stock_account
        self.ensure_one()
        if float_compare(qty, 0, precision_rounding=self.product_id.uom_id.rounding) == 0:
            return self.env['stock.quant']
        else:
            return super(FixNullQuantsStockQuant, self)._quant_split(qty)
