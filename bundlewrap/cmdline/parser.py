# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from argparse import ArgumentParser
from os import environ

from .. import VERSION_STRING
from ..utils.text import mark_for_translation as _
from .apply import bw_apply
from .debug import bw_debug
from .groups import bw_groups
from .hash import bw_hash
from .items import bw_items
from .metadata import bw_metadata
from .nodes import bw_nodes
from .plot import bw_plot_group, bw_plot_node, bw_plot_node_groups
from .repo import bw_repo_bundle_create, bw_repo_create, bw_repo_plugin_install, \
    bw_repo_plugin_list, bw_repo_plugin_search, bw_repo_plugin_remove, bw_repo_plugin_update
from .run import bw_run
from .stats import bw_stats
from .test import bw_test
from .verify import bw_verify
from .zen import bw_zen


def build_parser_bw():
    parser = ArgumentParser(
        prog="bw",
        description=_("BundleWrap - Config Management with Python"),
    )
    parser.add_argument(
        "-a",
        "--add-host-keys",
        action='store_true',
        default=False,
        dest='add_ssh_host_keys',
        help=_("set StrictHostKeyChecking=no instead of yes for SSH"),
    )
    parser.add_argument(
        "-d",
        "--debug",
        action='store_true',
        default=False,
        dest='debug',
        help=_("print debugging info (implies -v)"),
    )
    parser.add_argument(
        "--version",
        action='version',
        version=VERSION_STRING,
    )
    subparsers = parser.add_subparsers(
        title=_("subcommands"),
        help=_("use 'bw <subcommand> --help' for more info"),
    )

    # bw apply
    help_apply = _("Applies the configuration defined in your repository to your nodes")
    parser_apply = subparsers.add_parser("apply", description=help_apply, help=help_apply)
    parser_apply.set_defaults(func=bw_apply)
    parser_apply.add_argument(
        'target',
        metavar=_("NODE1,NODE2,GROUP1,bundle:BUNDLE1..."),
        type=str,
        help=_("target nodes, groups and/or bundle selectors"),
    )
    parser_apply.add_argument(
        "-f",
        "--force",
        action='store_true',
        default=False,
        dest='force',
        help=_("ignore existing node locks"),
    )
    parser_apply.add_argument(
        "-i",
        "--interactive",
        action='store_true',
        default=False,
        dest='interactive',
        help=_("ask before applying each item"),
    )
    parser_apply.add_argument(
        "-p",
        "--parallel-nodes",
        default=int(environ.get("BWNODEWORKERS", "4")),
        dest='node_workers',
        help=_("number of nodes to apply to simultaneously"),
        type=int,
    )
    parser_apply.add_argument(
        "-P",
        "--parallel-items",
        default=int(environ.get("BWITEMWORKERS", "4")),
        dest='item_workers',
        help=_("number of items to apply to simultaneously on each node"),
        type=int,
    )
    parser_apply.add_argument(
        "--profiling",
        action='store_true',
        default=False,
        dest='profiling',
        help=_("print time elapsed for each item"),
    )
    parser_apply.add_argument(
        "-s",
        "--skip",
        default="",
        dest='autoskip',
        help=_(
            "e.g. 'file:/foo,tag:foo,bundle:bar,node:baz,group:frob' "
            "to skip all instances of file:/foo "
            "and items with tag 'foo', "
            "or in bundle 'bar', "
            "or on node 'baz', "
            "or on a node in group 'frob'"
        ),
        metavar=_("SELECTOR"),
        type=str,
    )

    # bw debug
    help_debug = _("Start an interactive Python shell for this repository")
    parser_debug = subparsers.add_parser("debug", description=help_debug, help=help_debug)
    parser_debug.set_defaults(func=bw_debug)
    parser_debug.add_argument(
        "-c",
        "--command",
        default=None,
        dest='command',
        metavar=_("COMMAND"),
        required=False,
        type=str,
        help=_("command to execute in lieu of REPL"),
    )
    parser_debug.add_argument(
        "-n",
        "--node",
        default=None,
        dest='node',
        metavar=_("NODE"),
        required=False,
        type=str,
        help=_("name of node to inspect"),
    )

    # bw groups
    help_groups = _("Lists groups in this repository")
    parser_groups = subparsers.add_parser("groups", description=help_groups, help=help_groups)
    parser_groups.set_defaults(func=bw_groups)
    parser_groups.add_argument(
        "-n",
        "--nodes",
        action='store_true',
        dest='show_nodes',
        help=_("show nodes for each group"),
    )

    # bw hash
    help_hash = _("Shows a SHA1 hash that summarizes the entire configuration for this repo, node, group, or item.")
    parser_hash = subparsers.add_parser("hash", description=help_hash, help=help_hash)
    parser_hash.set_defaults(func=bw_hash)
    parser_hash.add_argument(
        "-d",
        "--dict",
        action='store_true',
        default=False,
        dest='dict',
        help=_("instead show the data this hash is derived from"),
    )
    parser_hash.add_argument(
        'node_or_group',
        metavar=_("NODE|GROUP"),
        type=str,
        nargs='?',
        help=_("show config hash for this node or group"),
    )
    parser_hash.add_argument(
        'item',
        metavar=_("ITEM"),
        type=str,
        nargs='?',
        help=_("show config hash for this item on the given node"),
    )

    # bw items
    help_items = _("List and preview items for a specific node")
    parser_items = subparsers.add_parser("items", description=help_items, help=help_items)
    parser_items.set_defaults(func=bw_items)
    parser_items.add_argument(
        'node',
        metavar=_("NODE"),
        type=str,
        help=_("list items for this node"),
    )
    parser_items.add_argument(
        "-f",
        "--file-preview",
        dest='file_preview',
        help=_("print preview of given file"),
        metavar=_("FILE"),
        required=False,
        type=str,
    )
    parser_items.add_argument(
        "-w",
        "--write-file-previews",
        default=None,
        dest='file_preview_path',
        metavar=_("DIRECTORY"),
        required=False,
        type=str,
        help=_("create DIRECTORY and fill it with rendered file previews"),
    )
    parser_items.add_argument(
        "--repr",
        action='store_true',
        dest='show_repr',
        help=_("show more verbose representation of each item"),
    )

    # bw metadata
    help_metadata = ("View a JSON representation of a node's metadata")
    parser_metadata = subparsers.add_parser(
        "metadata",
        description=help_metadata,
        help=help_metadata,
    )
    parser_metadata.set_defaults(func=bw_metadata)
    parser_metadata.add_argument(
        'node',
        metavar=_("NODE"),
        type=str,
        help=_("node to print JSON-formatted metadata for"),
    )

    # bw nodes
    help_nodes = _("List all nodes in this repository")
    parser_nodes = subparsers.add_parser("nodes", description=help_nodes, help=help_nodes)
    parser_nodes.set_defaults(func=bw_nodes)
    parser_nodes.add_argument(
        "--bundles",
        action='store_true',
        dest='show_bundles',
        help=_("show bundles for each node"),
    )
    parser_nodes.add_argument(
        "--hostnames",
        action='store_true',
        dest='show_hostnames',
        help=_("show hostnames instead of node names"),
    )
    parser_nodes.add_argument(
        "-g",
        "--filter-group",
        default=None,
        dest='filter_group',
        metavar=_("GROUP"),
        required=False,
        type=str,
        help=_("show only nodes in the given group"),
    )
    parser_nodes.add_argument(
        "--groups",
        action='store_true',
        dest='show_groups',
        help=_("show group membership for each node"),
    )
    parser_nodes.add_argument(
        "--os",
        action='store_true',
        dest='show_os',
        help=_("show OS for each node"),
    )

    # bw plot
    help_plot = _("Generates DOT output that can be piped into `dot -Tsvg -ooutput.svg`. "
                  "The resulting output.svg can be viewed using most browsers.")
    parser_plot = subparsers.add_parser("plot", description=help_plot, help=help_plot)
    parser_plot_subparsers = parser_plot.add_subparsers()

    # bw plot group
    help_plot_group = _("Plot subgroups and node members for the given group "
                        "or the entire repository")
    parser_plot_subparsers_group = parser_plot_subparsers.add_parser(
        "group",
        description=help_plot_group,
        help=help_plot_group,
    )
    parser_plot_subparsers_group.set_defaults(func=bw_plot_group)
    parser_plot_subparsers_group.add_argument(
        'group',
        default=None,
        metavar=_("GROUP"),
        nargs='?',
        type=str,
        help=_("group to plot"),
    )
    parser_plot_subparsers_group.add_argument(
        "-N", "--no-nodes",
        action='store_false',
        dest='show_nodes',
        help=_("do not include nodes in output"),
    )

    # bw plot node
    help_plot_node = _("Plot items and their dependencies for the given node")
    parser_plot_subparsers_node = parser_plot_subparsers.add_parser(
        "node",
        description=help_plot_node,
        help=help_plot_node,
    )
    parser_plot_subparsers_node.set_defaults(func=bw_plot_node)
    parser_plot_subparsers_node.add_argument(
        'node',
        metavar=_("NODE"),
        type=str,
        help=_("node to plot"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-cluster",
        action='store_false',
        dest='cluster',
        help=_("do not cluster items by bundle"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-depends-auto",
        action='store_false',
        dest='depends_auto',
        help=_("do not show auto-generated dependencies and items"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-depends-conc",
        action='store_false',
        dest='depends_concurrency',
        help=_("do not show concurrency blocker dependencies"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-depends-regular",
        action='store_false',
        dest='depends_regular',
        help=_("do not show regular user-defined dependencies"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-depends-reverse",
        action='store_false',
        dest='depends_reverse',
        help=_("do not show reverse dependencies ('needed_by')"),
    )
    parser_plot_subparsers_node.add_argument(
        "--no-depends-static",
        action='store_false',
        dest='depends_static',
        help=_("do not show static dependencies"),
    )

    # bw plot groups-for-node
    help_plot_node_groups = _("Show where a specific gets its groups from")
    parser_plot_subparsers_node_groups = parser_plot_subparsers.add_parser(
        "groups-for-node",
        description=help_plot_node_groups,
        help=help_plot_node_groups,
    )
    parser_plot_subparsers_node_groups.set_defaults(func=bw_plot_node_groups)
    parser_plot_subparsers_node_groups.add_argument(
        'node',
        metavar=_("NODE"),
        type=str,
        help=_("node to plot"),
    )

    # bw repo
    help_repo = _("Various subcommands to manipulate your repository")
    parser_repo = subparsers.add_parser("repo", description=help_repo, help=help_repo)
    parser_repo_subparsers = parser_repo.add_subparsers()

    # bw repo bundle
    parser_repo_subparsers_bundle = parser_repo_subparsers.add_parser("bundle")
    parser_repo_subparsers_bundle_subparsers = parser_repo_subparsers_bundle.add_subparsers()

    # bw repo bundle create
    parser_repo_subparsers_bundle_create = \
        parser_repo_subparsers_bundle_subparsers.add_parser("create")
    parser_repo_subparsers_bundle_create.set_defaults(func=bw_repo_bundle_create)
    parser_repo_subparsers_bundle_create.add_argument(
        'bundle',
        metavar=_("BUNDLE"),
        type=str,
        help=_("name of bundle to create"),
    )

    # bw repo create
    parser_repo_subparsers_create = parser_repo_subparsers.add_parser("create")
    parser_repo_subparsers_create.set_defaults(func=bw_repo_create)

    # bw repo plugin
    parser_repo_subparsers_plugin = parser_repo_subparsers.add_parser("plugin")
    parser_repo_subparsers_plugin_subparsers = parser_repo_subparsers_plugin.add_subparsers()

    # bw repo plugin install
    parser_repo_subparsers_plugin_install = parser_repo_subparsers_plugin_subparsers.add_parser("install")
    parser_repo_subparsers_plugin_install.set_defaults(func=bw_repo_plugin_install)
    parser_repo_subparsers_plugin_install.add_argument(
        'plugin',
        metavar=_("PLUGIN_NAME"),
        type=str,
        help=_("name of plugin to install"),
    )
    parser_repo_subparsers_plugin_install.add_argument(
        "-f",
        "--force",
        action='store_true',
        dest='force',
        help=_("overwrite existing files when installing"),
    )

    # bw repo plugin list
    parser_repo_subparsers_plugin_list = parser_repo_subparsers_plugin_subparsers.add_parser("list")
    parser_repo_subparsers_plugin_list.set_defaults(func=bw_repo_plugin_list)

    # bw repo plugin remove
    parser_repo_subparsers_plugin_remove = parser_repo_subparsers_plugin_subparsers.add_parser("remove")
    parser_repo_subparsers_plugin_remove.set_defaults(func=bw_repo_plugin_remove)
    parser_repo_subparsers_plugin_remove.add_argument(
        'plugin',
        metavar=_("PLUGIN_NAME"),
        type=str,
        help=_("name of plugin to remove"),
    )
    parser_repo_subparsers_plugin_remove.add_argument(
        "-f",
        "--force",
        action='store_true',
        dest='force',
        help=_("remove files even if locally modified"),
    )

    # bw repo plugin search
    parser_repo_subparsers_plugin_search = parser_repo_subparsers_plugin_subparsers.add_parser("search")
    parser_repo_subparsers_plugin_search.set_defaults(func=bw_repo_plugin_search)
    parser_repo_subparsers_plugin_search.add_argument(
        'term',
        metavar=_("SEARCH_STRING"),
        nargs='?',
        type=str,
        help=_("look for this string in plugin names and descriptions"),
    )

    # bw repo plugin update
    parser_repo_subparsers_plugin_update = parser_repo_subparsers_plugin_subparsers.add_parser("update")
    parser_repo_subparsers_plugin_update.set_defaults(func=bw_repo_plugin_update)
    parser_repo_subparsers_plugin_update.add_argument(
        'plugin',
        default=None,
        metavar=_("PLUGIN_NAME"),
        nargs='?',
        type=str,
        help=_("name of plugin to update"),
    )
    parser_repo_subparsers_plugin_update.add_argument(
        "-c",
        "--check-only",
        action='store_true',
        dest='check_only',
        help=_("only show what would be updated"),
    )
    parser_repo_subparsers_plugin_update.add_argument(
        "-f",
        "--force",
        action='store_true',
        dest='force',
        help=_("overwrite local modifications when updating"),
    )

    # bw run
    help_run = _("Run a one-off command on a number of nodes")
    parser_run = subparsers.add_parser("run", description=help_run, help=help_run)
    parser_run.set_defaults(func=bw_run)
    parser_run.add_argument(
        'target',
        metavar=_("NODE1,NODE2,GROUP1,bundle:BUNDLE1..."),
        type=str,
        help=_("target nodes, groups and/or bundle selectors"),
    )
    parser_run.add_argument(
        'command',
        metavar=_("COMMAND"),
        type=str,
        help=_("command to run"),
    )
    parser_run.add_argument(
        "-f",
        "--may-fail",
        action='store_true',
        dest='may_fail',
        help=_("ignore non-zero exit codes"),
    )
    parser_run.add_argument(
        "-p",
        "--parallel-nodes",
        default=int(environ.get("BWNODEWORKERS", "1")),
        dest='node_workers',
        help=_("number of nodes to run command on simultaneously"),
        type=int,
    )

    # bw stats
    help_stats = _("Show some statistics about your repository")
    parser_stats = subparsers.add_parser("stats", description=help_stats, help=help_stats)
    parser_stats.set_defaults(func=bw_stats)

    # bw test
    help_test = _("Test your repository for consistency "
                  "(you can use this with a CI tool like Jenkins)")
    parser_test = subparsers.add_parser("test", description=help_test, help=help_test)
    parser_test.set_defaults(func=bw_test)
    parser_test.add_argument(
        'target',
        default=None,
        metavar=_("NODE1,NODE2,GROUP1,bundle:BUNDLE1..."),
        nargs='?',
        type=str,
        help=_("target nodes, groups and/or bundle selectors"),
    )
    parser_test.add_argument(
        "-c",
        "--plugin-conflict-error",
        action='store_true',
        dest='plugin_conflict_error',
        help=_("check for local modifications to files installed by plugins"),
    )
    parser_test.add_argument(
        "-p",
        "--parallel-nodes",
        default=int(environ.get("BWNODEWORKERS", "1")),
        dest='node_workers',
        help=_("number of nodes to test simultaneously"),
        type=int,
    )
    parser_test.add_argument(
        "-P",
        "--parallel-items",
        default=int(environ.get("BWITEMWORKERS", "4")),
        dest='item_workers',
        help=_("number of items to test simultaneously for each node"),
        type=int,
    )

    # bw verify
    help_verify = _("Inspect the health or 'correctness' of a node without changing it")
    parser_verify = subparsers.add_parser("verify", description=help_verify, help=help_verify)
    parser_verify.set_defaults(func=bw_verify)
    parser_verify.add_argument(
        'target',
        metavar=_("NODE1,NODE2,GROUP1,bundle:BUNDLE1..."),
        type=str,
        help=_("target nodes, groups and/or bundle selectors"),
    )
    parser_verify.add_argument(
        "-a",
        "--show-all",
        action='store_true',
        dest='show_all',
        help=_("show correct items as well as incorrect ones"),
    )
    parser_verify.add_argument(
        "-p",
        "--parallel-nodes",
        default=int(environ.get("BWNODEWORKERS", "4")),
        dest='node_workers',
        help=_("number of nodes to verify to simultaneously"),
        type=int,
    )
    parser_verify.add_argument(
        "-P",
        "--parallel-items",
        default=int(environ.get("BWITEMWORKERS", "4")),
        dest='item_workers',
        help=_("number of items to verify to simultaneously on each node"),
        type=int,
    )
    parser_verify.add_argument(
        "-S",
        "---no-summary",
        action='store_false',
        dest='summary',
        help=_("show stats summary"),
    )

    # bw zen
    parser_zen = subparsers.add_parser("zen")
    parser_zen.set_defaults(func=bw_zen)
    return parser
