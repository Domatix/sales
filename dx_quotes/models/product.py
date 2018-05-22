from odoo import fields, models

class DisberProduct(models.Model):
    _inherit = 'product.product'
    is_pack = fields.Boolean(string="Pack", default=False)
    pack_list = fields.Many2many(
        comodel_name ='product.product',
        relation = 'pack_list',
        column1 = 'pack_name',
        column2 = 'product_list',
        string = 'Product List'
        )

class DisberCategory(models.Model):
    _inherit = 'product.category'
    order = fields.Integer(string="Order",translate ="True")
    price_breakdown = fields.One2many(
        comodel_name='sale.quote.tax',
        inverse_name='quote_id',
        string='Price Breakdown')
