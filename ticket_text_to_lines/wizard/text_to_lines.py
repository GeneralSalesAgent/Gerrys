# -*- coding: utf-8 -*-
from calendar import month_abbr
from datetime import datetime
import pty
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import re
from xlrd import open_workbook

class TicketText(models.TransientModel):
    _name = 'ticket.text'

    file_to_upload = fields.Binary(string="File")
    file_name = fields.Char(string="Filename")
    file_type = fields.Selection([('combined', 'Combined'), ('kenya', 'Kenya'), ('oman', 'Oman'), ('pegasus', 'Pegasus')], string='Airline')
    
    def get_text(self):
        if self.file_type:
            if self.file_type == 'combined':
                self.ticket_lines_from_text_combined()
            elif self.file_type == 'kenya':
                self.ticket_lines_from_text_kenya()
            elif self.file_type == 'oman':
                self.ticket_lines_from_text_oman()
            elif self.file_type == 'pegasus':
                self.ticket_lines_from_text_pegasus()
        else:
            raise UserError('Please choose the Airline')
    
    
    #for Pegasus Airline
    def ticket_lines_from_text_pegasus(self):
        pax_sales = self.env['x_pax_sales'].search([('id','=',self._context.get('active_id'))])
        if not self.file_to_upload:
            raise UserError('Please upload file first')

        wb = open_workbook(file_contents = base64.b64decode(self.file_to_upload))
        sheet = wb.sheets()[0]
        for s in wb.sheets():
            values = []
            for row in range(s.nrows):
                col_value = []
                for col in range(s.ncols):
                    value  = (s.cell(row,col).value)
#                     try:
                    value  = datetime(value)
                    raise UserError(str(value))
#                     except:
#                         value  = (s.cell(row,col).value)
                    col_value.append(value)
                values.append(col_value)
        raise UserError(str(values))
        
        
    #for Combined 3 Airlines
    def ticket_lines_from_text_combined(self):
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
        tax_lines = False
        fare_checked = False

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
                    'pnr_number':str(formatted_string.split(' ')[3]).split('-')[1],
                })
                new_line_valid = True

            elif count==4:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'source_location':formatted_string.split(' ')[0][3:6],
                    'dest_location': formatted_string.split(' ')[0][6:9],
                    'point_of_issuance': formatted_string.split(' ')[3].split('-')[1],
                    'date_of_issuance': formatted_string.split(' ')[4].split('-')[1],  
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

            line_formatted_string = re.sub(' +', ' ', line.strip())
            line_new_str = line_formatted_string.split(' ')
            if 'FARE' in line_new_str and not fare_checked:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'fare':new_str[len(new_str)-1],
                })
                fare_checked = True

            elif 'EQUIV' in line_new_str:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'equiv':formatted_string.split(' ')[2],
                })

            elif 'TOTALTAX' in line_new_str:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total_tax':new_str[len(new_str)-1],
                })

            elif 'TOTAL' in line_new_str:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total':new_str[len(new_str)-1],
                })

            elif 'twd/tax' in line_new_str:
                tax_lines = True

            elif 'TOTALTAX' not in line_new_str and tax_lines:
                lst_tax = []
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                div_len = len(new_str)/3
                sub_lst_tax = []
                for i in range(1,int(div_len)+1):
                    mul_index = int((i*3)-1)
                    # key = 'TX0'+str(tax_count)
                    key = 'Tax-'+new_str[mul_index][-2:]
                    vals.update({
                        key:new_str[mul_index][:-2],
                    })
                    tax_count+=1

        vals_lst.append(vals)
        total_tax = vals['total_tax']
        YQ = 'Tax-YQ'
        YR = 'Tax-YR'
        YR_value = 0
        YQ_value = 0
        

        if YQ in vals:
            # print("key exist" + " " +  vals['Tax-YQ'])
            YQ_value = vals['Tax-YQ']
        if YR in vals:
            # print("key exist" + " " + vals['Tax-YR'])
            YR_value = vals['Tax-YR']
       


#         Internation_taxes = float(total_tax) - (float(YQ_value)+float(YR_value)+float(RG_value)+float(SP_value)+float(YD_value))
        fuel_surcharge = float(YQ_value) + float(YR_value)
       

        for val in vals_lst:
            analytical_tag_id = self.env['account.analytic.tag'].search([('name','=',val['point_of_issuance'])])
#             pax_sales.x_studio_analytic_tag = analytical_tag_id.id
           # pax_sales.x_studio_text_date = val['date_of_issuance']
            date_number = val['date_of_issuance'][:2]
            year_number = val['date_of_issuance'][5:]
            month_name = val['date_of_issuance'][2:5]
            df = date_number+'-'+month_name+'-'+year_number
            new_date = datetime.strptime(df,'%d-%b-%y').strftime('%Y-%m-%d')
            pax_sales.x_studio_date = new_date
            pax_sales.x_studio_portal_ref = val['pnr_number']
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
            
#             raise UserError(str(val))
            self.env['x_pax_sales_line'].create({
                'x_studio_pax_sales_id': pax_sales.id,
                'x_studio_passenger': partner_id.id,
                'x_studio_base_fare': val['equiv'],
#                 'x_studio_sub_total': val['fare'],
                'x_studio_passenger_type': ptype,
                'x_studio_from': sourceid,
                'x_studio_to': destid,
                'x_studio_ticket_': val['ticket_number'],
                'x_studio_fuel_charges': fuel_surcharge,
                'x_studio_total_tax': total_tax,
            })
    
    #for Kenya Airline
    def ticket_lines_from_text_kenya(self):
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
        tax_lines = False
        fare_checked = False

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
                    'pnr_number':str(formatted_string.split(' ')[3]).split('-')[1],
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

            line_formatted_string = re.sub(' +', ' ', line.strip())
            line_new_str = line_formatted_string.split(' ')
            if 'FARE' in line_new_str and not fare_checked:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'fare':new_str[len(new_str)-1],
                })
                fare_checked = True

            elif 'EQUIV' in line_new_str:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'equiv':formatted_string.split(' ')[2],
                })

            elif 'TOTALTAX' in line_new_str:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total_tax':new_str[len(new_str)-1],
                })

            elif 'Code' in line_new_str and 'Currency' in line_new_str and 'Amount' in line_new_str and 'Status' in line_new_str:
                tax_lines = True

            elif tax_lines:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                if new_str[0] == 'Total':
                    pass
                else:
                    key = 'Tax-'+new_str[0]
                    vals.update({
                        key:new_str[4],
                    })

        vals_lst.append(vals)
        
        total_tax = vals['total_tax']
        YQ = 'Tax-YQ'
        YR = 'Tax-YR'
        YR_value = 0
        YQ_value = 0
        

        if YQ in vals:
            # print("key exist" + " " +  vals['Tax-YQ'])
            YQ_value = vals['Tax-YQ']
        if YR in vals:
            # print("key exist" + " " + vals['Tax-YR'])
            YR_value = vals['Tax-YR']
        


#         Internation_taxes = float(total_tax) - (float(YQ_value)+float(YR_value)+float(RG_value)+float(SP_value)+float(YD_value))
        fuel_surcharge = float(YQ_value.replace(',','')) + float(YR_value.replace(',',''))
       

        for val in vals_lst:
            analytical_tag_id = self.env['account.analytic.tag'].search([('name','=',val['point_of_issuance'])])
#             pax_sales.x_studio_analytic_tag = analytical_tag_id.id
#             pax_sales.x_studio_text_date = val['date_of_issuance']
            date_number = val['date_of_issuance'][:2]
            year_number = val['date_of_issuance'][5:]
            month_name = val['date_of_issuance'][2:5]
            df = date_number+'-'+month_name+'-'+year_number
            new_date = datetime.strptime(df,'%d-%b-%y').strftime('%Y-%m-%d')
            pax_sales.x_studio_date = new_date
            pax_sales.x_studio_portal_ref = val['pnr_number']
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
                'x_studio_fuel_charges': fuel_surcharge,
                'x_studio_total_tax': total_tax,
            })
    
    #for Oman Airline
    def ticket_lines_from_text_oman(self):
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
        tax_lines = False
        fare_checked = False
        total_checked = False
        equiv_checked = False

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
                    'name':str(formatted_string.split(' ')[1]).split('-')[1],
                })
                new_line_valid = True

            elif count==4:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'date_of_issuance':str(formatted_string.split(' ')[7]).split('-')[1],
                    'pnr_number':str(formatted_string.split(' ')[8]).split('-')[1],  
                })

            line_formatted_string = re.sub(' +', ' ', line.strip())
            line_new_str = line_formatted_string.split(' ')
            if count != 2 and 'FARE' in line_new_str and not fare_checked:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'fare':formatted_string.split(' ')[2],
                })
                fare_checked = True

            if count != 2 and 'EQUIV' in line_new_str and not equiv_checked:
                formatted_string = re.sub(' +', ' ', line.strip())
                vals.update({
                    'equiv':formatted_string.split(' ')[6],  
                })
                equiv_checked = True

            elif fare_checked and 'TOTAL' in line_new_str and not total_checked:
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                vals.update({
                    'total':formatted_string.split(' ')[len(new_str) - 1],
                })
                total_checked = True

            elif 'TAX' in line_new_str and 'SUMMARY' in line_new_str:
                tax_lines = True

            elif 'TAX' in line_new_str and tax_lines:
                lst_tax = []
                formatted_string = re.sub(' +', ' ', line.strip())
                new_str = formatted_string.split(' ')
                div_len = len(new_str)/2
                sub_lst_tax = []
                for i in range(1,int(div_len)+1):
                    mul_index = int((i*2)-1)
                    # key = 'TX0'+str(tax_count)
                    try:
                        check_int = float(new_str[mul_index][:-2])
                        key = 'Tax-'+new_str[mul_index][-2:]
                        vals.update({
                            key:new_str[mul_index][:-2],
                        })
                    except:
                        check_int = float(new_str[mul_index][:-3])
                        key = 'Tax-'+new_str[mul_index][-3:]
                        vals.update({
                            key:new_str[mul_index][:-3],
                        })
                    tax_count+=1

        vals_lst.append(vals)

        for val in vals_lst:
#             analytical_tag_id = self.env['account.analytic.tag'].search([('name','=',val['point_of_issuance'])])
#             pax_sales.x_studio_analytic_tag = analytical_tag_id.id
#             pax_sales.x_studio_text_date = val['date_of_issuance']
            date_number = val['date_of_issuance'][:2]
            year_number = val['date_of_issuance'][5:]
            month_name = val['date_of_issuance'][2:5]
            df = date_number+'-'+month_name+'-'+year_number
            new_date = datetime.strptime(df,'%d-%b-%y').strftime('%Y-%m-%d')
            pax_sales.x_studio_date = new_date
            pax_sales.x_studio_portal_ref = val['pnr_number']
            break
            
        for val in vals_lst:
#             sourceid = 0
#             destid = 0
#             ptype = ''

#             if val['passenger_type'] == 'ADT':
#                 ptype = 'Adult'
#             elif val['passenger_type'] == 'CHD':
#                 ptype = 'Child'
#             elif val['passenger_type'] == 'INT':
#                 ptype = 'Infant'

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
                'x_studio_sub_total': val['fare'],
                'x_studio_ticket_': val['ticket_number'],
            })

