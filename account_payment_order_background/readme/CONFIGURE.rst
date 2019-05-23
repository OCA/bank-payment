It is advised to configure the job runner to run one job at once for
the channel used for reconciliations, otherwise they'll issue many locks::

    ODOO_QUEUE_JOB_CHANNELS: root:4,root.background.move_reconcile:1
