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


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pack = fields.Boolean(
        string='Pack')

    pack_line_ids = fields.One2many(
        comodel_name='product.pack.line',
        inverse_name='parent_product_id',
        string='Product Packs',
        help='Product list from this pack')

    packs_product_ids = fields.One2many(
        comodel_name='product.pack.line',
        inverse_name='product_id',
        string='Productos en Packs',
        help='Pack list from these products.')



class ProductPack(models.Model):
    _name = 'product.pack.line'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Parent Product',
        ondelete='cascade',
        required=False)

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Products',
        required=True)

    quantity = fields.Float(
        string='Quantity',
        default=1.0,
        required=True)
