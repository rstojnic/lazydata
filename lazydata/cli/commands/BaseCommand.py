"""
Base class for the command line interface command

"""

class BaseCommand:

    """
    Implement this method to define the argument parser for the command

    :ivar parser: The sub-argparser for this command

    """
    def add_arguments(self, parser):
        return parser

    """
    Extend this method to implement the functionality of the command
    
    :ivar args: The parsed argument for this command

    """
    def handle(self, args):
        raise NotImplementedError('This functionality is not yet implemented!')