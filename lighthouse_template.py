#!/usr/bin/env python3

import json
import sys

from datetime import date
from glob import glob
from os.path import basename
from subprocess import run, CalledProcessError

# The variables below _must_ be modified:

# Home directory for the calling user:
home = "/YOUR/HOME/DIRECTORY"
# Location of local copies of the website pages:
wwwpath = f"{home}/FURTHER/SUBDIRECTORY"
# Page used for google site verification. It will not be tested.
google_verification_html = "YOUR_GOOGLE_VERIFICATION_PAGE.HTML"
# The website in which tests will be run:
website = "URL_FOR_YOUR_WEBSITE"

# The variables below _may_ need to be modified:

# Location of the `lighthouse` executable
lighthouse_exec = f"{home}/.npm-global/bin/lighthouse"
# Location where the lighthouse results will be written to:
output_path = f"{home}/LighthouseReports"
# The suffix to append to the results files:
suffix = date.today().isoformat()


def process_lighthouse_results(results_file):
    with open(results_file) as results_file:
        text = "".join(results_file.readlines())
        json_result = json.loads(text)
        results = {}
        for category, category_results in json_result["categories"].items():
            score = category_results.get("score")
            score = f"{round(score, 2) * 100}%" if score else "N/A"
            results[category] = score
        return results


scores = {}
for page in glob(f"{wwwpath}/*.html"):
    page = basename(page).removesuffix(".html")
    html_file = f"{page}.html"
    if html_file != google_verification_html:
        desktop_output_file = f"{output_path}/lighthouse_desktop_{page}_{suffix}.json"
        desktop_command = f'{lighthouse_exec} \
        --output json --output-path {desktop_output_file} \
        --quiet --preset=desktop --chrome-flags="--headless" \
        {website}/{page}.html'

        mobile_output_file = f"{output_path}/lighthouse_mobile_{page}_{suffix}.json"
        mobile_command = f'{lighthouse_exec} \
        --output json --output-path {mobile_output_file} \
        --quiet --form-factor=mobile --chrome-flags="--headless" \
        {website}/mobile/{page}.html'

        for command in [desktop_command, mobile_command]:
            try:
                run(command, shell=True, check=True, capture_output=True, encoding="utf-8")
            except CalledProcessError as e:
                print(
                    f"ERROR encountered while running `{e.cmd}`: {e.stderr}. Skipping",
                    file=sys.stderr,
                )
                continue

        scores[html_file] = {}
        scores[html_file]["desktop"] = process_lighthouse_results(desktop_output_file)
        scores[html_file]["mobile"] = process_lighthouse_results(mobile_output_file)

# Get the column width for the html page list. Note that '(desktop)' is longer than '(mobile)':
html_column_width = len(max([f"{h} (desktop) " for h in list(scores.keys())], key=len))
# Get the first list of categories that we find. We will verify later that they all match.
categories = list(scores[list(scores.keys())[0]]["desktop"].keys())
# Print the categories as headers. Note that a score with the maximum string length, e.g., 99.5%,
# will be 5 chars long, so we need to pad each header appropriately if it is shorter than that:
headers = [c.ljust(max(5, len(c)), " ") for c in categories]
print(f"{'page'.ljust(html_column_width, ' ')}{' '.join(headers)}")

for html_page, score_groups in scores.items():
    if list(score_groups["desktop"]) != categories:
        print(
            f"ERROR: Unexpected category list for {html_page} (desktop): "
            f"{list(score_groups['desktop'])}. Skipping.",
            file=sys.stderr,
        )
        continue

    if list(score_groups["mobile"]) != categories:
        print(
            f"ERROR: Unexpected category list for {html_page} (mobile): "
            f"{list(score_groups['mobile'])}. Skipping.",
            file=sys.stderr,
        )
        continue

    print(f"{html_page} (desktop)".ljust(html_column_width), end="")
    score_list = []
    for category, score in score_groups["desktop"].items():
        # A score with the maximum string length, e.g., 99.5%, will be 5 chars long.
        score_list.append(f"{score}".ljust(max(5, len(category)), " "))
    print(" ".join(score_list))

    print(f"{html_page} (mobile)".ljust(html_column_width), end="")
    score_list = []
    for category, score in score_groups["mobile"].items():
        # A score with the maximum string length, e.g., 99.5%, will be 5 chars long.
        score_list.append(f"{score}".ljust(max(5, len(category)), " "))
    print(" ".join(score_list))

print()
print(
    f"For more details see the .json files in {output_path}. Category "
    "definitions can be found (in some cases) under "
    "categories[<category_name>]['description']."
)
