
from odoo import fields, models, api, exceptions
from datetime import datetime, timedelta


class Quote(models.Model):
    _name = 'sale.quote'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Presupuestos Disber"

    @api.model
    def _default_note(self):
        return self.env['ir.config_parameter'].sudo().get_param('sale.use_sale_note') and self.env.user.company_id.sale_note or ''

    @api.depends('quote_line')
    def _get_cost_price(self):
        for record in self:
            for line in record.quote_line:
                if line.cost_price:
                    record.cost_price += line.cost_price * line.qty

    name = fields.Char(
        string='Quote name',
        required=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True)

    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('sent', 'Sent'),
         ('transfered', 'Transfered')],
        string='field_name',
        default='draft')

    origin = fields.Selection(
        [('modify', 'Modify'),
         ('same_as', 'Same as')],
        string='Origin')

    quote_taxes = fields.One2many(
        'sale.quote.tax',
        'quote_id',
        string='Tax Lines')
    quote_line = fields.One2many(
        comodel_name='sale.quote.line',
        inverse_name='quote_id',
        string='Lines')

    cost_price = fields.Float(
        string='Cost Price',
        compute=_get_cost_price)
    expiration = fields.Date(
        string="Expiration",
        default=fields.Datetime.from_string(fields.Datetime.now()) +
        timedelta(days=30))
    weight = fields.Float(
        string='Weight')
    quote_origin = fields.Many2one(
        comodel_name='sale.quote',
        string='Quote origin')
    amount_untaxed = fields.Float(
        string='Ammount Untaxed')
    amount_tax = fields.Float(
        string='Ammount tax')
    amount_total = fields.Float(
        string='Ammount total')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        default=1)
    margen_abs = fields.Float(
        string='Margen')
    margen_porcentaje = fields.Float(
        string='Margen porcentaje')
    total_bases = fields.Float(
        string='Total bases')
    descuento1 = fields.Float(
        string='Descuento 1')
    descuento2 = fields.Float(
        string='Descuento 2')
    metodo_valoracion = fields.Selection(
        [('porcentaje', 'Porcentaje'),
         ('margen', 'Margen'),
         ('ii', 'I.I'),
         ('bases', 'Total Bases'),
         ('mismo', 'Mismo Precio')],
        string='Metodo Valoración')
    porcentaje = fields.Float(
        string='Porcentaje')
    margen_valoracion = fields.Float(
        string='Margen Valoración')
    iva_incluido = fields.Float(
        string='I.V.A incluido')
    bases = fields.Float(
        string='Total Bases')
    mismo_precio = fields.Float(
        string='Mismo Precio')
    note = fields.Text('Terms and conditions', default=_default_note)

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The quote must be unique"),
    ]
    @api.model
    def _validate_expiration(self):
        if fields.Datetime.from_string(self.expiration).date() < datetime.now().date():
            return False
        return True

    @api.model
    def _validate_valoracion(self):
        if self.margen_abs == 0:
            return False
        return True


    def _generate_pack(self):
        if self.weightless() == False:
            raise exceptions.Warning('No se traspasa el presupuesto.Artículos sin peso.')
            return False

        producto = self.env['product.product'].create({'name':self.name,
                            'is_pack':True,'list_price':self.total_bases})

        bom = self.env['mrp.bom'].create({'product_tmpl_id':producto.product_tmpl_id.id,
                                          'product_id':producto.id,
                                          'name':producto.name + ' v.0',
                                          'product_qty':1,
                                          'type':'normal'})

        for line_quote in self.quote_line:
            producto.weight += line_quote.product_id.weight
            if line_quote.product_id.categ_id.name == "Envases y embalajes":
                producto.volume = line_quote.product_id.volume
            bom_line_values = {'bom_id':bom.id,
                               'product_id':line_quote.product_id.id,
                               'product_qty':line_quote.qty}
            bom.write({'bom_line_ids':[(0,0,bom_line_values)]})

        return True

    def weightless(self):
        for line_quote in self.quote_line:
            if line_quote.product_id.weight == 0:
                return False
        return True


    @api.one
    def valorar_presupuesto(self):
        self.calcular_bases()

        if self.metodo_valoracion == "porcentaje":
            self.margen_porcentaje = self.porcentaje
            self.margen_abs = self.margen_porcentaje * self.cost_price / 100
            self.total_bases = self.cost_price + self.margen_abs
            if self.descuento1 != 0 or self.descuento2 != 0:
                self.total_bases = self.total_bases / (1 - ((self.descuento1 + self.descuento2)/100))
            self.amount_total = 0
            for taxes in self.quote_taxes:
                taxes.base = taxes.porcentaje * self.total_bases / 100
                self.amount_total += taxes.base + (taxes.base * taxes.tax_id.amount/100)

        if self.metodo_valoracion == "margen":
            self.margen_abs = self.margen_valoracion
            self.total_bases = self.cost_price + self.margen_abs
            if self.descuento1 != 0 or self.descuento2 != 0:
                self.total_bases = self.total_bases / (1 - ((self.descuento1 + self.descuento2)/100))
            self.margen_porcentaje = self.margen_abs * 100 / self.cost_price
            self.amount_total = 0
            for taxes in self.quote_taxes:
                taxes.base = taxes.porcentaje * self.total_bases / 100
                self.amount_total += taxes.base + (taxes.base * taxes.tax_id.amount/100)
        if self.metodo_valoracion == "ii":
            self.amount_total = self.iva_incluido
            self.total_bases = 0
            for taxes in self.quote_taxes:
                base_temp = self.amount_total * taxes.porcentaje / 100.00
                taxes.base = base_temp / (1.00000 + taxes.tax_id.amount/100)
                self.total_bases += taxes.base
            self.margen_abs = self.total_bases - self.cost_price
            self.margen_porcentaje = self.margen_abs * 100 / self.cost_price
        if self.metodo_valoracion == "bases":
            self.total_bases = self.bases
            self.margen_abs = self.total_bases - self.cost_price
            self.margen_porcentaje = self.margen_abs * 100 / self.cost_price
            self.amount_total = 0
            for taxes in self.quote_taxes:
                taxes.base = taxes.porcentaje * self.total_bases / 100
                self.amount_total += taxes.base + (taxes.base * taxes.tax_id.amount/100)
        if self.metodo_valoracion == "mismo":
            self.total_bases = self.total_bases + ((self.total_bases * self.mismo_precio)/100)
            self.margen_abs = self.total_bases - self.cost_price
            self.margen_porcentaje = self.margen_abs * 100 / self.cost_price
            self.amount_total = 0
            for taxes in self.quote_taxes:
                taxes.base = taxes.porcentaje * self.total_bases / 100
                self.amount_total += taxes.base + (taxes.base * taxes.tax_id.amount/100)

    @api.multi
    def calcular_bases(self):
        taxes = []
        self.quote_taxes = False
        for line in self.quote_line:
            if line.tax_line not in taxes:
                taxes.append(line.tax_line)
        for tax in taxes:
            tax_value = {'tax_id': tax.id, 'base': 0}
            self.write({'quote_taxes': [(0,0,tax_value)]})
        for line in self.quote_line:
            for tax in self.quote_taxes:
                if line.tax_line == tax.tax_id:
                    tax.base += line.cost_price * line.qty
                    tax.porcentaje = (tax.base / self.cost_price) * 100

    @api.multi
    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [('name', '=like', u"Copy of {}%".format(self.name))])
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default['name'] = new_name
        res = super(Quote,self).copy(default)
        res.origin = 'same_as'
        res.quote_origin = self
        res.margen_abs = False
        res.margen_porcentaje = False
        res.total_bases = False
        res.descuento1 = False
        res.descuento2 = False
        res.porcentaje = False
        res.metodo_valoracion = ''
        res.margen_valoracion = False
        res.iva_incluido = False
        res.bases = False
        res.amount_total = False

        res.quote_line = self.quote_line
        res.calcular_bases()
        return res


    @api.multi
    def action_approved(self):
        import pdb; pdb.set_trace()
        if self._validate_valoracion() is True:
            self.state = 'approved'
        else:
            raise exceptions.Warning('No se puede aprobar un presupuesto que no ha sido valorado')

    @api.multi
    def action_sent(self):
        self.state = 'sent'

    @api.multi
    def action_transfered(self):
        if self._validate_expiration() is True:
            if self._generate_pack():
                self.state = 'transfered'
        else:
            raise exceptions.Warning('No se puede traspasar, la fecha de expiración ya ha vencido')


    @api.multi
    def action_to_draft(self):
        self.state = 'draft'


class QuoteLine(models.Model):
    _name = 'sale.quote.line'
    _order = 'sequence, line_order'


    name = fields.Text(
        string='Description',
        related="product_id.description")
    sequence = fields.Integer(string='Sequence', default=10)
    line_order = fields.Integer(
        string= 'Line Order')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True)
    qty = fields.Integer(
        string='Quantity',
        default = '1')
    cost_price = fields.Float(
        string='Cost Price',
        related="product_id.standard_price")
    tax_line = fields.Many2many(
        comodel_name='account.tax',
        relation='tax_line',
        column1='quote_line',
        column2='tax',
        string='Taxes',
        related="product_id.taxes_id")
    line_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    line_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    quote_id = fields.Many2one(
        comodel_name='sale.quote',
        string='Quote')
    stock = fields.Float(
        string='Stock available',
        related="product_id.qty_available")

    currency_id = fields.Many2one(related='quote_id.currency_id', store=True, string='Currency', readonly=True)

    @api.model
    def create(self, vals):
        res = super(QuoteLine, self).create(vals)
        res.order = res.product_id.categ_id.order
        if not res.line_order:
            res.line_order = len(res.quote_id.quote_line)
        return res

    @api.onchange('qty')
    def _check_qty(self):
        for record in self:
            if record.qty < 1:
                record.qty = 1
                return {
                    'warning': {
                        'title': "Valor incorrecto",
                        'message': "La cantidad no puede ser menor que 1. Se cambiará automaticamente.",
                    },
                }

    @api.depends('qty', 'tax_line')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.cost_price
            taxes = line.tax_line.compute_all(price, line.quote_id.currency_id, line.qty, product=line.product_id, partner=line.quote_id.partner_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'line_total': taxes['total_included'],
                'line_subtotal': taxes['total_excluded'],
            })


class QuoteTax(models.Model):
    _name = 'sale.quote.tax'

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Tax')
    base = fields.Float(
        string='base')
    porcentaje = fields.Float(
        string='%')
    quote_id = fields.Many2one(
        comodel_name='sale.quote',
        inverse_name='quote_taxes',
        string='Quote')
