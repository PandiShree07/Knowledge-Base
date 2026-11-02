---
type: schema
title: "Leave records table"
description: "Leave requests and approval status"
tags: ['schema', 'MySQL', 'database']---

Table: leave_records
Columns: id (INT primary key), employee_id (INT foreign key to employees.id), leave_type (VARCHAR), start_date (DATE), end_date (DATE), days (INT), status (VARCHAR), reason (VARCHAR).
Status values include approved, pending, rejected. For approved usage, filter status='approved'. The demo does not store a complete entitlement ledger, so avoid claiming an official remaining balance.
