odoo.define('accounts_hierarchy.accounts_hierarchy', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var ReportWidget = require('accounts_hierarchy.AccountHierarchyWidget');
    var framework = require('web.framework');

    var QWeb = core.qweb;
    
    var AccountsHierarchy= AbstractAction.extend({
        xmlDependencies: ['/accounts_hierarchy/static/src/xml/accounts_hierarchy_report_backend.xml'],
        hasControlPanel: true,
        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.actionManager = parent;
            this.given_context = action.context;
            this.controller_url = action.context.url;
            if (action.context.context) {
                this.given_context = action.context.context;
            }
        },
        willStart: function() {
            return Promise.all([this._super.apply(this, arguments), this.get_html()]);
        },
        start: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.set_html();
            });
        },
        get_html: function() {
            var self = this;
            var defs = [];
            return this._rpc({
                    model: 'accounts.hierarchy',
                    method: 'get_html',
                    args: [self.given_context],
                })
                .then(function (result) {
                    self.html = result.html;
                    self.renderButtons();
                    defs.push(self.update_cp());
                    return Promise.all(defs);
                });
        },
        set_html: function() {
            var self = this;
            var def = Promise.resolve();
            if (!this.report_widget) {
                this.report_widget = new ReportWidget(this, this.given_context);
                def = this.report_widget.appendTo(this.$('.o_content'));
            }
            return def.then(function () {
                self.report_widget.$el.html(self.html);
            })
        },
        update_cp: function() {
            if (!this.$buttons) {
                this.renderButtons();
            }
            var status = {
                cp_content: {
                    $buttons: this.$buttons,                    
                },
            };
            return this.updateControlPanel(status);
        },
        renderButtons: function() {
            var self = this;
            this.$buttons = $(QWeb.render("accountsHierarchyReports.buttons", {}));
            this.$buttons.bind('click', function () {                
                if (this.id == "print_pdf"){
                    framework.blockUI();
                    var url_data = self.controller_url.replace('active_id', self.given_context.active_id);                        
                    session.get_file({
                        url: url_data.replace('output_format', 'pdf'),
                        complete: framework.unblockUI,
                        error: (error) => self.call('crash_manager', 'rpc_error', error),
                    });
                }
                if (this.id == "print_xls"){
                    framework.blockUI();
                    var url_data = self.controller_url.replace('active_id', self.given_context.active_id);                        
                    session.get_file({
                        url: url_data.replace('output_format', 'xls'),
                        complete: framework.unblockUI,
                        error: (error) => self.call('crash_manager', 'rpc_error', error),
                    });
                }
            });
            return this.$buttons;            
        },
        do_show: function() {
            this._super();
            this.update_cp();
        },

    });
    
    core.action_registry.add('accounts_hierarchy.accounts_hierarchy', AccountsHierarchy);    
    return AccountsHierarchy;
    
    });
