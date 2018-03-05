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

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError
from odoo.exceptions import Warning
import logging
import mimetypes
from lxml import etree
import base64
import xlrd
import tempfile
import datetime

logger = logging.getLogger(__name__)


class SaleOrderImport(models.TransientModel):
    _name = 'sale.import.wizard'
    _description = 'Import sale orders'

    order_file = fields.Binary(
        string='Order file', required=True,
        help="Upload sale order from xls.")
    order_filename = fields.Char(string='Filename')


    @api.model
    def _read_xls(self, datafile):
        try:
            wb = xlrd.open_workbook(datafile)
            sh = wb.sheet_by_index(0)
            header = sh.row_values(0)
            lines = []
        except Exception:
            return False

        if sh.nrows == 0:
            return False

        for rownum in range(1, sh.nrows):
            i = 0
            data = {}
            for col in sh.row_values(rownum):
                data[header[i]] = col
                i += 1
            lines.append(data)
        return lines

    def check_skus(self,lines):
        sku_error = False
        cont_lines = 1
        product_obj = self.env['product.product']
        for line in lines:
            cont_lines = cont_lines + 1
            sku = line['SKU']
            if not sku:
                continue
            if type(line['SKU']) == float:
                sku = str(int(sku))
            product_id = product_obj.search([('sku_ids','=',sku)])
            if not product_id:
                if not sku_error:
                    sku_error = str(cont_lines) + ' - ' + sku + "\n"
                else:
                    sku_error +=str(cont_lines) + ' - ' + sku + "\n"
        return sku_error

    def check_channel(self,lines):
        channel_error = False
        cont_lines = 1
        channel_type_obj = self.env['channel.type']
        for line in lines:
            cont_lines = cont_lines + 1
            channel = line['CANAL']
            if not channel:
                continue
            channel_id = channel_type_obj.search([('name','=',channel)])
            if not channel_id:
                if not channel_error:
                    channel_error = str(cont_lines) + ' - ' + channel + "\n"
                else:
                    channel_error += str(cont_lines) + ' - ' + channel + "\n"
        return channel_error

    def check_sale_number_platform(self,lines):
        platform_error = False
        cont_lines = 1
        for line in lines:
            cont_lines = cont_lines + 1
            if not line['N VENTA']:
                continue
            if not line['N VENTA PLAT.']:
                platform_error = str(cont_lines)
                return platform_error

    @api.multi
    def import_button(self):
        f = tempfile.NamedTemporaryFile()
        f.write(base64.decodestring(self.order_file))
        f.flush()

        lines = self._read_xls(f.name)
        f.close()
        sku_error = self.check_skus(lines)
        if sku_error:
            raise UserError(
                _("Sku/s not created, Excel Lines - Sku\n '%s'")
                % (sku_error))

        channel_error = self.check_channel(lines)
        if channel_error:
            raise UserError(
                _("Channel not found\n '%s'")
                % (channel_error))

        platform_error = self.check_sale_number_platform(lines)
        if platform_error:
            raise UserError(
                _("Nº sale number platform cannot be empty '%s'")
                % (platform_error))
        cont_partner = 0
        cont_product = 0
        cont_order = 0
        cont_order_lines = 0
        cont_excel_lines = 1
        partner_obj = self.env['res.partner']
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        product_obj = self.env['product.product']
        state_obj = self.env['res.country.state']
        country_obj = self.env['res.country']
        payment_mode_obj = self.env['account.payment.mode']
        payment_term_obj = self.env['account.payment.term']
        import_obj = self.env['import.order']
        tax21 = self.env['account.tax'].search([('name','=','IVA 21% (Bienes)')])[0]
        tax0 = self.env['account.tax'].search([('name','=','IVA 0% Exportaciones')])[0]
        import_id = import_obj.create({})
        # Recorrer excel

        for line in lines:
            cont_excel_lines = cont_excel_lines + 1
            same_address = False
            #Comprobar si se han acabado las lineas
            if not line['N VENTA']:
                continue

            #comprobaciones de tipo
            if type(line['N VENTA']) == float:
                nventa = str(int(line['N VENTA']))
            else:
                nventa = line['N VENTA']

            if type(line['N VENTA PLAT.']) == float:
                nventaplat = str(int(line['N VENTA PLAT.']))
            else:
                nventaplat = line['N VENTA PLAT.']

            if type(line['N SEGUIMIENTO']) == float:
                nseguimiento = str(int(line['N SEGUIMIENTO']))
            else:
                nseguimiento = line['N SEGUIMIENTO']

            #Comprobar si existe el pedido, si no, lo crea
            sale_line_id = sale_line_obj.search([('sale_number','=',nventa),('sale_number_platform','=',nventaplat)])
            if sale_line_id:
                if sale_line_id[0].state != 'draft':
                    continue

            # Comprobar si existe el cliente
            if type(line['USER']) == float:
                user = str(int(line['USER']))
            else:
                user = line['USER']
            if user:
                partner_id = partner_obj.search([('user_channel','=',user),('type','=','invoice')])
            else:
                partner_id = False
            if not partner_id:
                if line['E-MAIL FACT.']:
                    partner_id = partner_obj.search([('email','=',line['E-MAIL FACT.']),('type','=','invoice')])

            if not partner_id:
                if line['TELEFONO FACT.']:
                    partner_id = partner_obj.search([('phone','=',str(int(line['TELEFONO FACT.']))),('type','=','invoice')])

            if not partner_id:
                country_id = country_obj.search([('name','=',line['PAIS FACT.'])])
                if not country_id:
                    country_id = country_obj.search([('name','like',line['PAIS FACT.'])])
                    if country_id:
                        country_id = country_id[0]
                state_id = state_obj.search([('name','=',line['ESTADO FACT.']),('country_id','=',country_id.id)])
                zip_partner = line['CODIGO POSTAL FACT.']
                if type(zip_partner) == float:
                    zip_partner = str(int(zip_partner))
                partner = {
                        'user_channel': user if user else False,
                        'name':line['NOMBRE FACT.'],
                        'phone': str(int(line['TELEFONO FACT.'])) if line['TELEFONO FACT.'] else False,
                        'email': line['E-MAIL FACT.'],
                        'street': line['DIRECCION FACT.'],
                        'city': line['POBLACION FACT.'],
                        'estado': line['ESTADO FACT.'],
                        'state_id': state_id.id if state_id else False,
                        'zip': zip_partner if line['CODIGO POSTAL FACT.'] else False,
                        'country_id': country_id.id if country_id else False,
                        'customer': True,
                        'supplier': False,
                        'opt_out': True,
                        'imported': True,
                        'type': 'invoice',
                }
                partner_id = partner_obj.create(partner)
                cont_partner = cont_partner + 1
                #Escribimos los datos importados del cliente
                import_vals = {
                                'import_client': [(0,0,{'line_client': str(cont_excel_lines),
                                                        'partner_id': partner_id.id,
                                                        'user_channel': partner_id.user_channel})]
                }
                import_id.write(import_vals)

            partner_delivery_id = partner_id
            #Comprobacion de direccion de ENVIO
            if line['DIRECCION FACT.'] == line['DIRECCION'] and line['POBLACION FACT.'] == line['POBLACION'] and \
            line['ESTADO FACT.'] == line['ESTADO'] and line['CODIGO POSTAL FACT.'] == line['CODIGO POSTAL'] and line['PAIS FACT.'] == line['PAIS']:
                same_address = True

            if not same_address:
                zip_partner = line['CODIGO POSTAL']
                if type(zip_partner) == float:
                    zip_partner = str(int(zip_partner))
                country_id = country_obj.search([('name','like',line['PAIS'])])
                state_id = state_obj.search([('name','=',line['ESTADO']),('country_id','=',country_id.id)])
                partner_delivery_id = partner_obj.search([('type','=','delivery'),('street','=',line['DIRECCION']),('zip','=',zip_partner),('country_id','=',country_id.id)])
                if not partner_delivery_id:
                    partner_devlivery_vals = {
                            'opt_out':True,
                            'is_company':False,
                            'customer' : False,
                            'name': line['NOMBRE'],
                            'street' : line['DIRECCION'],
                            'city' : line['POBLACION'],
                            'country_id' : country_id.id if country_id else False,
                            'phone' : str(int(line['TELEFONO 1'])) if line['TELEFONO 1'] else False,
                            'mobile': str(int(line['TELEFONO 2'])) if line['TELEFONO 2'] else False,
                            'zip' : zip_partner if line['CODIGO POSTAL'] else False,
                            'state_id' : state_id.id if state_id else False,
                            'email': line['E-MAIL'],
                            'parent_id': partner_id.id,
                            'type': 'delivery',
                            'imported': True,

                        }
                    partner_delivery_id = partner_obj.create(partner_devlivery_vals)
            #producto del sku
            sku = line['SKU']
            if type(line['SKU']) == float:
                sku = str(int(sku))

            product_id = product_obj.search([('sku_ids','=',sku)])

            # comprobamos que la cabecera del padre está ya creada

            sale_id = sale_obj.search([('sale_number_platform','=',nventaplat),('channel','=',line['CANAL'])])

            if not sale_id:
                payment_mode_id = payment_mode_obj.search([('name','=',line['METODO PAGO'])])
                payment_term_id = payment_term_obj.search([('name','like','Pago inmediato')])
                if type(line['FECHA VENTA']) == float:
                    start_date = "30/12/1899 00:00:00"
                    timedelta = datetime.timedelta(days=line['FECHA VENTA'])
                    date_1 = datetime.datetime.strptime(start_date,"%d/%m/%Y %H:%M:%S")
                    end_date = date_1 + timedelta
                    date = end_date.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date = datetime.datetime.strptime(line['FECHA VENTA'],'%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S')
                partner_id = partner_id[0]
                partner_delivery_id = partner_delivery_id[0]
                sale_vals = {
                        'partner_id': partner_id.id,
                        'partner_shipping_id': partner_delivery_id.id,
                        'date_order': date,
                        'channel': line['CANAL'],
                        'origin': nventa,
                        'sale_number': nventa,
                        'sale_number_platform': nventaplat,
                        'client_order_ref': nventaplat,
                        'payment_term_id': payment_term_id.id if payment_mode_id and payment_term_id else False,
                        'payment_mode_id': payment_mode_id.id if payment_mode_id else False,
                        'imported': True

                }
                sale_id = sale_obj.create(sale_vals)
                cont_order = cont_order + 1

            else:
                if sale_id.sale_number:
                    if nventa not in sale_id.sale_number:
                        sale_id.sale_number +=', '+nventa

            sale_line_vals ={
                    'order_id': sale_id.id,
                    'product_id':product_id.id,
                    'tracking_number': nseguimiento,
                    'name':line['DESCRIPCION'],
                    'product_uom_qty':line['CANTIDAD'],
                    'price_unit':line['PRECIO'],
                    'sale_number': nventa,
                    'sale_number_platform': nventaplat,
                    'tax_id': [(4,tax0.id)] if not line['IVA'] else [(4,tax21.id)],
                    'imported': True,

                }
            sale_order_line = sale_line_obj.create(sale_line_vals)

            cont_order_lines = cont_order_lines + 1
            # Escribimos los datos importados de la linea del pedido
            import_vals = {
                            'import_order': [(0,0,{'line_order': str(cont_excel_lines),
                                                    'order_id': sale_order_line.order_id.id,
                                                    'channel':sale_order_line.order_id.channel,
                                                    'sale_number':sale_order_line.order_id.sale_number,
                                                    'sale_number_platform':sale_order_line.order_id.sale_number_platform
                                                    })]
            }
            import_id.write(import_vals)
            if line['ENVIO']:
                ship_product = product_obj.search([('default_code','=','SHIPPING')])
                if not ship_product:
                    ship_product_vals = {
                                    'name': 'Costes envío',
                                    'type':'service',
                                    'default_code': 'SHIPPPING',

                    }
                    ship_product = product_obj.create(ship_product_vals)
                sale_line_vals ={
                        'order_id': sale_id.id,
                        'product_id':ship_product.id,
                        'tracking_number': nseguimiento,
                        'price_unit':line['ENVIO'],
                        'tax_id': [(4,tax0.id)] if not line['IVA'] else [(4,tax21.id)],
                        'imported': True,

                }
                sale_order_line = sale_line_obj.create(sale_line_vals)


        import_vals = {
                'client_count': str(cont_partner),
                'order_count': str(cont_order),
                'order_line_count': str(cont_order_lines),

        }

        import_id.write(import_vals)
        sale_unconfirmed = sale_obj.search([('imported','=',True),('state','=','draft')])
        for sale in sale_unconfirmed:
            sale.action_confirm()
        if not cont_partner and not cont_order and not cont_order_lines:
             raise Warning(_("No new data to import"))

        return {
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'import.order',
        'target': 'current',
        'res_id': import_id.id,
        'type': 'ir.actions.act_window'
    }
