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

from odoo import models, _,fields, api


class product(models.Model):
    _inherit = 'product.product'

    # name = fields.Char('Name',required=True)

    ref_uniq = fields.Char(
        string='Unique Reference')

    sku_ids = fields.One2many(
        comodel_name='product.sku',
        inverse_name='product_id',
        string='SKU List')


    _sql_constraints = [(
        'ref_prod_uniq',
        'unique(ref_uniq)',
        'A product with the same reference cannot be created'
        )]

class product(models.Model):
    _inherit = 'product.template'

    skus = fields.Char(
        string='Skus Template',
        compute='_compute_sku_codes',
        store=True)

    @api.depends('product_variant_ids.sku_ids')
    def _compute_sku_codes(self):
        for record in self:
            res = False
            if record.product_variant_ids:
                skus = record.product_variant_ids.mapped('sku_ids').mapped('name')
                if not skus:
                    continue
                for sku in skus:
                    if not res:

                        res = sku
                    else:

                        res += ' ' + sku

            record.skus = res


class ProductSku(models.Model):
    _name = 'product.sku'

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product')

    name = fields.Char(
        string='SKU')

    channel_platform = fields.Char(
        string='Plataform')

    _sql_constraints = [(
        'ref_sku_uniq',
        'unique(name)',
        'A SKU with an associated product cannot be created'
        )]
