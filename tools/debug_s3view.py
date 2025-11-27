#!/usr/bin/env python3
"""
Debug launcher for s3view; bypasses console script entry-points.
"""

from cfs3.s3view import main

if __name__ == "__main__":
    main()