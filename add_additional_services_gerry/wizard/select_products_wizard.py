# -*- coding: utf-8 -*-
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import UserError


class SelectServices(models.TransientModel):

    _name = 'select.services'
    _description = 'Select Services'

    product_ids = fields.One2many('all.services', 'selected_services', string='Services')

    #for populating wizard values
    def default_get(self, fields_list):
        res = super(SelectServices, self).default_get(fields_list)
        service_line = self.env['all.services.line'].search([('order_line_id','=',self._context.get('active_id'))])
        if service_line:
            ids=[]
            for line in service_line:
                createID = self.env['all.services'].create({
                        'product_id':line.product_id.id,
                        'price': line.price,
                        'selected_services': self.id,
                    })
                ids.append(createID.id)
            res.update(product_ids=[(4,id) for id in ids])
        return res

    def select_services(self):
        order_line = self.env['x_pax_sales_line'].browse(self._context.get('active_id', False))
        for record in self:
            subtotal = order_line.x_studio_sub_total - order_line.x_studio_services_cost
            order_line.write({
                    'x_studio_services_cost':False,
                    'x_studio_additional_services':False,
                    'x_studio_sub_total':subtotal
                })
            services_line = self.env['all.services.line'].search([('order_line_id','=',self._context.get('active_id', False))])
            if services_line:
                for sl in services_line:
                    sl.unlink()
            if record.product_ids:
                totalcost = 0
                subtotal = order_line.x_studio_sub_total
                for data in record.product_ids:
                    totalcost+=data.price
                    subtotal+=data.price
                    order_line.write({
                        'x_studio_services_cost':totalcost,
                        'x_studio_additional_services':[(4,data.product_id.id)],
                        'x_studio_sub_total':subtotal
                    })

                    createID = self.env['all.services.line'].create({
                        'product_id': data.product_id.id,
                        'price': data.price,
                        'order_line_id': order_line.id,
                        'order_id': order_line.x_studio_pax_sales_id.id,
                    })

class Services(models.TransientModel):

    _name = 'all.services'
    _description = 'Services'

    selected_services = fields.Many2one('select.services', string='Selected Services')
    product_id = fields.Many2one('product.product', string='Product')
    price = fields.Float(string='Price')

# class SOrderLine(models.Model):

#     _inherit = 'x_pax_sales_line'

#     additional_services = fields.Many2many('product.product', string='Additional Services')
#     total_cost = fields.Float(string='Total Cost')

class ServicesLine(models.Model):

    _name = 'all.services.line'
    _description = 'Services Lines'

    product_id = fields.Many2one('product.product', string='Product')
    price = fields.Float(string='Price')
    order_line_id = fields.Many2one('x_pax_sales_line', string='PAX Line ID')
    order_id = fields.Many2one('x_pax_sales', string='PAX ID')

class Product(models.Model):

    _inherit = 'product.template'

    additional_service = fields.Boolean(string="Additional Service")
