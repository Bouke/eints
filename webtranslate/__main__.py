import click
import logging

from openttd_helpers import click_helper
from openttd_helpers.logging_helper import click_logging
from openttd_helpers.sentry_helper import click_sentry

from . import bottle
from . import main

log = logging.getLogger(__name__)


@click_helper.command()
@click_logging  # Should always be on top, as it initializes the logging
@click_sentry
@click.option(
    "--server-mode",
    help="Mode of server.",
    type=click.Choice(["development", "production"], case_sensitive=False),
    default="development",
)
@click.option("--server-host", help="Host to bind the server to.", default="127.0.0.1")
@click.option("--server-port", help="Port to bind the server to.", default=8000)
@click.option(
    "--authentication",
    help="Authentication protocol to use.",
    type=click.Choice(["development", "github"], case_sensitive=False),
    default="development",
)
@click.option("--stable-languages", help="Folder with stable languages.", default="stable_languages")
@click.option("--unstable-languages", help="Folder with unstable languages.", default="unstable_languages")
@click.option("--project-root", help="Root folder for data storage.", required=True)
@click.option("--project-cache", help="Number of projects kept in memory LRU cache.", default=1)
@click.option(
    "--project-types",
    help="List of allowed project types.",
    multiple=True,
    type=click.Choice(["newgrf", "game-script", "openttd"], case_sensitive=False),
    default=["newgrf", "game-script"],
)
@click.option(
    "--storage-format",
    help="Storage format for project. "
    "Either one huge file per project, or one folder per project with files per language.",
    type=click.Choice(["one-file", "split-languages"], case_sensitive=False),
    default="one-file",
)
@click.option(
    "--data-format",
    help="Format to store project data in.",
    type=click.Choice(["xml", "json"], case_sensitive=False),
    default="xml",
)
@click.option("--language-file-size", help="Uploads larger than this are rejected.", default=100000)
@click.option("--num-backup-files", help="How many backup files for project data to keep.", default=5)
@click.option("--max-num-changes", help="Length of string history to keep.", default=5)
@click.option("--min-num-changes", help="See docs/manual/setup.rst.", default=2)
@click.option("--change-stable-age", help="See docs/manual/setup.rst.", default=600)
@click.option("--github-organization", help="Organization that contains the GitHub teams.")
@click.option("--github-org-api-token", help="Valid PAT with scope read:org of the organization.")
@click.option("--github-oauth2-client-id", help="Client ID for the GitHub OAuth2 Application.")
@click.option("--github-oauth2-client-secret", help="Client Secret for the GitHub OAuth2 Application.")
@click.option("--translators-password", help="Password for the translators account.")
def run(
    server_mode,
    server_host,
    server_port,
    authentication,
    stable_languages,
    unstable_languages,
    project_root,
    project_cache,
    project_types,
    storage_format,
    data_format,
    language_file_size,
    num_backup_files,
    max_num_changes,
    min_num_changes,
    change_stable_age,
    github_organization,
    github_org_api_token,
    github_oauth2_client_id,
    github_oauth2_client_secret,
    translators_password,
):
    """
    Run the program (it was started from the command line).
    """

    with open("config.xml", "w") as fp:
        fp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        fp.write("<config>\n")

        fp.write(f"  <server-mode>{server_mode}</server-mode>\n")
        fp.write(f"  <server-host>{server_host}</server-host>\n")
        fp.write(f"  <server-port>{server_port}</server-port>\n")
        fp.write(f"  <authentication>{authentication}</authentication>\n")
        fp.write(f"  <stable-languages>{stable_languages}</stable-languages>\n")
        fp.write(f"  <unstable-languages>{unstable_languages}</unstable-languages>\n")
        fp.write(f"  <project-root>{project_root}</project-root>\n")
        fp.write(f"  <project-cache>{project_cache}</project-cache>\n")
        fp.write(f"  <project-types>{' '.join(set(project_types))}</project-types>\n")
        fp.write(f"  <storage-format>{storage_format}</storage-format>\n")
        fp.write(f"  <data-format>{data_format}</data-format>\n")
        fp.write(f"  <language-file-size>{language_file_size}</language-file-size>\n")
        fp.write(f"  <num-backup-files>{num_backup_files}</num-backup-files>\n")
        fp.write(f"  <max-num-changes>{max_num_changes}</max-num-changes>\n")
        fp.write(f"  <min-num-changes>{min_num_changes}</min-num-changes>\n")
        fp.write(f"  <change-stable-age>{change_stable_age}</change-stable-age>\n")

        if authentication == "github":
            fp.write("  <github>\n")
            fp.write(f"    <organization>{github_organization}</organization>\n")
            fp.write(f"    <org-api-token>{github_org_api_token}</org-api-token>\n")
            fp.write(f"    <oauth2-client-id>{github_oauth2_client_id}</oauth2-client-id>\n")
            fp.write(f"    <oauth2-client-secret>{github_oauth2_client_secret}</oauth2-client-secret>\n")
            fp.write(f"    <translators-password>{translators_password or ''}</translators-password>\n")
            fp.write("  </github>\n")

        fp.write("</config>\n")

    log.info("Generated config.xml")

    # Make sure that all files we accept to be transferred, are kept in
    # memory, and only start creating temp-files for files bigger than
    # what we accept. This avoids tons of temp-files during normal operation
    # at the expense of some minor (temporary) increase in memory.
    bottle.BaseRequest.MEMFILE_MAX = language_file_size

    main.run()


if __name__ == "__main__":
    run(auto_envvar_prefix="EINTS")
