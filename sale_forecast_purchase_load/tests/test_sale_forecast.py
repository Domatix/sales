from datetime import date, datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta

from odoo.tests import common


class TestSaleForecastPurchaseLoadFlow(common.TransactionCase):

    def setUp(self):
        super(TestSaleForecastPurchaseLoadFlow, self).setUp()
        # Useful models

        self.po_model = self.env['purchase.order']
        self.sf_model = self.env['sale.forecast']
        self.po_line_model = self.env['sale.order.line']
        self.res_partner_model = self.env['res.partner']
        self.product_tmpl_model = self.env['product.template']
        self.product_model = self.env['product.product']
        self.categ_model = self.env['product.category']
        self.product_uom_model = self.env['product.uom']
        self.supplierinfo_model = self.env["product.supplierinfo"]
        self.partner_id = self.env.ref('base.res_partner_1')
        self.partner_agrolite = self.env.ref('base.res_partner_2')
        self.categ_id = self.categ_model.create({
            'name': 'Sale Forecast Purchase Load'
        })
        self.productsflp = self.env['product.product'].create({
            'name': 'Product SF LP',
            'type': 'product',
            'categ_id': self.categ_id.id,
        })
        self.productsflp2 = self.env['product.product'].create({
            'name': 'Product SF LP2',
            'type': 'product',
            'categ_id': self.categ_id.id,
        })

    def test_sale_forecast_load_purchases(self):
        """ Test sale forecast flow."""

        po_vals = {
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsflp.name,
                    'product_id': self.productsflp.id,
                    'product_qty': 1.0,
                    'product_uom': self.productsflp.uom_po_id.id,
                    'price_unit': 121.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ]
        }
        po_vals2 = {
            'partner_id': self.partner_agrolite.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsflp.name,
                    'product_id': self.productsflp.id,
                    'product_qty': 1.0,
                    'product_uom': self.productsflp.uom_po_id.id,
                    'price_unit': 121.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ]
        }
        po_vals3 = {
            'partner_id': self.partner_agrolite.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsflp.name,
                    'product_id': self.productsflp.id,
                    'product_qty': 2.0,
                    'product_uom': self.productsflp.uom_po_id.id,
                    'price_unit': 121.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ]
        }
        po_vals4 = {
            'partner_id': self.partner_agrolite.id,
            'order_line': [
                (0, 0, {
                    'name': self.productsflp2.name,
                    'product_id': self.productsflp2.id,
                    'product_qty': 2.0,
                    'product_uom': self.productsflp.uom_po_id.id,
                    'price_unit': 121.0,
                    'date_planned': datetime.today().strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ]
        }

        self.po_model.create(po_vals)
        confirmed_po = self.po_model.create(po_vals2)
        confirmed_po.button_confirm()
        confirmed_po2 = self.po_model.create(po_vals3)
        confirmed_po2.button_confirm()
        confirmed_po3 = self.po_model.create(po_vals4)
        confirmed_po3.button_confirm()
        sf_vals = {
            'name': 'Test LP 1',
            'date_from': date.today() + relativedelta(years=1),
            'date_to': date.today() + relativedelta(years=2),

        }
        sf = self.sf_model.create(sf_vals)
        context = {
            "active_model": 'sale.forecast',
            "active_ids": [sf.id],
            "active_id": sf.id
            }

        load_purchases_wizard = \
            self.env['purchase.forecast.load'].with_context(
                context).create(
                {
                    'factor': 3,
                    'product_id': self.productsflp.id
                })
        load_purchases_wizard.load_purchases()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('qty')),
            9,
            'Purchases are not loaded proper.')

        load_purchases_wizard = \
            self.env['purchase.forecast.load'].with_context(
                context).create(
                {
                    'factor': 3,
                    'product_id': self.productsflp.id,
                    'partner_id': self.partner_agrolite.id
                })
        load_purchases_wizard.load_purchases()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('qty')),
            18,
            'Purchases are not loaded proper.')
        self.assertEqual(
            len(sf.forecast_lines),
            1,
            'Lines are not grouped proper.')

        load_purchases_wizard = \
            self.env['purchase.forecast.load'].with_context(
                context).create(
                {
                    'factor': 3,
                    'product_categ_id': self.categ_id.id,
                })
        load_purchases_wizard.load_purchases()
        self.assertEqual(
            sum(sf.forecast_lines.mapped('qty')),
            33,
            'Purchases by category are not loaded proper.')
