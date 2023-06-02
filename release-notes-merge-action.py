import argparse
import datetime

from github import Github

parser = argparse.ArgumentParser()
parser.add_argument("--github_token", type=str, help="Github token.", required=True)

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

    server_latest_release = next(
        filter(lambda release: release.prerelease, server_repo.get_releases())
    )

    foobar = server_latest_release.body

    changelog_file = target_repo.get_contents("CHANGELOG.md", ref="main")
    foo = changelog_file.decoded_content.decode("utf-8")
    log_date = datetime.datetime.now().strftime("%m-%d-%Y")

    updated_changelog = """
    # {server_latest_release.tag_name} - [{log_date}]
    
    # Frontend
    
    {frontend_release.body}
    
    # Server
    
    {server_latest_release.body}
    
    # Test
    
    {foo}
    
    """

    # target_repo.update_file("CHANGELOG.md", f"Update CHANGELOG.md for {server_latest_pre_release.tag_name}", updated_changelog, changelog_file.sha, branch="main")

    print(updated_changelog)

    target_release = target_repo.get_latest_release()
    target_release_id = target_release.id

    # target_release.update_release(name="The first test", message=f"{REPO_1}{release1.body}\r\n{REPO_2}{release2.body}")
