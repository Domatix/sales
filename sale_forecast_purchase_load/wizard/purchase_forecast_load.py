# -*- encoding: utf-8 -*-
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api


class PurchaseForecastLoad(models.TransientModel):

    _name = 'purchase.forecast.load'

    def _get_default_partner(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        partner = False
        if model == 'purchase.order':
            partner = record.partner_id
        return partner

    def _get_default_forecast(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        forecast = False
        if model == 'sale.forecast':
            forecast = record.id
        return forecast

    def _get_default_purchase(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        purchase = False
        if model == 'purchase.order':
            purchase = record.id
        return purchase

    def _get_default_date_from(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_from = False
        if model == 'purchase.order':
            date_from = record.date_order
        elif model == 'sale.forecast':
            date_from = record.date_from
        return date_from

    def _get_default_date_to(self):
        model = self.env.context.get('active_model', False)
        record = self.env[model].browse(self.env.context.get('active_id'))
        date_to = False
        if model == 'purchase.order':
            date_to = record.date_order
        elif model == 'sale.forecast':
            date_to = record.date_to
        return date_to

    partner_id = fields.Many2one("res.partner", string="Partner",
                                 default=_get_default_partner)
    date_from = fields.Date(string="Date from", default=_get_default_date_from)
    date_to = fields.Date(string="Date to", default=_get_default_date_to)
    purchase_id = fields.Many2one("purchase.order", "Purchase",
                                  default=_get_default_purchase)
    forecast_id = fields.Many2one("sale.forecast", "Forecast",
                                  default=_get_default_forecast)
    product_categ_id = fields.Many2one("product.category", string="Category")
    product_tmpl_id = fields.Many2one("product.template", string="Template")
    product_id = fields.Many2one("product.product", string="Product")
    factor = fields.Float(string="Factor", default=1)

    @api.onchange('purchase_id')
    def purchase_onchange(self):
        if self.purchase_id:
            self.partner_id = self.purchase_id.partner_id.id
            self.date_from = self.purchase_id.date_order
            self.date_to = self.purchase_id.date_order

    @api.onchange('forecast_id')
    def forecast_onchange(self):
        if self.forecast_id:
            self.date_from = self.forecast_id.date_from
            self.date_to = self.forecast_id.date_to

    @api.multi
    def match_purchases_forecast(self, purchases, factor):
        self.ensure_one()
        res = {}
        for purchase in purchases:
            partner = self.partner_id.id
            product = purchase.product_id.id
            if partner not in res:
                res[partner] = {}
            if product not in res[partner]:
                res[partner][product] = {'qty': 0.0, 'amount': 0.0}
            product_dict = res[partner][product]
            sum_qty = product_dict['qty'] + purchase.product_qty
            sum_subtotal = (product_dict['amount'] +
                            purchase.price_subtotal)
            product_dict['qty'] = sum_qty * factor
            product_dict['amount'] = sum_subtotal
        return res

    @api.multi
    def get_purchase_forecast_lists(self, forecast):
        purchase_line_obj = self.env['purchase.order.line']
        purchase_obj = self.env['purchase.order']
        product_obj = self.env['product.product']
        self.ensure_one()
        purchases = []
        if self.purchase_id:
            purchases = self.purchase_id
        else:
            purchase_domain = [('date_order', '>=', self.date_from),
                               ('date_order', '<=', self.date_to)]
            if self.partner_id:
                purchase_domain += [('partner_id', '=', self.partner_id.id)]
            purchases = purchase_obj.search(purchase_domain)
        purchase_line_domain = [('order_id', 'in', purchases.ids)]
        if self.product_id:
            purchase_line_domain += [('product_id', '=', self.product_id.id)]
        elif self.product_tmpl_id:
            purchase_line_domain += [('product_tmpl_id', '=',
                                      self.product_tmpl_id.id)]
        elif self.product_categ_id:
            products = product_obj.search([('categ_id', '=',
                                            self.product_categ_id.id)])
            purchase_line_domain += [('product_id', 'in', products.ids)]
        purchase_lines = purchase_line_obj.search(purchase_line_domain)
        return purchase_lines

    @api.multi
    def load_purchases(self):
        self.ensure_one()
        forecast_line_obj = self.env['sale.forecast.line']
        forecast = self.forecast_id
        purchase_lines = self.get_purchase_forecast_lists(forecast)
        result = self.match_purchases_forecast(purchase_lines, self.factor)
        for partner in result.keys():
            for product in result[partner].keys():
                prod_vals = result[partner][product]
                line = forecast_line_obj.search(
                    [
                        ('forecast_id', '=', self.forecast_id.id),
                        ('partner_id', '=', partner),
                        ('product_id', '=', product)
                     ])
                unit_price = prod_vals['amount'] / prod_vals['qty']
                if line:
                    line.unit_price = (line.unit_price * line.qty + unit_price
                                       * prod_vals['qty']) / (line.qty +
                                                              prod_vals['qty'])

                    line.qty += prod_vals['qty']
                else:
                    forecast_line_vals = {'product_id': product,
                                          'forecast_id': self.forecast_id.id,
                                          'partner_id': partner,
                                          'qty': prod_vals['qty'],
                                          'unit_price': unit_price
                                          }
                    forecast_line_obj.create(forecast_line_vals)
        return True
