#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Colored Logging Module

This module provides functionality to add colors to logging output
for better visual distinction between different log levels.
"""

import logging

# ANSI color codes
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[31m',     # ERROR
    'GREEN': '\033[32m',   # INFO
    'YELLOW': '\033[33m',  # WARNING
    'BLUE': '\033[34m',    # DEBUG
    'MAGENTA': '\033[35m', # CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on their level."""
    
    def __init__(self, fmt=None, datefmt=None, style='%'):
        """Initialize the formatter with specified format strings.
        
        Args:
            fmt: The format string for the message
            datefmt: The format string for the date/time
            style: The style of the format string
        """
        super().__init__(fmt, datefmt, style)
        self.level_colors = {
            logging.DEBUG: COLORS['BLUE'],
            logging.INFO: COLORS['GREEN'],
            logging.WARNING: COLORS['YELLOW'],
            logging.ERROR: COLORS['RED'],
            logging.CRITICAL: COLORS['MAGENTA'],
        }
    
    def format(self, record):
        """Format the log record with appropriate colors.
        
        Args:
            record: The log record to format
            
        Returns:
            The formatted, colored log message
        """
        # Get the original formatted message
        message = super().format(record)
        
        # Add color based on the log level
        if record.levelno in self.level_colors:
            color_code = self.level_colors[record.levelno]
            message = f"{color_code}{message}{COLORS['RESET']}"
            
        return message


def setup_colored_logging(level=logging.INFO, format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):
    """Set up colored logging for the root logger.
    
    Args:
        level: The logging level to use
        format_str: The format string for log messages
    """
    # Create a colored formatter
    formatter = ColoredFormatter(format_str)
    
    # Set up the console handler with the formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicates
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # Add the console handler
    root_logger.addHandler(console_handler)