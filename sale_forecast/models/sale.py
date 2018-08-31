# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp


class SaleForecast(models.Model):
    _name = 'sale.forecast'

    name = fields.Char(string='Name', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    forecast_lines = fields.One2many('sale.forecast.line',
                                     'forecast_id', string="Forecast Lines")

    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from >= self.date_to:
            raise exceptions.Warning(_('Error! Date to must be lower '
                                       'than date from.'))

    @api.multi
    def recalculate_actual_qty(self):
        sale_obj = self.env['sale.order.line']
        prod_obj = self.env['product.product']
        for record in self.forecast_lines:
            if record.product_id:
                if record.partner_id:
                    sale_ids = sale_obj.search([
                        ('product_id', '=', record.product_id.id),
                        ('order_id.partner_id', '=', record.partner_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                else:
                    sale_ids = sale_obj.search([
                        ('product_id', '=', record.product_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))

            elif record.product_category_id:
                product_ids = prod_obj.search([
                    ('categ_id', '=', record.product_category_id.id)])
                if record.partner_id:
                    sale_ids = sale_obj.search([
                        ('product_id', 'in', product_ids.ids),
                        ('order_id.partner_id', '=', record.partner_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                else:
                    sale_ids = sale_obj.search([
                        ('product_id', 'in', product_ids.ids),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))


class SaleForecastLine(models.Model):

    _name = 'sale.forecast.line'
    _order = 'forecast_id,product_id,qty,partner_id'

    @api.one
    @api.depends('unit_price', 'qty')
    def _get_subtotal(self):
        self.subtotal = self.unit_price * self.qty

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.unit_price = self.product_id.list_price

    product_id = fields.Many2one('product.product', string='Product')
    product_category_id = fields.Many2one('product.category',
                                          string='Product Category')
    qty = fields.Float('Quantity', default=1,
                       digits=dp.get_precision('Product Unit of Measure'))
    unit_price = fields.Float('Unit Price',
                              digits=dp.get_precision('Product Price'))
    subtotal = fields.Float('Subtotal', compute=_get_subtotal, store=True,
                            digits=dp.get_precision('Product Price'))
    partner_id = fields.Many2one("res.partner", string="Partner")
    commercial_id = fields.Many2one(comodel_name="res.users",
                                    related="partner_id.user_id",
                                    string="Commercial")
    currency_id = fields.Many2one(
        comodel_name="res.currency", string="Currency",
        related="partner_id.property_product_pricelist.currency_id")
    date_from = fields.Date(string="Date from", store=True,
                            related="forecast_id.date_from")
    date_to = fields.Date(string="Date to", related="forecast_id.date_to",
                          store=True)
    forecast_id = fields.Many2one('sale.forecast',
                                  string='Forecast',
                                  ondelete='cascade')
    date = fields.Date("Date")

    actual_qty = fields.Float(
        string='Actual Qty',
        compute='_compute_actual_qty',
        store=True)

    @api.depends('forecast_id.forecast_lines')
    def _compute_actual_qty(self):
        sale_obj = self.env['sale.order.line']
        prod_obj = self.env['product.product']
        for record in self:
            if record.product_id:
                if record.partner_id:
                    sale_ids = sale_obj.search([
                        ('product_id', '=', record.product_id.id),
                        ('order_id.partner_id', '=', record.partner_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                else:
                    sale_ids = sale_obj.search([
                        ('product_id', '=', record.product_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))

            elif record.product_category_id:
                product_ids = prod_obj.search([
                    ('categ_id', '=', record.product_category_id.id)])
                if record.partner_id:
                    sale_ids = sale_obj.search([
                        ('product_id', 'in', product_ids.ids),
                        ('order_id.partner_id', '=', record.partner_id.id),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                else:
                    sale_ids = sale_obj.search([
                        ('product_id', 'in', product_ids.ids),
                        ('invoice_status', '=', 'invoiced'),
                        ('order_id.confirmation_date', '>=', record.date_from),
                        ('order_id.confirmation_date', '<=', record.date_to)])
                record.actual_qty = sum(sale_ids.mapped('product_uom_qty'))