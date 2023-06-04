import argparse
import datetime

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
    target_repo = github.get_repo("jozefKruszynski/release-notes-merge-action")

    frontend_release = frontend_repo.get_latest_release()

    if args.pre_release == "true":
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

    target_release = target_repo.get_latest_release()
    target_release_id = target_release.id

    changelog_file = target_repo.get_contents("CHANGELOG.md", ref="main")
    existing_changelog_content = changelog_file.decoded_content.decode("utf-8")
    log_date = datetime.datetime.now().strftime("%d.%m.%Y")

    updated_changelog = f"# {server_latest_release.tag_name} - [{log_date}]\n\n"
    updated_changelog += "# Frontend\n\n"
    updated_changelog += f"{frontend_release.body}\n\n"
    updated_changelog += "# Server\n\n"
    updated_changelog += f"{server_latest_release.body}\n\n"

    target_release.update_release(name="The first test", message=updated_changelog)

    updated_changelog += f"{existing_changelog_content}\n\n"

    target_repo.update_file(
        "CHANGELOG.md",
        f"Update CHANGELOG.md for {server_latest_release.tag_name}",
        updated_changelog,
        changelog_file.sha,
        branch="main",
    )

    print(updated_changelog)
