# -*- coding: utf8 -*-
#
# Copyright (C) 2018 NDP Systèmes (<http://www.ndp-systemes.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from odoo import fields, models


class ProjectTaskCategory(models.Model):
    _name = 'project.task.category'

    name = fields.Char(u"Name")
    project_id = fields.Many2one('project.project', string=u"Project")

    active = fields.Boolean(u"Active", default=True, readonly=True)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    category_id = fields.Many2one('project.task.category', string=u"Category")
