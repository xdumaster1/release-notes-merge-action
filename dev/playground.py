import datetime

import yaml
import os
from github import Auth, Github


MAIN = "main"
ORGANIZATION = "music-assistant"
FRONTEND_REPO = "frontend"
SERVER_REPO = "server"
ADDON_REPO = "home-assistant-addon"
FRONTEND_REPO_PR_MESSAGE = "Bump frontend to"
DEPENDENCIES = "## ⬆️ Dependencies"
WHATS_CHANGED = "## What’s Changed"

github = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))

frontend_repo = github.get_repo(f"{ORGANIZATION}/{FRONTEND_REPO}")
server_repo = github.get_repo(f"{ORGANIZATION}/{SERVER_REPO}")
addon_repo = github.get_repo(f"{ORGANIZATION}/{ADDON_REPO}")

frontend_release = frontend_repo.get_release("2.0.15")

server_latest_release = server_repo.get_release("2.0.0b73")

server_split = server_latest_release.body.split(DEPENDENCIES)
frontend_split = frontend_release.body.split(DEPENDENCIES)

server_split_formatted = server_split[0].replace(WHATS_CHANGED, "").strip()
frontend_split_formatted = frontend_split[0].replace(WHATS_CHANGED, "").strip()

log_date = datetime.datetime.now().strftime("%d.%m.%Y")

updated_changelog = f"# [{server_latest_release.title}] - {log_date}\n\n"
aggregate_release_notes = f"{WHATS_CHANGED}\n\n"
aggregate_release_notes += f"### Server {server_latest_release.title}\n\n"
aggregate_release_notes += f"{server_split_formatted}\n\n"
aggregate_release_notes += f"### Frontend {frontend_release.title}\n\n"
aggregate_release_notes += f"{frontend_split_formatted}\n\n"
aggregate_release_notes += f"{DEPENDENCIES}\n\n"
aggregate_release_notes += "### Server\n\n"
aggregate_release_notes += f"{server_split[1].strip()}\n\n"
aggregate_release_notes += f"### Frontend\n\n"
aggregate_release_notes += f"{frontend_split[1].strip()}\n\n"

updated_changelog += aggregate_release_notes
# If the server release contains a PR message, we need to update the changelog and release notes

print(updated_changelog)
