# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from odoo import models, _, fields, api
from datetime import datetime
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        if self.currency_id and self.pricelist_id:
            if self.currency_id.name == 'GBP' or self.pricelist_id.name == 'GBP':
                if not self.currency_id.date:
                    raise Warning(_("There is no rate assigned to the currency."))
                if self.currency_id.date < datetime.now().strftime('%Y-%m-%d'):
                    raise Warning(_("Date rate is different from today."))
                pricelist_obj = self.env['product.pricelist']
                currency_obj = self.env['res.currency']
                pricelist_id = pricelist_obj.search([('name','=','EUR')])
                currency_id = currency_obj.search([('name','=','EUR')])
                currency_tax = self.pricelist_id.currency_id.rate
                for line in self.order_line:
                    line.price_unit_before = line.price_unit
                    line.price_unit = line.price_unit / currency_tax
                    if currency_id:
                        line.currency_id = currency_id.id

                if pricelist_id:
                    self.pricelist_id = pricelist_id.id

        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_cancel(self):
        if self.currency_id and self.pricelist_id and self.order_line[0].price_unit_before and self.partner_id.country_id.code == 'GB':
            if self.currency_id.name == 'EUR' or self.pricelist_id.name == 'EUR':
                pricelist_obj = self.env['product.pricelist']
                currency_obj = self.env['res.currency']
                pricelist_id = pricelist_obj.search([('name','=','GBP')])
                currency_id = currency_obj.search([('name','=','GBP')])
                for line in self.order_line:
                    line.price_unit = line.price_unit_before
                    if currency_id:
                        line.currency_id = currency_id.id
                    if pricelist_id:
                        self.pricelist_id = pricelist_id.id

        return super(SaleOrder, self).action_cancel()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    price_unit_before = fields.Float(string='Unit Price Before', digits=dp.get_precision('Product Price'))
