# -*- coding: utf-8 -*-
from __future__ import print_function
from calendar import month_abbr
from datetime import datetime,date,timedelta
import pty
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import re
from xlrd import open_workbook
from itertools import count
import string
from xmlrpc import client as xmlrpclib
# import mysql.connector as sql
import sys
from datetime import datetime,timedelta
from csv import writer

class AttendanceWorkentries(models.TransientModel):
    _name = 'attendance.workentries'

    # file_to_upload = fields.Binary(string="Attendance File")
    # file_name = fields.Char(string="Filename")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
      
    def attendance_workentries_from_api(self):
        raise UserError(self.from_date)
        now = datetime.now() - timedelta(days = 1)
        current_time = now.strftime("%H:%M:%S")
        today_date=now.strftime("%Y-%m-%d")
        # df=pd.read_csv("log.csv")
        #Odoo Database Connection to Fetch Attendance Start
        # url_attendance = 'http://gerrys.odoo.com'
        url_attendance = 'http://gerrys-staging-5360658.dev.odoo.com'
        # db_attendance = 'generalsalesagent-gerrys-live-4467063'
        db_attendance = 'gerrys-staging-5360658'
        username_attendance = 'haris.jiwani@affinitysuite.net'
        password_attendance = 'gerrys@786'

        common_attendance = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url_attendance))
        models_attendance = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url_attendance))

        uid_attendance = common_attendance.login(db_attendance, username_attendance, password_attendance)


        var_attendance = common_attendance.version()

        models_attendance = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url_attendance))
        #Odoo Database Connection to Fetch Attendance End

        if models_attendance:
            print('Connection Established')

        #Fetch Attendance according to date
        # attendance = models_attendance.execute_kw(db_attendance, uid_attendance, password_attendance,
        #                 'hr.attendance', 'search_read',
        #                 [[['x_studio_check_date', '=', today_date]]],
        #                 {'fields': ['employee_id','check_in','check_out','worked_hours']})

        attendance = models_attendance.execute_kw(db_attendance, uid_attendance, password_attendance,
                        'hr.attendance', 'search_read',
                        [[('check_in','>=','%s 00:00:00'),('check_in','<=','%s 23:59:59')]],
                        {'fields': ['x_studio_date','employee_id','check_in','check_out','worked_hours','x_studio_attendance_type']})


        # print(len(attendance))

        #Odoo Database Connection to Work Entries Start
        # url_odoo = 'http://gerrys.odoo.com'
        url_odoo = 'http://gerrys-staging-5360658.dev.odoo.com'
        # db_odoo = 'generalsalesagent-gerrys-live-4467063'
        db_odoo = 'gerrys-staging-5360658'
        username_odoo = 'haris.jiwani@affinitysuite.net'
        password_odoo = 'gerrys@786'

        common_odoo = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo))
        models_odoo = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo))

        uid_odoo = common_odoo.login(db_odoo, username_odoo, password_odoo)

        var_odoo = common_odoo.version()

        models_odoo = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo))
        #Odoo Database Connection to Enter Work Entries End

        # if models_odoo:
        #     print('Connection Established')
        for record in attendance:
            checkValid = False
            try:
                checkValid = True
                #Creating Work Entries in Odoo    
                checkTime = record['check_in'].split(' ')[1]
                checkDate = record['check_in'].split(' ')[0]
                attendance_type = record['x_studio_attendance_type']
                employee_id = record['employee_id'][0]
                employee_id = str(employee_id)
                # print (employee_id)
                # print(attendance_type)
                checkTime = datetime.strptime(checkTime, '%H:%M:%S')
                checkTime = checkTime + timedelta(hours = 5)
                checkTime = checkTime.strftime("%H:%M:%S")
                # print(checkTime)
                grace_time = datetime(2021, 7, 23, 9, 30, 00)
                grace_time = grace_time.strftime("%H:%M:%S")
                start_date = checkDate+" "+"09:00:00"
                # print(start_date)

            
                if attendance_type == 'On Time':
                    id = models_odoo.execute_kw(db_odoo, uid_odoo, password_odoo, 'hr.work.entry', 'create', [{
                    'name': "Attendance: "+record['employee_id'][1],
                    'employee_id': record['employee_id'][0],
                    'date_start': checkDate+" "+"04:00:00",
                    'date_stop':  checkDate+" "+"12:00:00",
                    # 'duration': '08.00',
                    'work_entry_type_id': 1,
                    'state': 'draft'
                    }])
                    # print('Inserted: '+str(record))

                elif attendance_type == 'Late':
                    id = models_odoo.execute_kw(db_odoo, uid_odoo, password_odoo, 'hr.work.entry', 'create', [{
                    'name': "Attendance: "+record['employee_id'][1],
                    'employee_id': record['employee_id'][0],
                    'date_start': checkDate+" "+"04:00:00",
                    'date_stop':  checkDate+" "+"12:00:00",
                    # 'duration': '08.00',
                    'work_entry_type_id': 13,
                    'state': 'draft'
                    }])
                    # print('Inserted: '+str(record))
                    
                elif attendance_type == 'Absent':
                    id = models_odoo.execute_kw(db_odoo, uid_odoo, password_odoo, 'hr.work.entry', 'create', [{
                    'name': "Attendance: "+record['employee_id'][1],
                    'employee_id': record['employee_id'][0],
                    'date_start': checkDate+" "+"04:00:00",
                    'date_stop':  checkDate+" "+"12:00:00",
                    # 'duration': '08.00',
                    'work_entry_type_id': 5,
                    'state': 'draft'
                    }])
                    # print('Inserted: '+str(record))

                elif attendance_type == 'Half Day':
                    id = models_odoo.execute_kw(db_odoo, uid_odoo, password_odoo, 'hr.work.entry', 'create', [{
                    'name': "Attendance: "+record['employee_id'][1],
                    'employee_id': record['employee_id'][0],
                    'date_start': checkDate+" "+"04:00:00",
                    'date_stop':  checkDate+" "+"12:00:00",
                    # 'duration': '08.00',
                    'work_entry_type_id': 14,
                    'state': 'draft'
                    }])
                    # print('Inserted: '+str(record))
                            
                else:
                    # print('Could not insert: '+str(record))
                    checkValid = False

            except Exception as e:
                raise UserError(e.stdout)
                checkValid=False
            
            if not checkValid:
                try:
                    List_data=[record['employee_id'][0],record['employee_id'][1],record['check_in'],record['check_out']]
                    with open('log.csv', 'a') as f_object:
                        writer_object = writer(f_object)
                        writer_object.writerow(List_data)
                        f_object.close()
                
                except Exception as e:
                    raise UserError(e.stdout)