---
type: document
title: "FAQ: Database Questions"
description: "How the assistant queries the demo database safely"
tags: ['FAQ', 'MySQL', 'database']---

# FAQ: Database Questions

The assistant uses the configured MySQL demo database and a read-only runtime account. It generates one SELECT query and limits returned rows. The seed script uses a separate account and is restricted to the database name uka_demo. Do not point the seed script at a production or real business database.
