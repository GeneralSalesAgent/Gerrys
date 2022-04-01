odoo.define('accounts_hierarchy.AccountHierarchyWidget', function (require) {
    'use strict';
    
    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var _t = core._t;

    var AccountHierarchyWidget = Widget.extend({
        events: {
            'click span.o_accounts_hierarchy_foldable': 'fold',
            'click span.o_accounts_hierarchy_unfoldable': 'unfold',
            'click span.o_accounts_hierarchy_action': 'boundLink',
        },
        init: function(parent) {
            this._super.apply(this, arguments);
        },
        start: function() {
            QWeb.add_template("/accounts_hierarchy/static/src/xml/accounts_hierarchy_report_line.xml");
            return this._super.apply(this, arguments);
        },
        boundLink: function(e) {
            e.preventDefault();
            var self = this            
            var account_id = $(e.currentTarget).data('id');
            var wizard_id = $(e.currentTarget).data('wizard_id');
            return this._rpc({
                model: 'accounts.hierarchy',
                method: 'get_child_ids',
                args: [parseInt(wizard_id, 10), parseInt(account_id, 10)],
            }).then(function (result) {   
                console.log("length",  result.length)
                if (result){
                    return self.do_action({
                        name: 'Journal Items',
                        type: 'ir.actions.act_window',
                        res_model: 'account.move.line',
                        domain: result,
                        views: [[false, 'list'], [false, 'form']],
                        view_mode: "list",
                        target: 'current'
                    });
                }            
            });
        },
        removeLine: function(element) {
            var self = this;
            var el, $el;
            var rec_id = element.data('id');
            var $accountEl = element.nextAll('tr[data-parent_id=' + rec_id + ']')
            for (el in $accountEl) {
                $el = $($accountEl[el]).find(".o_account_hierarchy_domain_line_0, .o_account_hierarchy_domain_line_1");

                if ($el.length === 0) {
                    break;
                }
                
                else {
                    var $nextEls = $($el[0]).parents("tr");
                    self.removeLine($nextEls);
                    $nextEls.remove();
                }
                $el.remove();
            }
            return true;
        },
        fold: function(e) {            
            this.removeLine($(e.target).parents('tr'));
            var active_id = $(e.target).parents('tr').find('td.o_accounts_hierarchy_td').data('id');    
            $(e.target).parents('tr').find('span.o_accounts_hierarchy_foldable').replaceWith(QWeb.render("unfoldable", {lineId: active_id}));
            $(e.target).parents('tr').toggleClass('o_accounts_hierarchy_unfolded');
        },
        unfold: function(e) {            
            var $CurretElement;
            $CurretElement = $(e.target).parents('tr').find('td.o_accounts_hierarchy_td');
            var active_id = $CurretElement.data('id');
            var wizard_id = $CurretElement.data('wizard_id');
            var active_model_id = $CurretElement.data('model_id');
            var row_level = $CurretElement.data('level');
            var $cursor = $(e.target).parents('tr');
            this._rpc({
                    model: 'accounts.hierarchy',
                    method: 'get_lines',
                    args: [parseInt(wizard_id, 10), parseInt(active_id, 10)],
                    kwargs: {
                        'model_id': active_model_id,
                        'level': parseInt(row_level) + 1 || 1
                    },
                })
                .then(function (lines) {
                    _.each(lines, function (line) {                        
                        $cursor.after(QWeb.render("report_accounts_hierarchy_lines", {l: line}));
                        $cursor = $cursor.next();                        
                    });
                });
            $(e.target).parents('tr').find('span.o_accounts_hierarchy_unfoldable').replaceWith(QWeb.render("foldable", {lineId: active_id}));
            $(e.target).parents('tr').toggleClass('o_accounts_hierarchy_unfolded');
        },

    });
    return AccountHierarchyWidget;
});