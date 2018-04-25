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

from openerp import models, fields, api
from openerp.addons.connector.session import ConnectorSession
from .product import create_needed_orderpoint_for_product

class StockProcurementJitConfig(models.TransientModel):
    _inherit = 'stock.config.settings'

    required_orderpoint_location_ids = fields.Many2many('stock.location', string=u"Required Orderpoint Location")

    @api.multi
    def update_orderpoint(self):
        if self.env.context.get('jobify', True):
            create_needed_orderpoint_for_product.delay(ConnectorSession.from_env(self.env), self.env.context)
        else:
            create_needed_orderpoint_for_product(ConnectorSession.from_env(self.env), self.env.context)

    @api.multi
    def get_default_required_orderpoint_location_ids(self):
        required_orderpoint_location_ids = self.env['ir.config_parameter'].get_param(
            "stock_location_orderpoint.required_orderpoint_location_ids", default="[]")
        return {'required_orderpoint_location_ids': eval(required_orderpoint_location_ids)}

    @api.multi
    def set_required_orderpoint_location_ids(self):
        config_parameters = self.env["ir.config_parameter"]
        for record in self:
            config_parameters.set_param("stock_location_orderpoint.required_orderpoint_location_ids",
                                        record.required_orderpoint_location_ids.ids)
