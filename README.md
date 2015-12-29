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
    + Seperate `branches` database from config of *what* to track.
    + `[✓]` Universal config file:
        + Chunk size.
        + Verbosity.
    + `[ ]` Tracking should have `.gitignore`-like regex for ignoring files.
+   Installation:
    + Step-by-step walkthrough for setting up an API key.
    + `secret.py`-file generation.
+   TUI:
    + `[✓]` Time precision. 
    + Real speed test.
    + `[✓]` Replace `~/` with blank-space. (It's *secret* for a reason.)
+   Packaging:
    + `[✓]` Multi-level folder discovery 
+   Files:
    + Deletion mode
    + Rename mode
    + `[✓]` Properties. (size, path, checksum, etc.)