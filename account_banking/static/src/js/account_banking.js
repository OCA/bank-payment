/*############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
#            
#    All other contributions are (C) by their respective contributors
#
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsability of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs
#    End users who are looking for a ready-to-use solution with commercial
#    garantees and support are strongly adviced to contract EduSense BV
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################*/

openerp.account_banking = function(instance)
{
    var _t = instance.web._t;
    instance.web.Dialog.include(
    {
        close: function()
        {
            this._super.apply(this, arguments);
            if (this.dialog_title == _t("Match transaction"))
            {   
                // The match wizard can create or unlink a statement line
                // Force a reload of the view so that the correct lines
                // are shown.
                var parent = this.getParent()
                if (parent)
                {
                    var child = this.getParent().getChildren()[0];
                    if (child.views) {
                        _.each(child.views, function(view)
                               {
                                   if (view && view.controller)
                                   {
                                       view.controller.reload();
                                   }
                               }
                              );
                    }
                }
            }
        },
    });
}
