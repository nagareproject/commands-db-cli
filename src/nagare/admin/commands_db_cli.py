# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

import os
import tempfile

from mycli import main as mycli
from pgcli import main as pgcli
from litecli import main as litecli
from pygments.styles import STYLE_MAP

from nagare import commands
from nagare.admin import command
from nagare.services.database import Database


class CLIConfig(dict):
    def as_bool(self, name):
        return self[name]

    as_list = as_int = as_bool


def create_lite_config(config, colors, config_filename):
    return {
        'main': CLIConfig(
            dict(
                config,
                key_bindings='emacs',
                less_chatty=True,
                show_bottom_toolbar=True,
                autocompletion=True,
                destructive_warning=True,
                login_path_as_host=False,
                auto_vertical_output=False,
                log_file='default',
                log_level='NONE',
            )
        ),
        'colors': colors,
    }


def create_pg_config(config, colors, config_filename):
    return {
        'main': CLIConfig(
            dict(
                config,
                show_bottom_toolbar=True,
                destructive_warning=[
                    'drop',
                    'shutdown',
                    'delete',
                    'truncate',
                    'alter',
                    'update',
                    'unconditional_update',
                ],
                log_file='default',
                log_level='NONE',
                auto_expand=True,
                expand=False,
                vi=False,
                timing=True,
                row_limit=1000,
                max_field_width='500',
                min_num_menu_lines=4,
                multiline_continuation_char='',
                on_error='STOP',
                keyring=False,
                smart_completion=True,
                keyword_casing='auto',
                casing_file=None,
                generate_casing_file=False,
                generate_aliases=False,
                asterisk_column_order='table_order',
                qualify_columns='if_more_than_one_table',
                case_column_headers=False,
                search_path_filter=False,
                history_file='default',
                auto_retry_closed_connection=False,
                destructive_warning_restarts_connection=False,
                destructive_statements_require_transaction=False,
                always_use_single_connection=False,
                alias_map_file=None,
            )
        ),
        'data_formats': {'decimal': '', 'float': ''},
        'colors': colors,
    }


def create_my_config(config, colors, config_filename, list_values=False):
    main_config = CLIConfig(
        dict(
            config,
            key_bindings='emacs',
            timing=True,
            beep_after_seconds=0,
            less_chatty=True,
            destructive_warning=True,
            login_path_as_host=False,
            auto_vertical_output=False,
            log_file='',
            log_level='NONE',
            smart_completion=True,
        )
    )

    config = CLIConfig(main=main_config, colors=colors, alias_dsn=None)
    config.filename = mycli.MyCli.system_config_files[0]

    return config


litecli.get_config = create_lite_config
pgcli.get_config = create_pg_config
mycli.read_config_files = create_my_config


def create_spec():
    table_formats = litecli.TabularOutputFormatter().supported_formats

    return {
        'cli': {
            'activated': 'boolean(default=False)',
            'wider_completion_menu': 'boolean(default=False, help="display the completions in several columns")',
            'multi_line': 'boolean(default=True, help="if True, the statements must end by a semi-colon")',
            'table_format': 'option({}, default="ascii")'.format(', '.join([f'"{t}"' for t in table_formats])),
            'syntax_style': 'option({}, default="default")'.format(', '.join([f'"{t}"' for t in STYLE_MAP])),
            'enable_pager': 'boolean(default=False)',
            'pager': 'string(default="less -SRXF")',
            'prompt_continuation': 'string(default="-> ")',
            'colors': {
                'completion-menu.completion.current': 'string(default="bg:#ffffff #000000")',
                'completion-menu.completion': 'string(default="bg:#008888 #ffffff")',
                'completion-menu.meta.completion.current': 'string(default="bg:#44aaaa #000000")',
                'completion-menu.meta.completion': 'string(default="bg:#448888 #ffffff")',
                'completion-menu.multi-column-meta': 'string(default="bg:#aaffff #000000")',
                'scrollbar.arrow': 'string(default="bg:#003333")',
                'scrollbar': 'string(default="bg:#00aaaa")',
                'selected': 'string(default="#ffffff bg:#6666aa")',
                'search': 'string(default="#ffffff bg:#4444aa")',
                'search.current': 'string(default="#ffffff bg:#44aa44")',
                'bottom-toolbar': 'string(default="bg:#222222 #aaaaaa")',
                'bottom-toolbar.off': 'string(default="bg:#222222 #888888")',
                'bottom-toolbar.on': 'string(default="bg:#222222 #ffffff")',
                'search-toolbar': 'string(default="noinherit bold")',
                'search-toolbar.text': 'string(default="nobold")',
                'system-toolbar': 'string(default="noinherit bold")',
                'arg-toolbar': 'string(default="noinherit bold")',
                'arg-toolbar.text': 'string(default="nobold")',
                'bottom-toolbar.transaction.valid': 'string(default="bg:#222222 #00ff5f bold")',
                'bottom-toolbar.transaction.failed': 'string(default="bg:#222222 #ff005f bold")',
                # style classes for colored table output
                'output.header': 'string(default="#00ff5f bold")',
                'output.odd-row': 'string(default="")',
                'output.even-row': 'string(default="")',
                'output.null': 'string(default="#808080")',
            },
        }
    }


Database.CONFIG_SPEC.update(create_spec())


class CLI(command.Command):
    DESC = 'interactive console'
    WITH_STARTED_SERVICES = True

    def set_arguments(self, parser):
        parser.add_argument('--db', help='name of the db section')
        parser.add_argument('-l', '--list', action='store_true', dest='list_databases', help='list the databases')

        super(CLI, self).set_arguments(parser)

    @staticmethod
    def run_lite_cli(database_uri, list_databases):
        litecli.cli.callback(
            database=database_uri.database,
            execute=r'\l' if list_databases else None,
            dbname=None,
            version=False,
            prompt='SQLite \\d> ',
            logfile=None,
            auto_vertical_output=None,
            table=True,
            csv=False,
            warn=None,
            liteclirc=None,
        )

    @staticmethod
    def run_pg_cli(database_uri, list_databases):
        pgcli.cli.callback(
            dbname=database_uri.render_as_string(hide_password=False),
            username_opt=None,
            host=None,
            port=None,
            prompt_passwd=False,
            never_prompt=False,
            single_connection=False,
            dbname_opt=None,
            username=None,
            version=False,
            pgclirc=None,
            dsn='',
            row_limit=None,
            less_chatty=True,
            prompt='PostgreSQL \\u@\\h/\\d> ',
            prompt_dsn='DSN',
            list_databases=list_databases,
            auto_vertical_output=False,
            list_dsn=False,
            warn=False,
            ssh_tunnel=None,
        )

    @staticmethod
    def run_my_cli(database_uri, list_databases):
        password_file, password_filename = tempfile.mkstemp()
        try:
            os.write(password_file, os.environ.get('MYSQLPASSWORD', '').encode('utf-8'))

            mycli.cli.callback(
                database=database_uri.render_as_string(hide_password=False),
                user=None,
                host=None,
                port=None,
                socket='',
                password=None,
                execute=r'\l' if list_databases else None,
                dbname=None,
                version=False,
                verbose=True,
                prompt='\\t \\u@\\h/\\d> ',
                logfile=None,
                defaults_group_suffix=None,
                defaults_file=None,
                login_path=None,
                auto_vertical_output=None,
                local_infile=None,
                ssl_enable=False,
                ssl_ca=None,
                ssl_capath=None,
                ssl_cert=None,
                ssl_key=None,
                ssl_cipher=None,
                ssl_verify_server_cert=False,
                table=True,
                csv=False,
                warn=None,
                myclirc='',
                dsn=None,
                list_dsn=False,
                ssh_user=None,
                ssh_host=None,
                ssh_port=None,
                ssh_password=None,
                ssh_key_filename=None,
                list_ssh_config=None,
                ssh_config_path=None,
                ssh_config_host=None,
                init_command=None,
                charset=None,
                password_file=password_filename,
            )
        finally:
            os.close(password_file)
            os.remove(password_filename)

    def run(self, database_service, db=None, list_databases=False):
        metadatas = {metadata.name: metadata for metadata in database_service.metadatas}

        if not db:
            if len(metadatas) == 1:
                db = next(iter(metadatas))
            else:
                raise commands.ArgumentError('missing --db option')

        engine = database_service.get_engine(metadatas[db])
        if engine.url.drivername.startswith('sqlite'):
            cli = self.run_lite_cli
        elif engine.url.drivername.startswith('postgresql'):
            cli = self.run_pg_cli
        elif engine.url.drivername.startswith('mysql'):
            cli = self.run_my_cli
        else:
            raise commands.ArgumentError('No CLI available for {} database'.format(engine.url.drivername))

        config = database_service.plugin_config['cli']
        colors = config.pop('colors')

        litecli.get_config = lambda *args, **kw: create_lite_config(config, colors, *args, **kw)
        pgcli.get_config = lambda *args, **kw: create_pg_config(config, colors, *args, **kw)
        mycli.read_config_files = lambda *args, **kw: create_my_config(config, colors, *args, **kw)

        cli(engine.url, list_databases)
        return 0
