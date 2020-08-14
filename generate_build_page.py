# Python script that automatically generates & replaces the builds webpage
# Created by Nico Williams, 8/12/2020
import os
import pickle
import shutil

import jinja2

# NOTES
#   * REQUIRES: daily-builds.html is at the top level of the site directory
#   * This script should be called after all executables & directories for a
#     new build have been made
#   * BUILDS_DIR should point to the directory that contains each of the builds
#   * Each build in BUILDS_DIR should have it's own directory, which should
#     contain one zip file for each OS (Windows, Mac, Linux)

# Directory containing website
WEBSITE_DIR = "/home/studio/studio-website"
# Directory containing daily game builds (path based on website root)
DAILY_BUILDS_DIR = "files/daily-builds"
PLATFORMS = ["windows", "mac", "linux"]


# Python class object to represent a git commit. Required for loading commits
class Commit:
    def __init__(self, category, hash_str, message):
        self.category = category
        self.hash_str = hash_str
        self.message = message


# Returns dictionary of lists of commit messages based on pickled data
def load_pickled_patch_notes(abs_patch_file_path):
    patch_file = open(abs_patch_file_path, "rb")
    commit_dict = pickle.load(patch_file)
    patch_file.close()
    return commit_dict


# Load the template
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "build_page_template.html"
template = templateEnv.get_template(TEMPLATE_FILE)

# Acquire the builds
daily_build_list = []

for build_basename in os.listdir(os.path.join(WEBSITE_DIR, DAILY_BUILDS_DIR)):
    build_path = os.path.join(DAILY_BUILDS_DIR, build_basename)

    # Create daily build object for Jinja template
    daily_build = {
        "name": build_basename,
        "windows": os.path.join(build_path, "windows_" + build_basename),
        "mac": os.path.join(build_path, "mac_" + build_basename),
        "linux": os.path.join(build_path, "linux_" + build_basename),
    }

    # Acquire patch notes dictionary
    patch_notes_path = os.path.join(
        WEBSITE_DIR, build_path, f"patch_notes_{build_basename}"
    )

    # Make sure there are patch notes
    if os.path.exists(patch_notes_path) and os.path.isfile(patch_notes_path):
        patch_notes = load_pickled_patch_notes(patch_notes_path)

        daily_build["features"] = patch_notes["feature"]
        print(daily_build["features"][0])
        daily_build["bugfixes"] = patch_notes["bugfix"]

    daily_build_list.append(daily_build)


# Sort builds by name in descending order
daily_build_list.sort(key=lambda i: i["name"], reverse=True)

# Write template content to new webpage
template_content = template.render(builds=daily_build_list, platforms=PLATFORMS)

# Create & save new webpage file
new_page = open("daily-builds.html", "w+")
new_page.write(template_content)
new_page.close()

# TODO: Verify there weren't any errors?

# Overwrite existing webpage with new one
shutil.move("daily-builds.html", os.path.join(WEBSITE_DIR, "daily-builds.html"))
