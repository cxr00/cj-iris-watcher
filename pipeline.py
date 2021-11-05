from bpl_scraper import scrape_all_data
from diffy import EntryList

import datetime
import os


def generate_filename(directory, datecode0, datecode1, added=True):
    # Friendly filename constructor
    return f"{directory}/{datecode0}-{datecode1}{'+' if added else '-'}.tsv"


def scrape_and_diff_today_from_yesterday():
    # Construct datecodes
    today = datetime.datetime.now()
    day_before = today - datetime.timedelta(days=1)
    datecode0 = day_before.strftime("%Y%m%d")
    datecode1 = today.strftime("%Y%m%d")

    # Scrape from BPL site
    if not os.path.exists(f"repo/scrape/{datecode1}.tsv"):
        print("Scraping data...")
        scrape_all_data(datecode=datecode1, directory="repo/scrape")
    else:
        print("Today's data has already been scraped.")

    # If there isn't already a file for datecode0, ask for an alternate
    # This is rag-tag because
    while not os.path.exists(f"repo/scrape/{datecode0}.tsv"):
        print(f"No file for {datecode0} to measure against.")
        datecode0 = input("Enter an alternate datecode, or leave it empty to exit: ")
        # If input is empty, just leave
        if not datecode0:
            return

    # Get EntryLists for differencing
    el0 = EntryList.open(f"repo/scrape/{datecode0}.tsv")
    el1 = EntryList.open(f"repo/scrape/{datecode1}.tsv")
    diff = el0.diff(el1, log=True)

    print(f"Removed since {datecode0}:")
    print(str(diff[0]))
    print()

    print(f"Added to {datecode1}:")
    print(str(diff[1]))

    addition_file = generate_filename("repo/added", datecode0, datecode1, True)
    removal_file = generate_filename("repo/removed", datecode0, datecode1, False)

    # Always overwrite, it's fine since we're not always scraping
    with open(removal_file, "w+") as f:
        f.write(str(diff[0]))

    print(f"Saved removals to {removal_file}")

    with open(addition_file, "w+") as f:
        f.write(str(diff[1]))

    print(f"Saved additions to {addition_file}")


if __name__ == "__main__":
    scrape_and_diff_today_from_yesterday()
