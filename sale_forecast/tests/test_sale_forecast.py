from datetime import date
from dateutil.relativedelta import relativedelta

from odoo.tests import common


class TestSaleForecastFlow(common.TransactionCase):

    def setUp(self):
        super(TestSaleForecastFlow, self).setUp()
        # Useful models

        self.so_model = self.env['sale.order']
        self.sf_model = self.env['sale.forecast']
        self.po_line_model = self.env['sale.order.line']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.product_uom_model = self.env['product.uom']
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.pricelist_model = self.env['product.pricelist']
        self.partner = self.env.ref('base.res_partner_1')
        self.partner_agrolite = self.env.ref('base.res_partner_2')
        self.productsf = self.env['product.product'].create({
            'name': 'Product Sale Forecast',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
        })

    def test_sale_forecast_load_sales(self):
        """ Test sale forecast flow."""
        uom_id = self.product_uom_model.search([('name', '=', 'Unit(s)')])[0]
        pricelist = self.pricelist_model.search([
            ('name', '=', 'Public Pricelist')])[0]

        # so_vals = {
        #     'partner_id': self.partner_agrolite.id,
        #     'pricelist_id': pricelist.id,
        #     'order_line': [
        #         (0, 0, {
        #             'name': self.productsf.name,
        #             'product_id': self.productsf.id,
        #             'product_uom_qty': 1.0,
        #             'product_uom': uom_id.id,
        #             'price_unit': 121.0
        #         })
        #     ]
        # }
        so_vals2 = {
            'partner_id': self.partner.id,
            'pricelist_id': pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsf.name,
                    'product_id': self.productsf.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 121.0
                })
            ]
        }

        # self.so_model.create(so_vals)
        confirmed_so = self.so_model.create(so_vals2)
        confirmed_so.action_confirm()

        sf_vals = {
            'name': 'Test 1',
            'date_from': date.today() + relativedelta(years=1),
            'date_to': date.today() + relativedelta(years=2),

        }
        sf = self.sf_model.create(sf_vals)
        context = {
            "active_model": 'sale.forecast',
            "active_ids": [sf.id],
            "active_id": sf.id
            }

        load_sales_wizard = self.env['sale.forecast.load'].with_context(
            context).create(
            {
                'factor': 3,
                'forecast_id': sf.id,
            })
        load_sales_wizard.load_sales()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('qty')),
            3,
            'Sales are not loaded proper.')

    def test_sale_forecast_load_sale_forecast(self):
        """ Test sale forecast flow."""

        sf_vals = {
            'name': 'Test 2',
            'date_from': date.today() + relativedelta(years=1),
            'date_to': date.today() + relativedelta(years=2),
            'forecast_lines': [
                (0, 0, {
                    'product_id': self.productsf.id,
                    'qty': 1,
                })
            ]
        }
        sf = self.sf_model.create(sf_vals)

        empty_sf_vals = {
            'name': 'Test 3',
            'date_from': date.today() + relativedelta(years=1),
            'date_to': date.today() + relativedelta(years=2),
        }
        empty_sf = self.sf_model.create(empty_sf_vals)
        context = {
            "active_model": 'sale.forecast',
            "active_ids": [empty_sf.id],
            "active_id": empty_sf.id
            }

        load_sale_forecast_wizard_dict = \
            self.env['self.sale.forecast.load'].with_context(context).create(
                {
                    'forecast_id': empty_sf.id,
                    'forecast_sales': sf.id
                })
        load_sale_forecast_wizard_dict.button_confirm()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('qty')),
            1,
            'Sales forecasts are not loaded proper.')

    def test_sale_forecast_recalculate_actual_qty(self):
        """ Test sale forecast flow."""
        uom_id = self.product_uom_model.search([('name', '=', 'Unit(s)')])[0]
        pricelist = self.pricelist_model.search([
            ('name', '=', 'Public Pricelist')])[0]

        so_vals = {
            'partner_id': self.partner_agrolite.id,
            'pricelist_id': pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsf.name,
                    'product_id': self.productsf.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 121.0
                })
            ]
        }
        so_vals2 = {
            'partner_id': self.partner.id,
            'pricelist_id': pricelist.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsf.name,
                    'product_id': self.productsf.id,
                    'product_uom_qty': 1.0,
                    'product_uom': uom_id.id,
                    'price_unit': 121.0
                })
            ]
        }

        sf_vals = {
            'name': 'Test 3',
            'date_from': date.today() + relativedelta(months=-1),
            'date_to': date.today() + relativedelta(months=1),
            'forecast_lines': [
                (0, 0, {
                    'product_id': self.productsf.id,
                    'qty': 1,
                })
            ]
        }
        sf = self.sf_model.create(sf_vals)

        self.so_model.create(so_vals)
        invoiced_so = self.so_model.create(so_vals2)
        invoiced_so.action_confirm()
        invoiced_so.action_invoice_create()
        sf.recalculate_actual_qty()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('actual_qty')),
            1,
            'Actual quantities are not computed proper.')
