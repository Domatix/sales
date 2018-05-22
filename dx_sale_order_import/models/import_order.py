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

from odoo import models, _,fields
from datetime import datetime

class ImportOrder(models.Model):
    _name = 'import.order'
    _order = 'date desc'

    def _getname(self):
        return "Pedidos - " + datetime.now().strftime('%d-%m-%Y')

    name = fields.Char(
        string='Nombre',
        default=_getname)

    def _getdatetime(self):
        return datetime.now()

    date = fields.Datetime(
        string='Import date',
        default=_getdatetime)

    product_count = fields.Char(
        string='Import Products')

    client_count = fields.Char(
        string='Import Clients')

    order_count = fields.Char(
        string='Import Orders')

    order_line_count = fields.Char(
        string='Import Order Line')

    import_order = fields.One2many(
        comodel_name='import.order.line',
        inverse_name='import_order_line',
        string='Import Orders')

    import_lines = fields.One2many(
        comodel_name='import.order.line',
        inverse_name='import_lines_order',
        string='Import Order Lines')


    import_client = fields.One2many(
        comodel_name='import.order.line',
        inverse_name='import_client_line',
        string='Import Clients')


    import_product = fields.One2many(
        comodel_name='import.order.line',
        inverse_name='import_product_line',
        string='Import Products')


class ImportOrder(models.Model):
    _name = 'import.order.line'

    import_order_line = fields.Many2one(
        comodel_name='import.order',
        string='Import Order')

    import_lines_order = fields.Many2one(
        comodel_name='import.order',
        string='Import Order Lines')


    import_client_line = fields.Many2one(
        comodel_name='import.order',
        string='Import Client')

    import_product_line = fields.Many2one(
        comodel_name='import.order',
        string='Import Product')

    line_product = fields.Char(
        string='Line')

    line_client = fields.Char(
        string='Line')

    line_order = fields.Char(
        string='Line')

    line_order_line = fields.Char(
        string='Line')


    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product')

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order')

    sale_number = fields.Char(
        string='Sale Number')

    sale_number_platform = fields.Char(
        string='Sale Number Platform')

    user_channel = fields.Char(
        string='User Channel')

    channel = fields.Char(
        string='Channel')


    order_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Sale Order Lines')
