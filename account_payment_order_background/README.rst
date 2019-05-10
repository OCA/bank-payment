.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Account Payment Order in Background
===================================

When a Payment Order goes from state "File generated" to "File uploaded" ("File
successfully uploaded" button), payment lines are reconciled with their
counterparts. This step is very slow for hundreds of lines and locks many
records for the whole duration of the process, including sales orders when the
'invoiced' quantity is updated.

When this module is installed, the reconciliations are processed as jobs, so
the locks are short and the UI doesn't stay stuck for too long.

Installation
============

Queue Job is required and must be started.

Configuration
=============

It is advised to configure the job runner to run one job at once for
the channel used for reconciliations, otherwise they'll issue many locks::

    ODOO_QUEUE_JOB_CHANNELS: root:4,root.background.move_reconcile:1


Contributors
------------

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
