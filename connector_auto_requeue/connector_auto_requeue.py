# -*- coding: utf8 -*-
#
# Copyright (C) 2019 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp import models


class QueueJob(models.Model):
    _inherit = 'queue.job'

    def _register_hook(self, cr):
        if not hasattr(QueueJob, 'requeue_on_started'):
            QueueJob.requeue_on_started = True
            started_jobs_ids = self.search(cr, 1, [('state', '=', 'started')])
            started_jobs = self.browse(cr, 1, started_jobs_ids)
            started_jobs.requeue()
        return super(QueueJob, self)._register_hook(cr)
