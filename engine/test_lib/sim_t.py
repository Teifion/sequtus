"""
This module is designed to run black-box testing on the application's
main code base. Many parts of the game may be data-dependant and hard
to test in complete isolation. This module will take data and run the
simulation for a set number of cycles and then pass the result back to
the caller so that checks on the data can be performed.
"""

