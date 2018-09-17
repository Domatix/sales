from .common import TestWebsiteQuotationProductSubstituteCommon

IMPORT = 'odoo.addons.website_quotation_product_substitute.controllers.main'


class TestControllers(TestWebsiteQuotationProductSubstituteCommon):
    def setUp(self):
        super(TestControllers, self).setUp()

        # Test SO
        self.SaleOrder = self.env['sale.order']
        self.pricelist_model = self.env['product.pricelist']
        self.pricelist = self.pricelist_model.search([
            ('name', '=', 'Public Pricelist')])[0]
        self.product1 = self.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'lst_price': 1,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product2 = self.env['product.product'].create({
            'name': 'Product B',
            'type': 'product',
            'lst_price': 2,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.product3 = self.env['product.product'].create({
            'name': 'Product C',
            'type': 'product',
            'lst_price': 3,
            'categ_id': self.env.ref('product.product_category_all').id,
        })
        self.partner = self.env.ref('base.res_partner_1')

    def _check_route(self, url):
        resp = self.url_open(url, timeout=30)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.status_code, 200)

    # def test_default_routes(self):
    #     import pdb; pdb.set_trace()
    #     line_id = self.so.product_substitute_ids[0].id
    #     so_id = self.so.id
    #     token = self.so.access_token
    #     self._check_route(
    #         '/quote/substitute_line/%s/%s/%s' % (line_id, so_id, token))
    #     self.assertEqual(
    #         self.so.order_line[0].product_id.id,
    #         self.product2.id,
    #         'Products are not changed proper.')
