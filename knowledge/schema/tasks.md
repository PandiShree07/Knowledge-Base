---
type: schema
title: "Tasks table"
description: "Task assignments and delivery state"
tags: ['schema', 'MySQL', 'database']---

Table: tasks
Columns: id (INT primary key), project_id (INT foreign key to projects.id), assignee_employee_id (INT foreign key to employees.id), title (VARCHAR), status (VARCHAR), priority (VARCHAR), estimated_hours (INT), created_date (DATE), due_date (DATE).
Statuses include todo, in_progress, blocked, completed. Estimated hours are planning estimates, not actual hours worked.
