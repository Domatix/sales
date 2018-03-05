# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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

from odoo import models, _, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    imported = fields.Boolean(
        string='Imported')

    channel = fields.Char(
        string='Channel')

    sale_number = fields.Char(
        string='Nº Sale')

    sale_number_platform = fields.Char(
        string='Nº Sale Platform')

    @api.multi
    def unlink(self):
        for record in self:
            if record.state != 'draft' and record.imported:
                record.action_cancel()
        return super(SaleOrder, self).unlink()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fecha_pago = fields.Date(
        string='Payment Date')

    identificador_paypal = fields.Char(
        string='PayPal Identifier')

    imported = fields.Boolean(
        string='Imported')

    ref_uniq = fields.Char(
        string='Reference')

    shipping_cost_imported = fields.Float(
        string='Shipping cost')

    sale_number = fields.Char(
        string='Nº Sale')

    sale_number_platform = fields.Char(
        string='Nº Sale Platform')


    _sql_constraints = [(
        'ref_sale_line_uniq',
        'unique(ref_uniq)',
        'A sale order line with the same reference cannot be created'
        )]
