---
type: schema
title: "Employees table"
description: "Synthetic employee directory with department and role fields"
tags: ['schema', 'MySQL', 'database']---

Table: employees
Columns: id (INT primary key), full_name (VARCHAR), email (VARCHAR unique), department (VARCHAR), job_title (VARCHAR), manager_name (VARCHAR), location (VARCHAR), hire_date (DATE), salary_band (VARCHAR), employment_status (VARCHAR).
Use this table for employee counts, department distributions, location summaries, and employee directory questions. Data is synthetic.
