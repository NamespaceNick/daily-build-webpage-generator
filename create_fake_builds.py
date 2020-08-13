import os

WEBSITE_DIR = "./website"
DAILY_BUILDS_DIR = "daily-builds"


# create os directories
for daily_build in os.listdir(os.path.join(WEBSITE_DIR, DAILY_BUILDS_DIR)):
    relative_path = os.path.join(WEBSITE_DIR, DAILY_BUILDS_DIR, daily_build)
    os.system(
        f"touch {relative_path}/windows_{daily_build} {relative_path}/mac_{daily_build} {relative_path}/linux_{daily_build}"
    )
