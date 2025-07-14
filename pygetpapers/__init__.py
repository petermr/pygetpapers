"""
pygetpapers module
"""

def main():
    """Main entry point for pygetpapers CLI."""
    from pygetpapers import Pygetpapers
    callpygetpapers = Pygetpapers()
    callpygetpapers.create_argparser()
