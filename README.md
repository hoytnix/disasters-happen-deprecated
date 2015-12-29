Disasters Happen
================

Are *you* prepared?



Changes
-------

v0.1

+   First commit!
+   Very basic support for Dropbox.
+   Un-configurable branch-like system.
+   Uni-directional file-support. (All files must have been on local at some point to be tracked.)
+   Insane TUI.



Todo
----

v0.2

+   Classification:
    + `[✓]` Console-class for TUI.
    + `[✓]` File-class.
    + `[✓]` Service-class interface for adding multiple API supports.

+   Configuration:
    + `[✓]` Seperate `branches` database from config of *what* to track.
    + `[✓]` Persistent config file.
    + `[✓]` Tracking should have `.gitignore`-like regex for ignoring files.
        + `[ ]` Should also be available on a package-specific level. 

+   Installation:
    + `[ ]` Step-by-step walkthrough for setting up an API key.
    + `[ ]` `secret.py`-file generation.

+   LocalFS:
    + `[✓]` Multi-level folder discovery 
    + `[✓]` Replace `~/` with blank-space. (It's *secret* for a reason.)
    + `[✓]` Properties. (size, path, checksum, etc.)

+   RemoteFS:
    + `[ ]` Interaction with service-class.

+   SyncFS:
    + `[ ]` File-mode detection:
        + `[ ]` Deletion; file no longer exists on LocalFS.
        + `[ ]` Modified; file data has been changed on LocalFS.
        + `[ ]` Moved; file path has changed on LocalFS.