"""Scoped, fail-closed Git backup for the portable agent workflow.

Learning operations finish before this helper runs. Failures are returned as
backup outcomes, never rolled back into learning records.
"""
import json
import re
import subprocess

from .contracts import Invalid, require
from .engine import atomic, read_json

PUBLIC_REPOSITORY = "matt-salamone/invo-learn"


def run(ws, *args, ok=(0,)):
    result = subprocess.run(list(args), cwd=ws.root, capture_output=True, text=True, timeout=30)
    require(result.returncode in ok, result.stderr.strip() or f"{args[0]} failed ({result.returncode})")
    return result.stdout.strip()


def git(ws, *args, **kwargs):
    return run(ws, "git", "--literal-pathspecs", *args, **kwargs)


def repository_url(url):
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([\w.-]+/[\w.-]+?)(?:\.git)?/?", url)
    require(match is not None, "Backup supports direct GitHub HTTPS/SSH remotes only")
    repository = match[1].lower()
    require(repository != PUBLIC_REPOSITORY, "Never push learner data to the public harness repository")
    return repository


def verify(ws, remote, repository):
    require(re.fullmatch(r"[\w.-]+/[\w.-]+", repository) is not None, "Expected OWNER/REPO")
    repository = repository.lower()
    require(repository != PUBLIC_REPOSITORY, "Never push learner data to the public harness repository")
    require(git(ws, "rev-parse", "--show-toplevel").lower() == str(ws.root).replace("\\", "/").lower(),
            "Workspace must be the Git repository root")
    require(not git(ws, "config", "--get-regexp", r"^url\.", ok=(0, 1)), "URL rewrites require manual backup review")
    fetch = git(ws, "remote", "get-url", "--all", remote).splitlines()
    push = git(ws, "remote", "get-url", "--push", "--all", remote).splitlines()
    require(len(fetch) == len(push) == 1 and fetch == push, "Remote must have one identical fetch/push destination")
    require(repository_url(push[0]) == repository, "Configured remote does not match the workspace binding")
    info = json.loads(run(ws, "gh", "api", "--hostname", "github.com", "repos/" + repository))
    require(isinstance(info, dict) and isinstance(info.get("permissions"), dict), "Private repository verification returned invalid metadata")
    require(info.get("private") is True and info.get("full_name", "").lower() == repository
            and info.get("permissions", {}).get("push") is True,
            "Cannot verify private repository identity and push access; configure an authenticated private learner remote")
    require(not info.get("fork"), "Learner backup must be an independent repository, not a fork")
    return push[0]


def configure(ws, remote, repository):
    """The agent calls this only for the learner's explicitly identified remote."""
    verify(ws, remote, repository)
    binding = {"workspace_id": ws.state["workspace_id"], "remote": remote, "repository": repository.lower()}
    atomic(ws.root / ".invo-learn/backup-remote.json", binding)
    return {"status": "configured", **binding}


def backup(ws, paths, message, tid=None):
    prefs = ws.effective_preferences(tid) if tid else ws.state["profile"]["preferences"]
    if not prefs.get("auto_backup", True):
        return {"status": "disabled", "local_work_preserved": True}
    commit = None
    try:
        binding_path = ws.root / ".invo-learn/backup-remote.json"
        require(binding_path.exists(), "No verified learner remote. Identify an existing independent private GitHub repository, configure its remote explicitly, then run configure-backup. No remote was created.")
        binding = read_json(binding_path)
        require(binding["workspace_id"] == ws.state["workspace_id"], "Remote belongs to a different workspace binding")
        url = verify(ws, binding["remote"], binding["repository"])
        branch = git(ws, "symbolic-ref", "--short", "HEAD")
        require(branch and not branch.startswith("-"), "Backup requires a named branch")
        scope = set()
        for name in paths:
            path = ws.path(name)
            rel = path.relative_to(ws.root).as_posix()
            require(rel != "." and not path.is_dir(), "List completed files individually, not directories or the whole workspace")
            require(rel != ".git" and not rel.startswith(".git/"), "Cannot back up Git internals")
            require(rel != ".invo-learn/operation.lock", "Cannot commit the operation lock")
            scope.add(rel)
        require(scope, "Explicit completed-file scope required")
        require(not git(ws, "diff", "--cached", "--name-only"), "Existing staged changes need review; backup left the index untouched")
        ref = "refs/heads/" + branch
        remote = git(ws, "ls-remote", url, ref)
        remote_head = remote.split()[0] if remote else None
        head = git(ws, "rev-parse", "--verify", "HEAD", ok=(0, 128))
        if head:
            # A push transmits history too. Check every pending commit, not only
            # the aggregate diff (which could hide reverted unrelated changes).
            pending = git(ws, "rev-list", (remote_head + "..HEAD") if remote_head else "HEAD").splitlines()
            for revision in pending:
                names = git(ws, "diff-tree", "--root", "--no-commit-id", "--name-only", "--no-renames", "-r", "-m", revision).splitlines()
                require(set(names) <= scope, "Unpushed history contains files outside the completed scope; review it before backup")
        git(ws, "add", "--", *sorted(scope))
        if git(ws, "diff", "--cached", "--name-only"):
            git(ws, "commit", "-m", message)
        commit = git(ws, "rev-parse", "--verify", "HEAD")
        if remote_head == commit:
            return {"status": "no-changes", "commit": commit}
        # Reverify visibility immediately before publishing. No force or implicit
        # upstream/refspec selection; one branch goes to one verified destination.
        require(verify(ws, binding["remote"], binding["repository"]) == url, "Remote changed during backup")
        git(ws, "push", "--no-follow-tags", "--recurse-submodules=no", url, "HEAD:" + ref)
        observed = git(ws, "ls-remote", url, ref).split()
        require(observed and observed[0] == commit, "Push returned but remote commit verification failed")
        return {"status": "pushed", "commit": commit, "repository": binding["repository"], "branch": branch}
    except (Invalid, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        return {"status": "backup-failed", "reason": str(exc), "commit": commit,
                "local_work_preserved": True,
                "instruction": "Learning work remains saved locally. Resolve the backup problem and retry the same completed-file scope; do not repeat learning operations."}
