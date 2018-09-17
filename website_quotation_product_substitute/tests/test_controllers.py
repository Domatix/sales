from contextlib import contextmanager
from odoo.tests import common
import mock
from .utils import fake_request
IMPORT = 'odoo.addons.website_quotation_product_substitute.controllers.main'


class TestWebsiteQuotationProductSubstituteCommon(common.HttpCase):

    def setUp(self):
        super(TestWebsiteQuotationProductSubstituteCommon, self).setUp()

        TestUsersEnv = self.env['res.users'].with_context({'no_reset_password': True})
        group_employee_id = self.env.ref('base.group_user').id
        group_portal_id = self.env.ref('base.group_portal').id
        group_public_id = self.env.ref('base.group_public').id
        self.user_employee = TestUsersEnv.create({
            'name': 'Armande Employee',
            'login': 'Armande',
            'email': 'armande.employee@example.com',
            'groups_id': [(6, 0, [group_employee_id])]
        })
        self.user_portal = TestUsersEnv.create({
            'name': 'Beatrice Portal',
            'login': 'Beatrice',
            'email': 'beatrice.employee@example.com',
            'groups_id': [(6, 0, [group_portal_id])]
        })
        self.user_public = TestUsersEnv.create({
            'name': 'Cedric Public',
            'login': 'Cedric',
            'email': 'cedric.employee@example.com',
            'groups_id': [(6, 0, [group_public_id])]
        })

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

    @contextmanager
    def mock_assets(self):
        """Mocks some stuff like request."""
        with mock.patch('%s.request' % IMPORT) as request:
            faked = fake_request()
            request.session = self.session
            request.env = self.env
            request.httprequest = faked.httprequest
            yield {
                'request': request,
            }

    def _check_route(self, url):
        resp = self.url_open(url, timeout=30)
        self.assertTrue(resp.ok)
        self.assertEqual(resp.status_code, 200)

    def test_default_routes(self):
        with self.mock_assets():
            so = self.SaleOrder.create({
                'partner_id': self.partner.id,
                'pricelist_id': self.pricelist.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product1.name,
                        'product_id': self.product1.id,
                        'product_uom_qty': 1.0,
                        'product_uom': self.product1.uom_id.id,
                        'price_unit': 121.0
                    })
                ],
            })
            so.write({
                'product_substitute_ids': [
                    (0, 0, {
                        'sale_order_line_id': so.order_line[0].id,
                        'product_substitute_id': self.product2.id,
                    })
                ]
            })
            so.write({
                'product_substitute_ids': [
                    (0, 0, {
                        'sale_order_line_id': so.order_line[0].id,
                        'product_substitute_id': self.product3.id,
                    })
                ]
            })
            line_id = so.product_substitute_ids[0].id
            so_id = so.id
            token = so.access_token
            self._check_route(
                '/quote/substitute_line/%s/%s/%s' % (line_id, so_id, token))
            self.assertEqual(
                so.order_line[0].product_id.id,
                self.product3.id,
                'Products are not changed proper.')
