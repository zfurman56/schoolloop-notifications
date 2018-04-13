SchoolLoop Notification System (SLNS)
=====================================

This program will email you whenever your grades change, telling you which grade changed and by how much.

SLNS will check once a minute (by default) whether your grades have changed, and if so, email you.

SLNS is run at the command line, like so:

`python main.py {schoolloop school prefix} {schoolloop username} {schoolloop password} {destination email address} {sender email address} {sender password} {smtp address} {update time}`

By default, it runs continuously, checking for grade changes every 60 seconds. You can change this time with the final parameter (`update time`) by specifying it. You may wish to run it in the background so as not to permanently occupy a terminal window.
