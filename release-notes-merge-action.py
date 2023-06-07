import argparse
import datetime

import yaml
from github import Github

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
parser.add_argument(
    "--new_frontend_tag",
    type=str,
    help="The new frontend tag to use for the release.",
    required=True,
)
parser.add_argument(
    "--new_frontend_release_title",
    type=str,
    help="The new frontend release title to use for the release.",
    required=True,
)
parser.add_argument(
    "--new_server_tag",
    type=str,
    help="The new server tag to use for the release.",
    required=True,
)
parser.add_argument(
    "--new_server_release_title",
    type=str,
    help="The new server release title to use for the release.",
    required=True,
)

if __name__ == "__main__":
    args = parser.parse_args()

    ORGANIZATION = "music-assistant"
    FRONTEND_REPO = "frontend"
    SERVER_REPO = "server"
    ADDON_REPO = "home-assistant-addon"

    github = Github(args.github_token)

    frontend_repo = github.get_repo(f"{ORGANIZATION}/{FRONTEND_REPO}")
    server_repo = github.get_repo(f"{ORGANIZATION}/{SERVER_REPO}")
    addon_repo = github.get_repo(f"{ORGANIZATION}/{ADDON_REPO}")

    frontend_release = frontend_repo.get_latest_release()

    pre_release_bool = args.pre_release == "true"
    if pre_release_bool:
        server_latest_release = next(
            filter(lambda release: release.prerelease, server_repo.get_releases())
        )
    else:
        server_latest_release = server_repo.get_latest_release()

    if args.new_frontend_tag != frontend_release.tag_name:
        raise ValueError(
            f"Frontend tag: {args.new_frontend_tag} does not match the latest release tag."
        )

    if args.new_server_tag != server_latest_release.tag_name:
        raise ValueError(
            f"Server tag: {args.new_frontend_tag} does not match the latest release tag."
        )

    ref = addon_repo.get_git_ref("heads/main")
    sha = ref.object.sha
    new_branch_name = f"release-{server_latest_release.tag_name}"
    new_branch = addon_repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=sha)

    changelog_file = addon_repo.get_contents(
        "music_assistant_beta/CHANGELOG.md", ref=new_branch_name
    )

    addon_config_file = addon_repo.get_contents(
        "music_assistant_beta/config.yaml", ref=new_branch_name
    )

    existing_changelog_content = changelog_file.decoded_content.decode("utf-8")
    log_date = datetime.datetime.now().strftime("%d.%m.%Y")

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
        branch=new_branch_name,
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
        sha=changelog_file.sha,
        branch=new_branch_name,
    )

    addon_repo.create_pull(
        title=new_branch_name,
        body=f"Update CHANGELOG.md for {server_latest_release.tag_name}",
        head=new_branch_name,
        base="main",
    )
