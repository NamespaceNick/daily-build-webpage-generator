# Python script that automatically generates & replaces the builds webpage
# Created by Nico Williams, 8/12/2020
import os
import shutil

import jinja2

# NOTES
#   * This script should be called after all executables & directories for a
#     new build have been made
#   * BUILDS_DIR should point to the directory that contains each of the builds
#   * Each build in BUILDS_DIR should have it's own directory, which should
#     contain one zip file for each OS (Windows, Mac, Linux)

# Directory containing website
WEBSITE_DIR = "./website"
# Directory containing daily game builds (path based on website root)
DAILY_BUILDS_DIR = "daily-builds"
PLATFORMS = ["windows", "mac", "linux"]


# Load the template
templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader)
TEMPLATE_FILE = "template.html"
template = templateEnv.get_template(TEMPLATE_FILE)

# Acquire the builds
daily_build_list = []

for build_basename in os.listdir(os.path.join(WEBSITE_DIR, DAILY_BUILDS_DIR)):
    build_path = os.path.join(DAILY_BUILDS_DIR, build_basename)
    daily_build = {
        "name": build_basename,
        "path": build_path,
        "windows": os.path.join(build_path, "windows_" + build_basename),
        "mac": os.path.join(build_path, "mac_" + build_basename),
        "linux": os.path.join(build_path, "linux_" + build_basename),
    }
    daily_build_list.append(daily_build)


# Sort builds by name in descending order
daily_build_list.sort(key=lambda i: i["name"], reverse=True)

# Write template content to new webpage
template_content = template.render(builds=daily_build_list, platforms=PLATFORMS)

# Create & save new webpage file
new_page = open("new_page.html", "w+")
new_page.write(template_content)
new_page.close()

# TODO: Verify there weren't any errors?

# Overwrite existing webpage with new one
shutil.copyfile("new_page.html", "website/index.html")
