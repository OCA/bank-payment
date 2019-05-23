When a Payment Order goes from state "File generated" to "File uploaded" ("File
successfully uploaded" button), payment lines are reconciled with their
counterparts. This step is very slow for hundreds of lines and locks many
records for the whole duration of the process, including sales orders when the
'invoiced' quantity is updated.

When this module is installed, the reconciliations are processed as jobs, so
the locks are short and the UI doesn't stay stuck for too long.
