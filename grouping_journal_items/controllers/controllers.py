# -*- coding: utf-8 -*-
# from odoo import http


# class GroupingJournalItems(http.Controller):
#     @http.route('/grouping_journal_items/grouping_journal_items/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/grouping_journal_items/grouping_journal_items/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('grouping_journal_items.listing', {
#             'root': '/grouping_journal_items/grouping_journal_items',
#             'objects': http.request.env['grouping_journal_items.grouping_journal_items'].search([]),
#         })

#     @http.route('/grouping_journal_items/grouping_journal_items/objects/<model("grouping_journal_items.grouping_journal_items"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('grouping_journal_items.object', {
#             'object': obj
#         })
