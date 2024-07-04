import argparse
import datetime
from github import Auth, Github
from github.GithubException import UnknownObjectException

def parse_arguments():
    parser = argparse.ArgumentParser(description="Update release notes and changelog for a GitHub repository.")
    
    parser.add_argument(
        "--release_tag",
        type=str,
        help="Tag of release just built.",
        required=True,
    )
    parser.add_argument(
        "--github_token",
        type=str,
        help="Github API Access token, NOT the usual Github token.",
        required=True,
    )
    parser.add_argument(
        "--pre_release",
        type=str,
        help="Prerelease boolean.",
        required=True,
    )
    
    return parser.parse_args()

def main():
    args = parse_arguments()

    MAIN = "main"
    ORGANIZATION = "music-assistant"
    REPO_NAME = "home-assistant-addon"
    ADDON_VERSION = "music_assistant"
    WHATS_CHANGED = "## What’s Changed"
    DEPENDENCIES = "## ⬆️ Dependencies"
    
    github = Github(auth=Auth.Token(args.github_token))
    repo = github.get_repo(f"{ORGANIZATION}/{REPO_NAME}")

    pre_release = args.pre_release.lower() == "true"
    release_tag = args.release_tag

    # Fetch the latest release
    try:
        latest_release = repo.get_latest_release()
    except UnknownObjectException:
        print("No latest release found.")
        latest_release = None

    if not latest_release:
        # Handle the case where no latest release is found
        print("No releases found in the repository.")
        return

    # Check if this is a pre-release
    if pre_release:
        try:
            latest_release = next(filter(lambda release: release.prerelease, repo.get_releases()), None)
        except StopIteration:
            print("No pre-release found.")
            latest_release = None
        
        ADDON_VERSION = "music_assistant_beta"

    if not latest_release:
        print("No pre-release found in the repository.")
        return

    # Fetch the changelog and config files
    changelog_file = repo.get_contents(f"{ADDON_VERSION}/CHANGELOG.md", ref=MAIN)
    config_file = repo.get_contents(f"{ADDON_VERSION}/config.yaml", ref=MAIN)

    existing_changelog_content = changelog_file.decoded_content.decode("utf-8")
    log_date = datetime.datetime.now().strftime("%d.%m.%Y")

    # Update the changelog content
    aggregate_release_notes = latest_release.body

    updated_changelog = f"# [{latest_release.title}] - {log_date}\n\n"
    updated_changelog += f"{aggregate_release_notes}\n\n"
    updated_changelog += f"{existing_changelog_content}\n\n"

    # Update the changelog file
    repo.update_file(
        changelog_file.path,
        f"Update changelog for release {release_tag}",
        updated_changelog,
        changelog_file.sha,
        branch=MAIN
    )

    # Optionally update the release notes on GitHub
    latest_release.update_release(
        name=latest_release.title,
        message=aggregate_release_notes,
        prerelease=pre_release,
    )

if __name__ == "__main__":
    main()
