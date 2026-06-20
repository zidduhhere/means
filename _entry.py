"""PyInstaller entry point — delegates to the installed package."""
import sys
from means.__main__ import main

sys.exit(main())
