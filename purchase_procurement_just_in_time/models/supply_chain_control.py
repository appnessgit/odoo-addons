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

from openerp.addons.connector.queue.job import job
from . import partner
from openerp.addons.connector.session import ConnectorSession, ConnectorSessionHandler
from openerp.osv import fields as old_api_fields

from openerp import models, fields, api, _
from openerp.tools.float_utils import float_round


@job
def job_update_supply_chain_controls(session, model_name, ids, context=None):
    model_instance = session.pool[model_name]
    handler = ConnectorSessionHandler(session.cr.dbname, session.uid, session.context)
    with handler.session() as session:
        result = model_instance.update_supply_chain_control(session.cr, session.uid, ids, context=context)
    return result


class SupplyChainControl(models.Model):
    _name = 'supply.chain.control'

    product_id = fields.Many2one('product.product', string=u"Product")
    seller_defined = fields.Boolean(string=u"Seller defined")
    main_seller_id = fields.Many2one('res.partner', string=u"Main seller")
    scheduler_active_for_seller = fields.Boolean(string=u"Scheduler active for seller")
    virtual_available = fields.Float(string=u"Forecast Quantity")
    draft_orders_qty = fields.Float(string=u"Draft orders quantity")
    oversupply_qty = fields.Float(string=u"Scheduler Oversupply quantity")
    missing_date = fields.Date(string=u"Date of first not covered need")

    @api.model
    def update_supply_chain_control(self):
        self.search([]).unlink()
        supplierinfos = self.env['product.supplierinfo'].search([])
        product_template_ids = [ps.product_tmpl_id.id for ps in supplierinfos]
        products = self.env['product.product'].search([('product_tmpl_id', 'in', product_template_ids)])
        index = 0
        while products:
            index += 1
            chunk_products = products[:500]
            products = products[500:]
            session = ConnectorSession(self.env.cr, self.env.uid, self.env.context)
            job_update_supply_chain_controls.delay(session, 'product.product', chunk_products.ids,
                                                   description="Update Supply Chain Control (chunk %s)" % index,
                                                   context=dict(self.env.context))

    @api.multi
    def open_product_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'name': self.product_id.display_name,
            'views': [(False, "form")],
            'res_id': self.product_id.id,
            'context': {}
        }

    @api.multi
    def action_show_evolution(self):
        self.ensure_one()
        return self.product_id.action_show_evolution()

    @api.multi
    def open_purchase_lines_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'name': _("Purchase order lines for product %s") % self.product_id.display_name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': {'search_default_product_id': self.product_id.id}
        }

    @api.multi
    def open_moves_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'name': _("Moves for product %s") % self.product_id.display_name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': {'search_default_product_id': self.product_id.id,
                        'search_default_ready': True,
                        'search_default_future': True,
                        'search_default_groupby_location_id': True,
                        'search_default_groupby_dest_location_id': True}
        }

    @api.multi
    def open_procurements_list(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'procurement.order',
            'name': _("Procurements for product %s") % self.product_id.display_name,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': {'search_default_product_id': self.product_id.id,
                        'search_default_group_procs_by_location': True,
                        'search_default_group_procs_by_state': True}
        }


class SupplyChainControlProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def get_available_qty_supply_control(self, available_quantities):
        return available_quantities

    @api.multi
    def get_missing_date(self):
        self.ensure_one()
        warehouse = self.get_warehouse_for_stock_report()
        level_report = self.env['stock.levels.report'].search([('warehouse_id', '=', warehouse.id),
                                                               ('product_id', '=', self.id),
                                                               ('qty', '<', 0)], order='date', limit=1)
        return level_report and level_report.date and level_report.date[:10] or False

    @api.multi
    def get_supplier_scheduler_data(self):
        self.ensure_one()
        seller_defined = True
        scheduler_active_for_seller = True
        companies = self.env['res.company'].search([])
        main_supplierinfo = self.get_main_supplierinfo()
        for company in companies:
            if seller_defined:
                supplierinfo = self.get_main_supplierinfo(force_company=company)
                seller = supplierinfo and supplierinfo.name or False
                if not seller:
                    seller_defined = False
                    scheduler_active_for_seller = False
                elif scheduler_active_for_seller:
                    if seller not in self.env['res.partner'].search(partner.DOMAIN_PARTNER_ACTIVE_SCHEDULER):
                        scheduler_active_for_seller = False
        return main_supplierinfo, seller_defined, scheduler_active_for_seller

    @api.multi
    def update_supply_chain_control(self):
        available_quantities = self._product_available()
        available_quantities = self.get_available_qty_supply_control(available_quantities)
        for product in self:
            draft_orders_qty = 0
            virtual_available = available_quantities.get(product.id) and \
                available_quantities[product.id].get('virtual_available', 0)
            draft_lines = self.env['purchase.order.line']. \
                search([('order_id.state', 'in', ['draft', 'bid', 'sent', 'confirmed']),
                        ('product_id', '=', product.id)])
            done_uoms = []
            for line in draft_lines:
                uom = line.product_uom
                if uom not in done_uoms:
                    done_uoms += [uom]
                    lines_uom = self.env['purchase.order.line'].search([('id', 'in', draft_lines.ids),
                                                                        ('product_uom', '=', uom.id)])
                    lines_uom_qty = sum([line.product_qty for line in lines_uom])
                    if uom == product.uom_id:
                        draft_orders_qty += lines_uom_qty
                    else:
                        draft_orders_qty += self.env['product.uom']._compute_qty(uom.id, lines_uom_qty,
                                                                                 product.uom_id.id)
            prec = product.uom_id.rounding
            missing_date = product.get_missing_date()
            main_supplierinfo, seller_defined, scheduler_active_for_seller = product.get_supplier_scheduler_data()
            self.env['supply.chain.control'].create(
                {'product_id': product.id,
                 'seller_defined': seller_defined,
                 'main_seller_id': main_supplierinfo and main_supplierinfo.name.id or False,
                 'scheduler_active_for_seller': scheduler_active_for_seller,
                 'virtual_available': float_round(virtual_available, precision_rounding=prec),
                 'draft_orders_qty': float_round(draft_orders_qty, precision_rounding=prec),
                 'oversupply_qty': float_round(min(draft_orders_qty + virtual_available, draft_orders_qty),
                                               precision_rounding=prec),
                 'missing_date': missing_date}
            )

    @api.multi
    def sanitize_purchase_order_lines(self):
        for rec in self:
            lines = self.env['purchase.order.line']. \
                search([('order_id.state', 'in', self.env['purchase.order'].get_purchase_order_states_with_moves()),
                        ('product_id', '=', rec.product_id.id)])
            for line in lines:
                line.adjust_moves_qties(line.product_qty)
