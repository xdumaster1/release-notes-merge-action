import argparse
import datetime

import yaml
import marko
from github import Auth, Github

parser = argparse.ArgumentParser()

parser.add_argument(
    "--pre_release",
    type=str,
    help="Whether or not this is a pre-release.",
    required=True,
)
parser.add_argument(
    "--github_token",
    type=str,
    help="Github API Access token, NOT the usual Github token.",
    required=True,
) 

if __name__ == "__main__":
    args = parser.parse_args()

    MAIN = "main"
    ORGANIZATION = "music-assistant"
    FRONTEND_REPO = "frontend"
    SERVER_REPO = "server"
    ADDON_REPO = "home-assistant-addon"
    FRONTEND_REPO_PR_MESSAGE = "Update files for"

    github = Github(auth=Auth.Token(args.github_token))

    frontend_repo = github.get_repo(f"{ORGANIZATION}/{FRONTEND_REPO}")
    server_repo = github.get_repo(f"{ORGANIZATION}/{SERVER_REPO}")
    addon_repo = github.get_repo(f"{ORGANIZATION}/{ADDON_REPO}")

    frontend_release = frontend_repo.get_latest_release()

    pre_release_bool = args.pre_release
    if pre_release_bool:
        server_latest_release = next(
            filter(lambda release: release.prerelease, server_repo.get_releases())
        )
    else:
        server_latest_release = server_repo.get_latest_release()

    changelog_file = addon_repo.get_contents(
        "music_assistant_beta/CHANGELOG.md", ref=MAIN
    )

    addon_config_file = addon_repo.get_contents(
        "music_assistant_beta/config.yaml", ref=MAIN
    )

    existing_changelog_content = changelog_file.decoded_content.decode("utf-8")
    log_date = datetime.datetime.now().strftime("%d.%m.%Y")


    if FRONTEND_REPO_PR_MESSAGE in server_latest_release.body:
        # If the server release contains a PR message, we need to update the changelog and release notes
        aggregate_release_notes = f"## Frontend {frontend_release.title}\n\n"
        aggregate_release_notes += f"{frontend_release.body}\n\n"
        aggregate_release_notes += f"## Server {server_latest_release.title}\n\n"
        aggregate_release_notes += f"{server_latest_release.body}\n\n"


        server_latest_release.update_release(
            name=server_latest_release.title,
            message=aggregate_release_notes,
            prerelease=pre_release_bool,
        )

    updated_changelog = f"# [{server_latest_release.title}] - {log_date}\n\n"
    updated_changelog += f"{aggregate_release_notes}"
    updated_changelog += f"{existing_changelog_content}\n\n"

    addon_repo.update_file(
        path="music_assistant_beta/CHANGELOG.md",
        message=f"Update CHANGELOG.md for {server_latest_release.tag_name}",
        content=updated_changelog,
        sha=changelog_file.sha,
        branch=MAIN,
    )

    existing_config_content = yaml.safe_load(
        addon_config_file.decoded_content.decode("utf-8")
    )

    existing_config_content["version"] = server_latest_release.tag_name

    updated_config = yaml.dump(existing_config_content)

    addon_repo.update_file(
        path="music_assistant_beta/config.yaml",
        message=f"Update config.yaml for {server_latest_release.tag_name}",
        content=updated_config,
        sha=addon_config_file.sha,
        branch=MAIN,
    )
