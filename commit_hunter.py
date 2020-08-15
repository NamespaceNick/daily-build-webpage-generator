#!/usr/bin/env python3
# Generate patch notes based on tagged commit messages
# Created by Nicolas Williams, 8/14/2020
from datetime import date
import os
import pickle
from sh.contrib import git


##############################################################################
#################################### NOTES ###################################
##############################################################################
#   * sh.contrib is used instead of sh because it avoids using a pager, which
#       has can cause unintended behavior when parsing the output of a command

# FIXME: Implement behavior for when previous HEAD commit cannot be identified

# TODO: Find a more robust way to store the previous HEAD commit.
#       Using `ledger.txt` is too error prone.

##############################################################################
###################### CONSTANTS & ENVIRONMENT VARIABLES #####################
##############################################################################
WEBSITE_BUILDS_DIR = "/home/studio/studio-website/files/daily-builds"
UNITY_REPO_DIR = "/home/studio/auto-build-devops-testing/test-unity-repo"
LOGFILE = "log_commit_hunter.log"
# Contains the latest commit that was included in previous patch notes
COMMIT_LEDGER = "ledger.txt"

VALID_CATEGORIES = ["bugfix", "feature"]
DATE_FORMAT = "%m_%d_%y"


##############################################################################
################################## FUNCTIONS #################################
##############################################################################


# Create new logfile
# TODO: Increment logfile name and preserve old logfiles instead of overwriting
logfile = open(LOGFILE, "w").close()

# Python class object to represent a git commit
class Commit:
    def __init__(self, category, hash_str, message):
        self.category = category
        self.hash_str = hash_str
        self.message = message
        # self.author = author


# Writes error message to output as well as the logfile
def write_log(log_msg):
    print(fr"{log_msg}")
    logfile = open(LOGFILE, "a")
    logfile.write(log_msg)
    logfile.close()


# Returns a Commit object from a string acquired from the command:
#   `git log --pretty=oneline --abbrev-commit`
# Returns None if string can't be parsed
# TODO: Store commit author
def generate_commit(log_str):
    # Tokenize commit into object
    try:
        commit_hash, category, message = log_str.split(" ", 2)
    except:
        write_log(fr"The following string caused an ERROR: {repr(log_str)}")
        return None

    # Validate commit category
    if category.strip("[]") not in VALID_CATEGORIES:

        message = f"{category} {message}"  # False category is part of message
        category = "Misc"

    return Commit(category.strip("[]"), commit_hash, message)


# Returns the latest commit that has been included in the patch notes
# Returns None if commit file doesn't exist or commit can't be found
# FIXME: More sophisticated error checking to ensure file exists & has content
def get_previous_head_commit():
    try:
        commit_ledger = open(COMMIT_LEDGER, "r")
        latest_commit_hash = commit_ledger.readline().split()[0]
    except:
        write_log(f"ERROR when reading commit ledger")
        return None
    commit_ledger.close()
    return latest_commit_hash


# Updates the latest commit included in the patch notes to be the HEAD commit.
# Should be called at end of script in case of script errors occurring
def update_previous_head_commit():
    # Update the latest noted commit now that patch notes have been created
    latest_patched_commit = git("rev-parse", "--short", "HEAD").rstrip("\n")
    commit_ledger = open(COMMIT_LEDGER, "w")
    commit_ledger.write(latest_patched_commit)
    commit_ledger.close()


##############################################################################
################################### SCRIPT ###################################
##############################################################################

# Set directory of git repo
git = git.bake(_cwd=UNITY_REPO_DIR)


# TODO: Make sure to pull from git repo and ensure it's up-to-date and on
#       the correct branch

# Initialize empty dictionary & keys
neat_commits = {key: [] for key in VALID_CATEGORIES + ["Misc"]}

# Acquire the latest commit that's been included in the patch notes
latest_commit = get_previous_head_commit()

git_log_output = git.log(
    "--pretty=oneline", "--abbrev-commit", f"{latest_commit}..HEAD"
)

# Cancel if there are no new commits
if not git_log_output:
    write_log("No new commits. Cancelling patch notes generation")
    exit(0)

# Populate dictionary to handoff to page generator
for line in git_log_output:
    line = line.rstrip("\n")  # remove trailing newline
    new_commit = generate_commit(line)  # generate commit object
    if new_commit is not None:
        neat_commits[new_commit.category].append(new_commit)

# Get current date to label patch notes
date_tag = date.today().strftime(DATE_FORMAT)

# Create build directory
# FIXME: Handle case where build directory / patch notes already exist (older)
#   ^ Should result in joining old patch notes with new ones
build_dir_abs_path = os.path.join(WEBSITE_BUILDS_DIR, f"build_{date_tag}")
if not (os.path.exists(build_dir_abs_path) and os.path.isdir(build_dir_abs_path)):
    os.makedirs(build_dir_abs_path)


# Serialize patch within relevant build directory
patch_notes = open(
    os.path.join(build_dir_abs_path, f"patch_notes_build_{date_tag}"), "wb"
)
pickle.dump(neat_commits, patch_notes)
patch_notes.close()

update_previous_head_commit()
