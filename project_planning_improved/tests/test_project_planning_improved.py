# -*- coding: utf8 -*-
#
# Copyright (C) 2017 NDP Systèmes (<http://www.ndp-systemes.fr>).
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

from openerp.tests import common
from openerp.exceptions import UserError, ValidationError


class TestTemplateTasksPlanningImproved(common.TransactionCase):
    def setUp(self):
        super(TestTemplateTasksPlanningImproved, self).setUp()
        self.test_project = self.browse_ref('project_planning_improved.project_planning_improved_test_project')
        self.demo_user = self.browse_ref('base.user_demo')
        self.parent_task_0 = self.browse_ref('project_planning_improved.parent_task_0')
        self.parent_task_1 = self.browse_ref('project_planning_improved.parent_task_1')
        self.parent_task_2 = self.browse_ref('project_planning_improved.parent_task_2')
        self.parent_task_3 = self.browse_ref('project_planning_improved.parent_task_3')
        self.project_task_1 = self.browse_ref('project_planning_improved.project_task_1')
        self.project_task_2 = self.browse_ref('project_planning_improved.project_task_2')
        self.project_task_3 = self.browse_ref('project_planning_improved.project_task_3')
        self.project_task_4 = self.browse_ref('project_planning_improved.project_task_4')
        self.project_task_5 = self.browse_ref('project_planning_improved.project_task_5')
        self.project_task_6 = self.browse_ref('project_planning_improved.project_task_6')
        self.project_task_7 = self.browse_ref('project_planning_improved.project_task_7')
        self.project_task_8 = self.browse_ref('project_planning_improved.project_task_8')
        self.project_task_9 = self.browse_ref('project_planning_improved.project_task_9')
        self.project_task_10 = self.browse_ref('project_planning_improved.project_task_10')
        self.project_task_11 = self.browse_ref('project_planning_improved.project_task_11')

    def test_10_critical_task(self):
        """Testing the calculation of field 'critical_task'."""

        self.test_project.start_auto_planning()
        self.assertTrue(self.project_task_1.critical_task)
        self.assertTrue(self.project_task_2.critical_task)
        self.assertFalse(self.project_task_3.critical_task)
        self.assertTrue(self.project_task_4.critical_task)
        self.assertFalse(self.project_task_5.critical_task)
        self.assertFalse(self.project_task_6.critical_task)
        self.assertFalse(self.project_task_7.critical_task)
        self.assertFalse(self.project_task_8.critical_task)
        self.assertTrue(self.project_task_9.critical_task)
        self.assertFalse(self.project_task_10.critical_task)
        self.assertTrue(self.project_task_11.critical_task)

    def test_20_allocated_duration(self):
        """Testing calculation of fields 'allocated_duration_unit_tasks' and 'total_allocated_duration'."""
        self.assertEqual(self.project_task_1.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_1.total_allocated_duration, 1)
        self.assertEqual(self.project_task_2.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_2.total_allocated_duration, 3)
        self.assertEqual(self.project_task_3.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_3.total_allocated_duration, 2)
        self.assertEqual(self.project_task_4.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_4.total_allocated_duration, 5)
        self.assertEqual(self.project_task_5.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_5.total_allocated_duration, 7)
        self.assertEqual(self.project_task_6.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_6.total_allocated_duration, 4)
        self.assertEqual(self.project_task_7.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_7.total_allocated_duration, 1)
        self.assertEqual(self.project_task_8.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_8.total_allocated_duration, 4)
        self.assertEqual(self.project_task_9.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_9.total_allocated_duration, 13)
        self.assertEqual(self.project_task_10.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_10.total_allocated_duration, 6)
        self.assertEqual(self.project_task_11.allocated_duration_unit_tasks, 0)
        self.assertEqual(self.project_task_11.total_allocated_duration, 7)

        self.assertEqual(self.parent_task_0.allocated_duration_unit_tasks, 1)
        self.assertEqual(self.parent_task_0.total_allocated_duration, 2)
        self.assertEqual(self.parent_task_1.allocated_duration_unit_tasks, 22)
        self.assertEqual(self.parent_task_1.total_allocated_duration, 26)
        self.assertEqual(self.parent_task_2.allocated_duration_unit_tasks, 17)
        self.assertEqual(self.parent_task_2.total_allocated_duration, 19)
        self.assertEqual(self.parent_task_3.allocated_duration_unit_tasks, 13)
        self.assertEqual(self.parent_task_3.total_allocated_duration, 16)

    def schedule_from_task_3(self):
        # Using task 3 as reference task
        self.test_project.reference_task_id = self.project_task_3
        self.test_project.reference_task_end_date = '2017-09-07 13:30:00'
        self.test_project.start_auto_planning()
        self.assertTrue(self.project_task_3.taken_into_account)
        self.assertEqual(self.project_task_3.objective_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_3.objective_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_1.objective_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.objective_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_2.objective_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_2.objective_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_4.objective_start_date, '2017-09-11 08:00:00')
        self.assertEqual(self.project_task_4.objective_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_5.objective_start_date, '2017-09-07 08:00:00')
        self.assertEqual(self.project_task_5.objective_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_6.objective_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_6.objective_end_date, '2017-09-11 18:00:00')
        self.assertEqual(self.project_task_7.objective_start_date, '2017-09-12 08:00:00')
        self.assertEqual(self.project_task_7.objective_end_date, '2017-09-12 18:00:00')
        self.assertEqual(self.project_task_8.objective_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.project_task_8.objective_end_date, '2017-09-21 18:00:00')
        self.assertEqual(self.project_task_9.objective_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.project_task_9.objective_end_date, '2017-10-04 18:00:00')
        self.assertEqual(self.project_task_10.objective_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.project_task_10.objective_end_date, '2017-10-12 18:00:00')
        self.assertEqual(self.project_task_11.objective_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.project_task_11.objective_end_date, '2017-10-13 18:00:00')
        self.assertEqual(self.parent_task_0.objective_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.parent_task_0.objective_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.parent_task_1.objective_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.parent_task_1.objective_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.parent_task_2.objective_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.parent_task_2.objective_end_date, '2017-10-04 18:00:00')
        self.assertEqual(self.parent_task_3.objective_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.parent_task_3.objective_end_date, '2017-10-13 18:00:00')
        for task in self.test_project.task_ids:
            self.assertEqual(task.objective_start_date, task.expected_start_date)
            self.assertEqual(task.objective_end_date, task.expected_end_date)

    def test_30_auto_planning_task_no_next_task(self):
        """Testing the automatic scheduling of tasks. The reference task here has no next task"""

        self.schedule_from_task_3()
        # Rescheduling end date and transmit it to next tasks
        self.project_task_6.expected_end_date = '2017-09-12 15:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.project_task_6.expected_end_date, '2017-09-12 18:00:00')
        self.assertEqual(self.project_task_7.expected_start_date, '2017-09-13 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-13 18:00:00')
        self.assertEqual(self.parent_task_1.expected_end_date, '2017-09-15 18:00:00')
        self.assertFalse(self.project_task_6.taken_into_account)
        self.assertFalse(self.project_task_7.taken_into_account)

    def test_40_reschedule_task_out_of_its_parent(self):

        self.schedule_from_task_3()

        self.project_task_6.expected_end_date = '2017-09-15 18:00:00'
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_3.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_2.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_2.expected_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_4.expected_start_date, '2017-09-11 08:00:00')
        self.assertEqual(self.project_task_4.expected_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_5.expected_start_date, '2017-09-07 08:00:00')
        self.assertEqual(self.project_task_5.expected_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_6.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_6.expected_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_7.expected_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-18 18:00:00')
        self.assertEqual(self.project_task_8.expected_start_date, '2017-09-19 08:00:00')
        self.assertEqual(self.project_task_8.expected_end_date, '2017-09-22 18:00:00')
        self.assertEqual(self.project_task_9.expected_start_date, '2017-09-19 08:00:00')
        self.assertEqual(self.project_task_9.expected_end_date, '2017-10-05 18:00:00')
        self.assertEqual(self.project_task_10.expected_start_date, '2017-10-09 08:00:00')
        self.assertEqual(self.project_task_10.expected_end_date, '2017-10-16 18:00:00')
        self.assertEqual(self.project_task_11.expected_start_date, '2017-10-09 08:00:00')
        self.assertEqual(self.project_task_11.expected_end_date, '2017-10-17 18:00:00')
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.parent_task_1.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.parent_task_1.expected_end_date, '2017-09-18 18:00:00')
        self.assertEqual(self.parent_task_2.expected_start_date, '2017-09-19 08:00:00')
        self.assertEqual(self.parent_task_2.expected_end_date, '2017-10-06 18:00:00')
        self.assertEqual(self.parent_task_3.expected_start_date, '2017-10-09 08:00:00')
        self.assertEqual(self.parent_task_3.expected_end_date, '2017-10-18 18:00:00')

    def test_50_auto_planning_task_no_previous_task(self):
        """Testing the automatic scheduling of tasks. The reference task here has no previous task"""

        # Using task 5 as reference task
        self.test_project.task_ids.write({'taken_into_account': False})
        self.test_project.reference_task_id = self.project_task_5
        self.test_project.reference_task_end_date = '2017-09-07 18:00:00'
        self.test_project.start_auto_planning()
        self.assertEqual(self.project_task_5.objective_start_date, '2017-08-30 08:00:00')
        self.assertEqual(self.project_task_5.objective_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_8.objective_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.project_task_8.objective_end_date, '2017-09-13 18:00:00')
        self.assertEqual(self.project_task_9.objective_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.project_task_9.objective_end_date, '2017-09-26 18:00:00')
        self.assertEqual(self.project_task_10.objective_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_10.objective_end_date, '2017-10-04 18:00:00')
        self.assertEqual(self.project_task_11.objective_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_11.objective_end_date, '2017-10-05 18:00:00')
        self.assertEqual(self.project_task_4.objective_start_date, '2017-09-01 08:00:00')
        self.assertEqual(self.project_task_4.objective_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_2.objective_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.project_task_2.objective_end_date, '2017-08-31 18:00:00')
        self.assertEqual(self.project_task_7.objective_start_date, '2017-09-07 08:00:00')
        self.assertEqual(self.project_task_7.objective_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_6.objective_start_date, '2017-09-01 08:00:00')
        self.assertEqual(self.project_task_6.objective_end_date, '2017-09-06 18:00:00')
        self.assertEqual(self.project_task_3.objective_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.project_task_3.objective_end_date, '2017-08-30 18:00:00')
        self.assertEqual(self.project_task_1.objective_start_date, '2017-08-28 08:00:00')
        self.assertEqual(self.project_task_1.objective_end_date, '2017-08-28 18:00:00')
        self.assertEqual(self.parent_task_0.objective_start_date, '2017-08-28 08:00:00')
        self.assertEqual(self.parent_task_0.objective_end_date, '2017-08-28 18:00:00')
        self.assertEqual(self.parent_task_1.objective_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.parent_task_1.objective_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.parent_task_2.objective_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.parent_task_2.objective_end_date, '2017-09-26 18:00:00')
        self.assertEqual(self.parent_task_3.objective_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.parent_task_3.objective_end_date, '2017-10-05 18:00:00')
        for task in self.test_project.task_ids:
            self.assertEqual(task.objective_start_date, task.expected_start_date)
            self.assertEqual(task.objective_end_date, task.expected_end_date)
        # Rescheduling start date and transmit it to previous tasks
        self.project_task_7.expected_start_date = '2017-09-05 18:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.project_task_7.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_6.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_6.expected_start_date, '2017-08-31 08:00:00')
        self.assertFalse(self.project_task_7.taken_into_account)
        self.project_task_7.taken_into_account = True
        self.assertFalse(self.project_task_6.taken_into_account)
        self.project_task_7.taken_into_account = False

        # Let's move task 6 out of parent task 1
        self.project_task_7.expected_start_date = '2017-08-30 18:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.project_task_7.expected_start_date, '2017-08-31 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_6.expected_start_date, '2017-08-25 08:00:00')
        self.assertEqual(self.project_task_6.expected_end_date, '2017-08-30 18:00:00')
        self.assertEqual(self.project_task_4.expected_start_date, '2017-09-01 08:00:00')
        self.assertEqual(self.project_task_4.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_2.expected_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.project_task_2.expected_end_date, '2017-08-31 18:00:00')
        self.assertEqual(self.project_task_3.expected_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.project_task_3.expected_end_date, '2017-08-30 18:00:00')
        self.assertEqual(self.project_task_5.expected_start_date, '2017-08-30 08:00:00')
        self.assertEqual(self.project_task_5.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_8.expected_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.project_task_8.expected_end_date, '2017-09-13 18:00:00')
        self.assertEqual(self.project_task_9.expected_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.project_task_9.expected_end_date, '2017-09-26 18:00:00')
        self.assertEqual(self.project_task_10.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_10.expected_end_date, '2017-10-04 18:00:00')
        self.assertEqual(self.project_task_11.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_11.expected_end_date, '2017-10-05 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-08-24 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-08-24 18:00:00')

        self.assertEqual(self.parent_task_0.expected_start_date, '2017-08-22 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-08-24 18:00:00')
        self.assertEqual(self.parent_task_1.expected_start_date, '2017-08-25 08:00:00')
        self.assertEqual(self.parent_task_1.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.parent_task_2.expected_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.parent_task_2.expected_end_date, '2017-09-26 18:00:00')
        self.assertEqual(self.parent_task_3.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.parent_task_3.expected_end_date, '2017-10-05 18:00:00')

    def test_60_reschedule_next_and_previous_tasks(self):
        """Testing the automatic rescheduling of next and previous tasks during manual moves of parent tasks"""

        self.schedule_from_task_3()

        self.parent_task_0.expected_start_date = '2017-08-15 18:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-08-16 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-09-05 18:00:00')
        self.assertFalse(self.parent_task_0.taken_into_account)

    def test_61_reschedule_and_raise_because_tia_parent(self):
        """Testing the automatic rescheduling of next and previous tasks during manual moves of parent tasks"""

        self.schedule_from_task_3()

        self.parent_task_0.expected_start_date = '2017-08-15 18:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-08-16 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-09-05 18:00:00')
        self.assertFalse(self.parent_task_0.taken_into_account)
        self.parent_task_0.taken_into_account = True
        with self.assertRaises(UserError):
            self.parent_task_3.expected_end_date = '2017-07-11 14:00:00'

    def test_62_reschedule_and_raise_because_tia_parent(self):
        """Testing the automatic rescheduling of next and previous tasks during manual moves of parent tasks"""

        self.schedule_from_task_3()

        self.parent_task_0.expected_start_date = '2017-08-15 18:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-08-16 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-09-05 18:00:00')
        self.assertFalse(self.parent_task_0.taken_into_account)
        self.parent_task_0.taken_into_account = True
        self.parent_task_3.taken_into_account = True
        with self.assertRaises(UserError):
            self.project_task_11.expected_end_date = '2017-10-20 18:00:00'

    def test_70_reschedule_children_tasks(self):
        """Testing the automatic rescheduling of children tasks during manual moves"""

        self.schedule_from_task_3()

        # Reschedulind start date of parent task 2
        self.parent_task_2.expected_start_date = '2017-09-11 08:00:00'
        self.assertEqual(self.parent_task_2.expected_start_date, '2017-09-11 08:00:00')
        self.assertEqual(self.parent_task_2.expected_end_date, '2017-10-04 18:00:00')

        # Tasks 8, 9, 10, 11 and parent task 3 should not have been rescheduled
        self.assertEqual(self.project_task_8.expected_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.project_task_8.expected_end_date, '2017-09-21 18:00:00')
        self.assertEqual(self.project_task_9.expected_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.project_task_9.expected_end_date, '2017-10-04 18:00:00')
        self.assertEqual(self.project_task_10.expected_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.project_task_10.expected_end_date, '2017-10-12 18:00:00')
        self.assertEqual(self.project_task_11.expected_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.project_task_11.expected_end_date, '2017-10-13 18:00:00')
        self.assertEqual(self.parent_task_3.expected_start_date, '2017-10-05 08:00:00')
        self.assertEqual(self.parent_task_3.expected_end_date, '2017-10-13 18:00:00')

        # Other tasks should have been rescheduled
        self.assertEqual(self.project_task_4.expected_start_date, '2017-09-04 08:00:00')
        self.assertEqual(self.project_task_4.expected_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_5.expected_start_date, '2017-08-31 08:00:00')
        self.assertEqual(self.project_task_5.expected_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_7.expected_start_date, '2017-09-08 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_6.expected_start_date, '2017-09-04 08:00:00')
        self.assertEqual(self.project_task_6.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_3.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_2.expected_start_date, '2017-08-30 08:00:00')
        self.assertEqual(self.project_task_2.expected_end_date, '2017-09-01 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-08-29 18:00:00')
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-08-29 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-08-29 18:00:00')
        self.assertEqual(self.parent_task_1.expected_start_date, '2017-08-30 08:00:00')
        self.assertEqual(self.parent_task_1.expected_end_date, '2017-09-08 18:00:00')

    def test_80_early_start_date(self):
        """Testing the manual scheduling of tasks out of working periods"""

        self.schedule_from_task_3()

        # We try to set a start date early in the morning
        self.assertTrue(self.project_task_3.taken_into_account)
        with self.assertRaises(UserError):
            self.project_task_3.expected_start_date = '2017-09-04 02:00:00'

    def test_81_reschedule_start_date_in_weekend(self):
        """Testing the manual scheduling of tasks out of working periods"""

        self.schedule_from_task_3()

        # We try to set a start date early in the morning
        self.assertTrue(self.project_task_3.taken_into_account)
        self.project_task_3.taken_into_account = False
        self.project_task_3.expected_start_date = '2017-09-04 02:00:00'
        self.project_task_3.taken_into_account = True
        self.env.invalidate_all()
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-04 08:00:00')

        # We try to set a start date during a weekend
        with self.assertRaises(UserError):
            self.project_task_3.expected_start_date = '2017-09-03 15:00:00'

    def test_82_reschedule_start_date_in_weekend(self):
        """Testing the manual scheduling of tasks out of working periods"""

        self.schedule_from_task_3()

        # We try to set a start date early in the morning
        self.assertTrue(self.project_task_3.taken_into_account)
        self.project_task_3.taken_into_account = False
        self.project_task_3.expected_start_date = '2017-09-04 02:00:00'
        self.project_task_3.taken_into_account = True
        self.env.invalidate_all()
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-04 08:00:00')

        # We try to set a start date during a weekend
        with self.assertRaises(ValidationError):
            self.project_task_3.taken_into_account = False
            self.project_task_3.expected_start_date = '2017-09-03 15:00:00'

    def test_83_reschedule_start_date_in_weekend(self):
        """Testing the manual scheduling of tasks out of working periods"""

        self.schedule_from_task_3()

        # We try to set a start date early in the morning
        self.assertTrue(self.project_task_3.taken_into_account)
        self.project_task_3.taken_into_account = False
        self.project_task_3.expected_start_date = '2017-09-04 02:00:00'
        self.project_task_3.taken_into_account = True
        self.env.invalidate_all()
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-04 08:00:00')

        # We try to set a end date late in the evening
        self.project_task_10.expected_end_date = '2017-09-15 22:00:00'
        self.env.invalidate_all()
        self.assertEqual(self.project_task_10.expected_end_date, '2017-09-15 18:00:00')

        # We try to set a end date during a weekend
        with self.assertRaises(ValidationError):
            self.project_task_10.expected_end_date = '2017-09-16 02:00:00'

    def test_89_schedule_task_in_weekend(self):

        self.schedule_from_task_3()
        # Rescheduling a task entirely in a weekend
        with self.assertRaises(ValidationError):
            self.project_task_10.write({
                'expected_start_date': '2017-09-09 08:00:00',
                'expected_end_date': '2017-09-09 18:00:00'})

    def test_90_reschedule_both_start_and_end_dates(self):

        self.schedule_from_task_3()

        # Rescheduling both start and end dates for a parent task
        self.test_project.task_ids.write({'taken_into_account': False})
        self.assertEqual(self.parent_task_2.expected_start_date, '2017-09-18 08:00:00')
        self.assertEqual(self.parent_task_2.expected_end_date, '2017-10-04 18:00:00')
        context = self.env.context.copy()
        if not context.get('params'):
            context['params'] = {}
        context['params']['view_type'] = 'timeline'
        self.parent_task_2.with_context(context).write({
            'expected_start_date': '2017-09-27 08:00:00',
            'expected_end_date': '2017-10-13 18:00:00',
        })

        self.assertEqual(self.parent_task_2.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.parent_task_2.expected_end_date, '2017-10-13 18:00:00')

        self.assertEqual(self.parent_task_3.expected_start_date, '2017-10-16 08:00:00')
        self.assertEqual(self.parent_task_3.expected_end_date, '2017-10-24 18:00:00')

        # Parent tasks 0 and 1 (and their children) should not have changed
        self.assertEqual(self.project_task_3.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_3.expected_end_date, '2017-09-07 18:00:00')
        self.assertEqual(self.project_task_1.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.project_task_1.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.project_task_2.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_2.expected_end_date, '2017-09-08 18:00:00')
        self.assertEqual(self.project_task_4.expected_start_date, '2017-09-11 08:00:00')
        self.assertEqual(self.project_task_4.expected_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_5.expected_start_date, '2017-09-07 08:00:00')
        self.assertEqual(self.project_task_5.expected_end_date, '2017-09-15 18:00:00')
        self.assertEqual(self.project_task_6.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.project_task_6.expected_end_date, '2017-09-11 18:00:00')
        self.assertEqual(self.project_task_7.expected_start_date, '2017-09-12 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-12 18:00:00')
        self.assertEqual(self.parent_task_0.expected_start_date, '2017-09-05 08:00:00')
        self.assertEqual(self.parent_task_0.expected_end_date, '2017-09-05 18:00:00')
        self.assertEqual(self.parent_task_1.expected_start_date, '2017-09-06 08:00:00')
        self.assertEqual(self.parent_task_1.expected_end_date, '2017-09-15 18:00:00')

        # Tasks 8 to 11 should have been rescheduled
        self.assertEqual(self.project_task_8.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_8.expected_end_date, '2017-10-02 18:00:00')
        self.assertEqual(self.project_task_9.expected_start_date, '2017-09-27 08:00:00')
        self.assertEqual(self.project_task_9.expected_end_date, '2017-10-13 18:00:00')
        self.assertEqual(self.project_task_10.expected_start_date, '2017-10-16 08:00:00')
        self.assertEqual(self.project_task_10.expected_end_date, '2017-10-23 18:00:00')
        self.assertEqual(self.project_task_11.expected_start_date, '2017-10-16 08:00:00')
        self.assertEqual(self.project_task_11.expected_end_date, '2017-10-24 18:00:00')

    def test_92_reschedule_and_raise_because_tia(self):
        self.schedule_from_task_3()
        self.assertTrue(self.project_task_3.taken_into_account)
        with self.assertRaises(UserError):
            self.project_task_1.expected_end_date = '2017-09-06 18:00:00'

    def test_95_reference_task_modification(self):
        self.test_project.reference_task_id = self.project_task_3
        self.test_project.reference_task_end_date = '2017-09-07 13:30:00'
        self.test_project.user_id = self.demo_user
        with self.assertRaises(UserError):
            self.test_project.sudo().write({'reference_task_end_date': '2017-09-08 13:30:00'})

    def test_96_schedule_task_between_two_opened_days(self):
        self.schedule_from_task_3()

        self.project_task_7.write({
            'expected_start_date': '2017-08-31 23:00:00',
            'expected_end_date': '2017-09-01 01:00:00'
        })
        self.assertEqual(self.project_task_7.expected_start_date, '2017-08-31 08:00:00')
        self.assertEqual(self.project_task_7.expected_end_date, '2017-09-01 18:00:00')
