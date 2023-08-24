# --
# Copyright (c) 2008-2023 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

from litecli import main as litecli
from mycli import main as mycli
from nagare import commands
from nagare.admin import command
from pgcli import main as pgcli

COLORS = {
    'completion-menu.completion.current': 'bg:#ffffff #000000',
    'completion-menu.completion': 'bg:#008888 #ffffff',
    'completion-menu.meta.completion.current': 'bg:#44aaaa #000000',
    'completion-menu.meta.completion': 'bg:#448888 #ffffff',
    'completion-menu.multi-column-meta': 'bg:#aaffff #000000',
    'scrollbar.arrow': 'bg:#003333',
    'scrollbar': 'bg:#00aaaa',
    'selected': '#ffffff bg:#6666aa',
    'search': '#ffffff bg:#4444aa',
    'search.current': '#ffffff bg:#44aa44',
    'bottom-toolbar': 'bg:#222222 #aaaaaa',
    'bottom-toolbar.off': 'bg:#222222 #888888',
    'bottom-toolbar.on': 'bg:#222222 #ffffff',
    'search-toolbar': 'noinherit bold',
    'search-toolbar.text': 'nobold',
    'system-toolbar': 'noinherit bold',
    'arg-toolbar': 'noinherit bold',
    'arg-toolbar.text': 'nobold',
    'bottom-toolbar.transaction.valid': 'bg:#222222 #00ff5f bold',
    'bottom-toolbar.transaction.failed': 'bg:#222222 #ff005f bold',
    # style classes for colored table output
    'output.header': '#00ff5f bold',
    'output.odd-row': '',
    'output.even-row': '',
    'output.null': '#808080',
}


class CLIConfig(dict):
    def as_bool(self, name):
        return self[name]

    as_int = as_bool


def create_lite_config(config_filename):
    return {
        'main': CLIConfig(
            multi_line=True,
            key_bindings='emacs',
            table_format='ascii',
            syntax_style='default',
            less_chatty=True,
            show_bottom_toolbar=True,
            wider_completion_menu=False,
            autocompletion=True,
            destructive_warning=True,
            login_path_as_host=False,
            auto_vertical_output=False,
            log_file='default',
            log_level='NONE',
            prompt_continuation='-> ',
            enable_pager=False,
        ),
        'colors': COLORS,
    }


def create_pg_config(config_filename):
    return {
        'main': CLIConfig(
            multi_line=True,
            table_format='ascii',
            show_bottom_toolbar=True,
            wider_completion_menu=False,
            destructive_warning='true',
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
            syntax_style='default',
            on_error='STOP',
            keyring=False,
            smart_completion=True,
            enable_pager=False,
            keyword_casing='auto',
            casing_file=None,
            generate_casing_file=False,
            generate_aliases=False,
            asterisk_column_order='table_order',
            qualify_columns='if_more_than_one_table',
            case_column_headers=False,
            search_path_filter=False,
            history_file='default',
        ),
        'data_formats': {'decimal': '', 'float': ''},
        'colors': COLORS,
    }


def create_my_config(config_filename, list_values=False):
    main_config = CLIConfig(
        multi_line=True,
        key_bindings='emacs',
        timing=True,
        beep_after_seconds=0,
        table_format='ascii',
        syntax_style='default',
        less_chatty=True,
        wider_completion_menu=False,
        destructive_warning=True,
        login_path_as_host=False,
        auto_vertical_output=False,
        log_file='',
        log_level='NONE',
        prompt_continuation='-> ',
        smart_completion=True,
        pager=None,
        enable_pager=False,
    )

    config = CLIConfig(main=main_config, colors=COLORS, alias_dsn=None)
    config.filename = mycli.MyCli.system_config_files[0]

    return config


litecli.get_config = create_lite_config
pgcli.get_config = create_pg_config
mycli.read_config_files = create_my_config


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
            dbname=database_uri.database,
            username_opt=database_uri.username,
            host=database_uri.host,
            port=database_uri.port,
            prompt_passwd=False,
            never_prompt=True,
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
        mycli.cli.callback(
            database=database_uri.database,
            user=database_uri.username,
            host=database_uri.host,
            port=database_uri.port,
            socket='',
            password=database_uri.password,
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
            password_file=None,
        )

    def run(self, database_service, db=None, **params):
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

        cli(engine.url, **params)
        return 0
