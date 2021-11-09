from bpl_scraper import scrape_all_data
from diffy import EntryList, DiffEntryHistory

import datetime
import os


def scrape_and_diff_today_from_yesterday():
    # Construct datecodes
    today = datetime.datetime.now()

    # Get previous day from _meta file
    with open(f"repo/diff/_meta.txt", "r") as f:
        datecode0 = f.readlines()[-1].strip()

    datecode1 = today.strftime("%Y%m%d")

    if datecode0 == datecode1:
        print("Data already recorded according to meta")
        return

    # Scrape from BPL site
    if not os.path.exists(f"repo/scrape/{datecode1}.tsv"):
        print("Scraping data...")
        scrape_all_data(datecode=datecode1, directory="repo/scrape")
    else:
        print("Today's data has already been scraped.")

    # Get EntryLists for differencing
    el0 = DiffEntryHistory.open(f"repo/diff").rebuild()
    el1 = EntryList.open(f"repo/scrape/{datecode1}.tsv")
    diff = el0.diff(el1, log=True)

    print(f"Removed since {datecode0[4:6]}/{datecode0[6:]}/{datecode0[:4]} (-):")
    print(str(diff[0]))
    print()

    print(f"Added to {datecode1[4:6]}/{datecode1[6:]}/{datecode1[:4]} (+):")
    print(str(diff[1]))

    diff_file = f"repo/diff/{datecode0}-{datecode1}.tsv"

    report_string = ""

    for entry in diff[0]:
        report_string += "-" + str(entry) + "\n"

    for entry in diff[1]:
        report_string += "+" + str(entry) + "\n"

    with open(diff_file, "w+") as f:
        f.write(report_string)

    print(f"Difference saved to {diff_file}")

    # Update diff _meta file with new day
    with open(f"repo/diff/_meta.txt", "a+") as f:
        f.write(datecode1 + "\n")

    print(f"Meta file updated with {datecode1}")


def delete_old_tsv():
    """
    Deletes TSV files that are no longer necessary thanks to differencing

    Hangs on to the past couple days just in case
    """
    def create_filename(datecode0, datecode1):
        return f"repo/diff/{datecode0}-{datecode1}.tsv"

    eh = DiffEntryHistory.open("repo/diff")

    for n in range(1, len(eh.meta) - 2):
        diff_filename = create_filename(eh.meta[n-1], eh.meta[n])
        if os.path.exists(diff_filename):
            del_filename = f"repo/scrape/{eh.meta[n]}.tsv"
            if os.path.exists(del_filename):
                print(f"Deleting old TSV for {eh.meta[n]}")
                os.remove(del_filename)


if __name__ == "__main__":
    scrape_and_diff_today_from_yesterday()
    delete_old_tsv()
