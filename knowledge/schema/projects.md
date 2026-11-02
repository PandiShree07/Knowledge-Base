---
type: schema
title: "Projects table"
description: "Project ownership, status, dates, and budget bands"
tags: ['schema', 'MySQL', 'database']---

Table: projects
Columns: id (INT primary key), project_name (VARCHAR), department (VARCHAR), owner_employee_id (INT foreign key to employees.id), status (VARCHAR), priority (VARCHAR), start_date (DATE), target_date (DATE), budget_band (VARCHAR).
Statuses include planning, in_progress, completed, on_hold. Budget bands are synthetic categories.
