---
type: schema
title: "Attendance table"
description: "Attendance events linked to employees"
tags: ['schema', 'MySQL', 'database']---

Table: attendance
Columns: id (INT primary key), employee_id (INT foreign key to employees.id), attendance_date (DATE), status (VARCHAR), hours_worked (INT), work_mode (VARCHAR).
Status values in the seed data include present, remote, absent, half_day, and leave. Work modes include office, remote, and hybrid. Use explicit date filters for time-based reports.
