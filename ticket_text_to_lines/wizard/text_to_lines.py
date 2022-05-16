# -*- coding: utf-8 -*-
from calendar import month_abbr
from datetime import datetime
import pty
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import re

class TicketText(models.TransientModel):
    _name = 'ticket.text'

    file_to_upload = fields.Binary(string="File")
    file_name = fields.Char(string="Filename")
    file_type = fields.Selection([('combined', 'Combined'), ('kenya', 'Kenya')], string='Airline')
    
    def get_text(self):
        if self.file_type:
            if self.file_type == 'combined':
                self.ticket_lines_from_text()
            elif self.file_type == 'kenya':
                self.ticket_lines_from_text_pegasus()
        else:
            raise UserError('Please choose the Airline')
    
    #for Combined 3 Airlines
    def ticket_lines_from_text(self):
        pax_sales = self.env['x_pax_sales'].search([('id','=',self._context.get('active_id'))])
        if not self.file_to_upload:
            raise UserError('Please upload file first')

        file_data = base64.b64decode(self.file_to_upload)
        filedata = file_data.decode("utf-8")
        lines = filedata.split('\n')
        vals_lst = []
        vals={}

        count=0 #line number counter
        tax_count = 1 #tax counter
        new_line_valid = False

        for line in lines:
            if ">" in line and new_line_valid: #checking new ticket starting
                count = 0
                tax_count = 1
                vals_lst.append(vals)
                vals={}

            count += 1 #line number

            if count==3:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'ticket_number':formatted_string.split(' ')[0],
                    
                })
                new_line_valid = True

            elif count==4:
                formatted_string = re.sub(' +', ' ', line.strip())
                raise UserError(formatted_string.split(' ')[3].split('-')[1])
                vals.update({
                    'source_location':formatted_string.split(' ')[0][3:6],
                    'dest_location': formatted_string.split(' ')[0][6:9],
                    'point_of_issuance': formatted_string.split(' ')[3].split('-')[1],
                    'date_of_issuance': formatted_string.split(' ')[4].split('-')[1],
                    'PNR': formatted_string.split(' ')[5].split('-')[1],
                    
                })

            elif count==5:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                full_name = ''
                for data in new_str:
                    full_name+=(data+' ')
                    if data in ['MR', 'MRS', 'MS']:
                        break
                if '1.' in full_name:
                    full_name = full_name.replace('1.', '')
                
                pt = False
                for data in new_str:
                    if pt:
                        passenger_type = data
                        break
                    if data in ['MR', 'MRS', 'MS']:
                        pt = True
                
                vals.update({
                    'name':full_name,
                    'passenger_type': passenger_type,
                })

            elif count==10:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'fare':new_str[len(new_str)-1],
                })

            elif count==11:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'equiv':formatted_string.split(' ')[2],
                })
            
            elif count==12:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total_tax':new_str[len(new_str)-1],
                })
            
            elif count==13:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total':new_str[len(new_str)-1],
                })
            
            elif count>20:
                lst_tax = []
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                div_len = len(new_str)/3
                sub_lst_tax = []
                for i in range(1,int(div_len)+1):
                    mul_index = int((i*3)-1)
                    key = 'TX0'+str(tax_count)
                    vals.update({
                        key:new_str[mul_index][:-2:],
                    })
                    tax_count+=1

        vals_lst.append(vals)

        for val in vals_lst:
            analytical_tag_id = self.env['account.analytic.tag'].search([('name','=',val['point_of_issuance'])])
            pax_sales.x_studio_analytic_tag = analytical_tag_id.id
           # pax_sales.x_studio_text_date = val['date_of_issuance']
            date_number = val['date_of_issuance'][:2]
            year_number = val['date_of_issuance'][5:]
            month_name = val['date_of_issuance'][2:5]
            df = date_number+'-'+month_name+'-'+year_number
            new_date = datetime.strptime(df,'%d-%b-%y').strftime('%Y-%m-%d')
            pax_sales.x_studio_date = new_date
            pax_sales.x_studio_portal_ref = val['PNR']
            break
        for val in vals_lst:
            sourceid = 0
            destid = 0
            ptype = ''

            if val['passenger_type'] == 'ADT':
                ptype = 'Adult'
            elif val['passenger_type'] == 'CHD':
                ptype = 'Child'
            elif val['passenger_type'] == 'INT':
                ptype = 'Infant'

            partner_id = self.env['res.partner'].create({
                'name': val['name'],
                'company_type': 'person',
            })

            source_id = self.env['x_destination'].search([('x_name','=',val['source_location'])])
            if source_id:
                for data in source_id:
                    sourceid = data.id
                    break
            
            dest_id = self.env['x_destination'].search([('x_name','=',val['dest_location'])])
            if dest_id:
                for data in dest_id:
                    destid = data.id
                    break

            self.env['x_pax_sales_line'].create({
                'x_studio_pax_sales_id': pax_sales.id,
                'x_studio_passenger': partner_id.id,
                'x_studio_base_fare': val['equiv'],
#                 'x_studio_sub_total': val['fare'],
                'x_studio_passenger_type': ptype,
                'x_studio_from': sourceid,
                'x_studio_to': destid,
                'x_studio_ticket_': val['ticket_number'],
            })
    
    #for Pegasus
    def ticket_lines_from_text_pegasus(self):
        pax_sales = self.env['x_pax_sales'].search([('id','=',self._context.get('active_id'))])
        if not self.file_to_upload:
            raise UserError('Please upload file first')

        file_data = base64.b64decode(self.file_to_upload)
        filedata = file_data.decode("utf-8")
        lines = filedata.split('\n')
        vals_lst = []
        vals={}

        count=0 #line number counter
        tax_count = 1 #tax counter
        new_line_valid = False

        for line in lines:
            if ">" in line and new_line_valid: #checking new ticket starting
                count = 0
                tax_count = 1
                vals_lst.append(vals)
                vals={}

            count += 1 #line number

            if count==2:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'ticket_number':formatted_string.split(' ')[0],
                })
                new_line_valid = True

            elif count==3:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    # 'source_location':formatted_string.split(' ')[0][3:6],
                    # 'dest_location': formatted_string.split(' ')[0][6:9],
                    'point_of_issuance': formatted_string.split(' ')[3].split('-')[1],
                    'date_of_issuance': formatted_string.split(' ')[4].split('-')[1],
                })

            elif count==4:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                full_name = ''
                for data in new_str:
                    full_name+=(data+' ')
                    if data in ['MR', 'MRS', 'MS']:
                        break
                if '1.' in full_name:
                    full_name = full_name.replace('1.', '')
                
                pt = False
                for data in new_str:
                    if pt:
                        passenger_type = data
                        break
                    if data in ['MR', 'MRS', 'MS']:
                        pt = True
                
                vals.update({
                    'name':full_name,
                    'passenger_type': passenger_type,
                })

            elif count==12:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'fare':new_str[len(new_str)-1],
                })

            elif count==13:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'equiv':formatted_string.split(' ')[2],
                })
            
            elif count==14:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total_tax':new_str[len(new_str)-1],
                })

            elif count>26:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                if new_str[0] == 'Total':
                    pass
                else:
                    key = 'TX-'+new_str[0]
                    vals.update({
                        key:new_str[4],
                    })

        vals_lst.append(vals)

        for val in vals_lst:
            analytical_tag_id = self.env['account.analytic.tag'].search([('name','=',val['point_of_issuance'])])
            pax_sales.x_studio_analytic_tag = analytical_tag_id.id
#             pax_sales.x_studio_text_date = val['date_of_issuance']
            date_number = val['date_of_issuance'][:2]
            year_number = val['date_of_issuance'][5:]
            month_name = val['date_of_issuance'][2:5]
            df = date_number+'-'+month_name+'-'+year_number
            new_date = datetime.strptime(df,'%d-%b-%y').strftime('%Y-%m-%d')
            pax_sales.x_studio_date = new_date
            break
        for val in vals_lst:
            sourceid = 0
            destid = 0
            ptype = ''

            if val['passenger_type'] == 'ADT':
                ptype = 'Adult'
            elif val['passenger_type'] == 'CHD':
                ptype = 'Child'
            elif val['passenger_type'] == 'INT':
                ptype = 'Infant'

            partner_id = self.env['res.partner'].create({
                'name': val['name'],
                'company_type': 'person',
            })

            # source_id = self.env['x_destination'].search([('x_name','=',val['source_location'])])
            # if source_id:
            #     for data in source_id:
            #         sourceid = data.id
            #         break
            
            # dest_id = self.env['x_destination'].search([('x_name','=',val['dest_location'])])
            # if dest_id:
            #     for data in dest_id:
            #         destid = data.id
            #         break

            self.env['x_pax_sales_line'].create({
                'x_studio_pax_sales_id': pax_sales.id,
                'x_studio_passenger': partner_id.id,
                'x_studio_base_fare': val['equiv'],
#                 'x_studio_sub_total': val['fare'],
                'x_studio_passenger_type': ptype,
                # 'x_studio_from': sourceid,
                # 'x_studio_to': destid,
                'x_studio_ticket_': val['ticket_number'],
            })

