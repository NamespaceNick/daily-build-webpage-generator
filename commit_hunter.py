#!/usr/bin/env python3
from datetime import date
import os
import pickle
import re
from sh.contrib import git

# Script for acquiring & serving commit messages based on their type
# (feature, bugfix, improvement, etc)

# CONSTANTS
WEBSITE_BUILDS_DIR = "/home/studio/studio-website/files/daily-builds"
UNITY_REPO_DIR = "/home/studio/auto-build-devops-testing/test-unity-repo"
LOGFILE = "log_commit_hunter.log"
# TODO: Remove VALID_CATEGORIES and just use the values of OUTPUT_LISTS_AND_TAGS
VALID_CATEGORIES = ["bugfix", "feature"]


# IMPORTANT - This dictionary is where you identify how you want commits
#               to be categorized and what their tag will be, respectively.
#               Each key in the below dictionary will have its own key in the
#               output dictionary of this program
#   NOTE: Any commits that cannot be matched to a tag will be tagged 'Misc' and
#           the list containing those commits will be under the key 'Untagged'
# TODO: Maybe remove this constant (after so much commenting, oof)
OUTPUT_LISTS_AND_TAGS = {
    "bugfixes": "bugfix",
    "features": "feature",
}

##############################################################################
#################################### NOTES ###################################
##############################################################################
#   * sh.contrib is used instead of sh because it avoids using a pager, which
#       has can cause unintended behavior when parsing the output of a command


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


# Writes error to output as well as the logfile
def write_error(err_msg):
    print(fr"ERROR: {err_msg}")
    logfile = open(LOGFILE, "a")
    logfile.write(err_msg)
    logfile.close()


# Generates a Commit object from a string acquired from the command:
#   `git log --pretty=oneline --abbrev-commit`
# Returns None if string can't be parsed
# TODO: ERROR CHECKING
# TODO: Store commit author
def generate_commit(log_str):
    # print(f"Commit string: {log_str}")
    # Tokenize commit into object
    try:
        commit_hash, category, message = log_str.split(" ", 2)
    except:
        write_error(fr"The following string caused an ERROR: {repr(log_str)}")
        return None

    # TODO: Handle merge commits

    # Validate commit category
    if category.strip("[]") not in VALID_CATEGORIES:

        message = f"{category} {message}"  # False category is part of message
        category = "Misc"

    return Commit(category.strip("[]"), commit_hash, message)


# Set directory of git repo
git = git.bake(_cwd=UNITY_REPO_DIR)

# Initialize empty dictionary & keys
neat_commits = {key: [] for key in VALID_CATEGORIES + ["Misc"]}

# Populate dictionary to handoff to page generator
for line in git.log("--pretty=oneline", "--abbrev-commit"):
    line = line.rstrip("\n")  # remove trailing newline
    new_commit = generate_commit(line)
    if new_commit is not None:
        neat_commits[new_commit.category].append(new_commit)

# Get current day to label patch notes
date_tag = date.today().strftime("%m_%d_%y")

# Create build directory
# FIXME: Handle case where build directory / patch notes already exist (older)
build_dir_abs_path = os.path.join(WEBSITE_BUILDS_DIR, f"build_{date_tag}")
if not (os.path.exists(build_dir_abs_path) and os.path.isdir(build_dir_abs_path)):
    os.makedirs(build_dir_abs_path)


# Write patch notes to correct build directory
patch_notes = open(
    os.path.join(build_dir_abs_path, f"patch_notes_build_{date_tag}"), "wb"
)
pickle.dump(neat_commits, patch_notes)
patch_notes.close()
