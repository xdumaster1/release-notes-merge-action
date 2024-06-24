import datetime
import os

from github import Auth, Github

MAIN = "main"
ORGANIZATION = "music-assistant"
FRONTEND_REPO = "frontend"
SERVER_REPO = "server"
ADDON_REPO = "home-assistant-addon"
FRONTEND_REPO_PR_MESSAGE = "frontend-"
DEPENDENCIES = "## ⬆️ Dependencies"
WHATS_CHANGED = "## What’s Changed"

github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

frontend_repo = github.get_repo(f"{ORGANIZATION}/{FRONTEND_REPO}")
server_repo = github.get_repo(f"{ORGANIZATION}/{SERVER_REPO}")
addon_repo = github.get_repo(f"{ORGANIZATION}/{ADDON_REPO}")

frontend_release = frontend_repo.get_latest_release()

pre_bool = "True"

pre_release = pre_bool in ("true", "True")

addon_version = "music_assistant"

if pre_release is True:
    server_latest_release = next(
        filter(lambda release: release.prerelease, server_repo.get_releases())
    )
    addon_version = "music_assistant_beta"
else:
    server_latest_release = server_repo.get_latest_release()

changelog_file = addon_repo.get_contents(f"{addon_version}/CHANGELOG.md", ref=MAIN)

addon_config_file = addon_repo.get_contents(f"{addon_version}/config.yaml", ref=MAIN)

existing_changelog_content = changelog_file.decoded_content.decode("utf-8")
log_date = datetime.datetime.now().strftime("%d.%m.%Y")

aggregate_release_notes = server_latest_release.body

if (
    f"{FRONTEND_REPO_PR_MESSAGE}{frontend_release.tag_name}"
    in server_latest_release.body
):
    # If the server release contains a PR message, we need to update the changelog and release notes
    server_split = server_latest_release.body.split(DEPENDENCIES)
    frontend_split = frontend_release.body.split(DEPENDENCIES)

    server_split_formatted = server_split[0].replace(WHATS_CHANGED, "").strip()
    frontend_split_formatted = frontend_split[0].replace(WHATS_CHANGED, "").strip()

    aggregate_release_notes = f"{WHATS_CHANGED}\n\n"
    aggregate_release_notes += f"### Server {server_latest_release.title}\n\n"
    aggregate_release_notes += f"{server_split_formatted}\n\n"
    aggregate_release_notes += f"### Frontend {frontend_release.title}\n\n"
    aggregate_release_notes += f"{frontend_split_formatted}\n\n"
    aggregate_release_notes += f"{DEPENDENCIES}\n\n"
    aggregate_release_notes += "### Server\n\n"
    if len(server_split) > 1:
        aggregate_release_notes += f"{server_split[1].strip()}\n\n"
    aggregate_release_notes += "### Frontend\n\n"
    if len(frontend_split) > 1:
        aggregate_release_notes += f"{frontend_split[1].strip()}\n\n"


updated_changelog = f"# [{server_latest_release.title}] - {log_date}\n\n"
updated_changelog += f"{aggregate_release_notes}\n\n"
# updated_changelog += f"{existing_changelog_content}\n\n"

# If the server release contains a PR message, we need to update the changelog and release notes

print(updated_changelog)
