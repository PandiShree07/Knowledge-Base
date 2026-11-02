---
type: document
title: "MySQL Demo Schema Notes"
description: "Table relationships and interpretation of sample fields"
tags: ['schema', 'MySQL', 'foreign key']---

# MySQL Demo Schema Notes

The employees table is the synthetic directory. Attendance and leave_records reference employees.id. Projects reference employees through owner_employee_id. Tasks reference projects.id and employees.id through project_id and assignee_employee_id. IDs are stable synthetic identifiers for reproducible learning. Status and priority values are categorical and should be grouped consistently in SQL reports.
