# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (c) 2015 Domatix (http://www.domatix.com)
#                       info <email@domatix.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

import odoo.addons.decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = 'sale.order'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)
            if line.product_id.pack:
                if line.product_id.pack_line_ids:
                    for product_line in line.product_id.pack_line_ids:
                        vals = line._prepare_order_line_procurement_pack(group_id=line.order_id.procurement_group_id.id,product_id=product_line.product_id.id,quantity=product_line.quantity)
                        new_proc = self.env["procurement.order"].with_context(procurement_autorun_defer=True).create(vals)
                        new_proc.message_post_with_view('mail.message_origin_link',
                            values={'self': new_proc, 'origin': line.order_id},
                            subtype_id=self.env.ref('mail.mt_note').id)
                        new_procs += new_proc
            else:
                vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
                vals['product_qty'] = line.product_uom_qty - qty
                new_proc = self.env["procurement.order"].with_context(procurement_autorun_defer=True).create(vals)
                new_proc.message_post_with_view('mail.message_origin_link',
                    values={'self': new_proc, 'origin': line.order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)
                new_procs += new_proc
        new_procs.run()
        return new_procs


    @api.multi
    def _prepare_order_line_procurement_pack(self, group_id=False,product_id=False,quantity=False):
        self.ensure_one()
        date_planned = datetime.strptime(self.order_id.date_order, DEFAULT_SERVER_DATETIME_FORMAT)\
            + timedelta(days=self.customer_lead or 0.0) - timedelta(days=self.order_id.company_id.security_lead)
        qty_product = self.product_uom_qty
        qty_total = qty_product * quantity
        return {
            'name': self.name,
            'origin': self.order_id.name,
            'date_planned': date_planned.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'location_id': self.order_id.partner_shipping_id.property_stock_customer.id,
            'route_ids': self.route_id and [(4, self.route_id.id)] or [],
            'warehouse_id': self.order_id.warehouse_id and self.order_id.warehouse_id.id or False,
            'partner_dest_id': self.order_id.partner_shipping_id.id,
            'product_id': product_id,
            'product_qty': qty_total,
            'product_uom': self.product_uom.id,
            'company_id': self.order_id.company_id.id,
            'group_id': group_id,
            'sale_line_id': self.id
        }
