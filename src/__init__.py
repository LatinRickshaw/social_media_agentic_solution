"""
Social Media Post Generator
Multi-platform social media content generation using best-of-breed AI models
"""

import sys
from pathlib import Path

# Add project root to Python path for proper module resolution
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

__version__ = "1.0.0"
__author__ = "Christian Fitz-Gibbon"
