import os
import sys
import pathlib
import logging
import inspect
import warnings
import argparse
import configparser

from copy import copy
from pathlib import Path
from collections import OrderedDict

from tomolog_cli import log

LOGS_HOME = os.path.join(str(pathlib.Path.home()), 'logs')
CONFIG_FILE_NAME = os.path.join(str(pathlib.Path.home()), 'logs', 'tomolog.conf')
TOKEN_HOME      = os.path.join(str(pathlib.Path.home()), 'tokens')

def default_parameter(func, param):
    """Get the default value for a function parameter.

    For a given function *func*, introspect the function and return
    the default value for the function parameter named *param*.

    Return
    ======
    default_val
      The default value for the parameter.

    Raises
    ======
    RuntimeError
      Raised if the function *func* has no default value for the
      requested parameter *param*.

    """
    # Retrieve the function parameter by introspection
    try:
        sig = inspect.signature(func)
        _param = sig.parameters[param]
    except TypeError as e:
        warnings.warn(str(e))
        log.warning(str(e))
        return None
    # Check if a default value exists
    if _param.default is _param.empty:
        # No default is listed in the function, so throw an exception
        msg = ("No default value given for parameter *{}* of callable {}."
               "".format(param, func))
        raise RuntimeError(msg)
    else:
        # Retrieve and return the parameter's default value
        return _param.default


SECTIONS = OrderedDict()


SECTIONS['general'] = {
    'config': {
        'default': CONFIG_FILE_NAME,
        'type': str,
        'help': "File name of configuration file",
        'metavar': 'FILE'},
    'logs-home': {
        'default': LOGS_HOME,
        'type': str,
        'help': "Log file directory",
        'metavar': 'FILE'},
    'token-home': {
        'default': TOKEN_HOME,
        'type': str,
        'help': "Token file directory",
        'metavar': 'FILE'},    
    'verbose': {
        'default': False,
        'help': 'Verbose output',
        'action': 'store_true'},
    'config-update': {
        'default': False,
        'help': 'When set, the content of the config file is updated using the current params values',
        'action': 'store_true'},
    'double-fov': {
        'default': False,
        'action': 'store_true',
        'help': "Set to true for 0-360 data sets"},
}

SECTIONS['file-reading'] = {
    'file-name': {
        'default': '.',
        'type': Path,
        'help': "Name of the hdf file",
        'metavar': 'PATH'},
}

SECTIONS['parameters'] = {
    'idx': {
        'type': int,
        'default': -1,
        'help': "Id of x slice for reconstruction visualization"},
    'idy': {
        'type': int,
        'default': -1,
        'help': "Id of y slice for reconstruction visualization"},
    'idz': {
        'type': int,
        'default': -1,
        'help': "Id of z slice for reconstruction visualization"},
    'max': {
        'type': float,
        'default': 0.0,
        'help': "Maximum threshold value for reconstruction visualization"},
    'min': {
        'type': float,
        'default': 0.0,
        'help': "Minimum threshold value for reconstruction visualization"},
    'beamline': {
        'default': '32-id',
        'type': str,
        'help': "Customized the goodle slide to the beamline selected",
        'choices': ['None','2-bm', '7-bm', '32-id']},
    'rec-type': {
        'default': 'rec',
        'type': str,
        'help': "Specify the prefix of the recon folder",
        'choices': ['recgpu','rec']},
    'PV-prefix': {
        'default': '32idcSP1:',
        'type': str,
        'help': "PV prefix for camera"},
    'presentation-url': {
        'default': None,
        'type': str,
        'help': "Google presention url"},
}

PARAMS = ('file-reading', 'parameters')
NICE_NAMES = ('General', 'File reading', 'Parameters')


def get_config_name():
    """Get the command line --config option."""
    name = CONFIG_FILE_NAME
    for i, arg in enumerate(sys.argv):
        if arg.startswith('--config'):
            if arg == '--config':
                return sys.argv[i + 1]
            else:
                name = sys.argv[i].split('--config')[1]
                if name[0] == '=':
                    name = name[1:]
                return name

    return name


def parse_known_args(parser, subparser=False):
    """
    Parse arguments from file and then override by the ones specified on the
    command line. Use *parser* for parsing and is *subparser* is True take into
    account that there is a value on the command line specifying the subparser.
    """
    if len(sys.argv) > 1:
        subparser_value = [sys.argv[1]] if subparser else []
        config_values = config_to_list(config_name=get_config_name())
        values = subparser_value + config_values + sys.argv[1:]
    else:
        values = ""

    return parser.parse_known_args(values)[0]


def config_to_list(config_name=CONFIG_FILE_NAME):
    """
    Read arguments from config file and convert them to a list of keys and
    values as sys.argv does when they are specified on the command line.
    *config_name* is the file name of the config file.
    """
    result = []
    config = configparser.ConfigParser()

    if not config.read([config_name]):
        return []

    for section in SECTIONS:
        for name, opts in ((n, o) for n, o in SECTIONS[section].items() if config.has_option(section, n)):
            value = config.get(section, name)

            if value != '' and value != 'None':
                action = opts.get('action', None)

                if action == 'store_true' and value == 'True':
                    # Only the key is on the command line for this action
                    result.append('--{}'.format(name))

                if not action == 'store_true':
                    if opts.get('nargs', None) == '+':
                        result.append('--{}'.format(name))
                        result.extend((v.strip() for v in value.split(',')))
                    else:
                        result.append('--{}={}'.format(name, value))

    return result


class Params(object):
    def __init__(self, sections=()):
        self.sections = sections + ('general', )

    def add_parser_args(self, parser):
        for section in self.sections:
            for name in sorted(SECTIONS[section]):
                opts = SECTIONS[section][name]
                parser.add_argument('--{}'.format(name), **opts)

    def add_arguments(self, parser):
        self.add_parser_args(parser)
        return parser

    def get_defaults(self):
        parser = argparse.ArgumentParser()
        self.add_arguments(parser)

        return parser.parse_args('')


def write(config_file, args=None, sections=None):
    """
    Write *config_file* with values from *args* if they are specified,
    otherwise use the defaults. If *sections* are specified, write values from
    *args* only to those sections, use the defaults on the remaining ones.
    """
    config = configparser.ConfigParser()

    for section in SECTIONS:
        config.add_section(section)
        for name, opts in SECTIONS[section].items():
            if args and sections and section in sections and hasattr(args, name.replace('-', '_')):
                value = getattr(args, name.replace('-', '_'))

                if isinstance(value, list):
                    value = ', '.join(value)
            else:
                value = opts['default'] if opts['default'] is not None else ''

            prefix = '# ' if value == '' else ''

            if name != 'config':
                config.set(section, prefix + name, str(value))

    with open(config_file, 'w') as f:
        config.write(f)


def show_config(args):
    """Log all values set in the args namespace.
    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    log.warning('status start')
    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted(
            (k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))
        if entries:
            for entry in entries:
                value = args[entry] if args[entry] != None else "-"
                log.info("  {:<16} {}".format(entry, value))

    log.warning('status end')


def log_values(args):
    """Log all values set in the args namespace.
    Arguments are grouped according to their section and logged alphabetically
    using the DEBUG log level thus --verbose is required.
    """
    args = args.__dict__

    log.warning('status start')
    for section, name in zip(SECTIONS, NICE_NAMES):
        entries = sorted(
            (k for k in args.keys() if k.replace('_', '-') in SECTIONS[section]))

        # print('log_values', section, name, entries)
        if entries:
            log.info(name)

            for entry in entries:
                value = args[entry] if args[entry] is not None else "-"
                if (value == 'none'):
                    log.warning("  {:<16} {}".format(entry, value))
                elif (value is not False):
                    log.info("  {:<16} {}".format(entry, value))
                elif (value is False):
                    log.warning("  {:<16} {}".format(entry, value))

    log.warning('status end')
