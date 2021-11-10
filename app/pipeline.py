from bpl_scraper import scrape_all_data
from diffy import EntryList, DiffEntryHistory

import datetime
import os


def scrape_and_diff_today_from_yesterday(directory=None):
    # Construct datecodes
    today = datetime.datetime.now()

    if not directory:
        directory = "repo"

    # Get previous day from _meta file
    with open(f"{directory}/diff/_meta.txt", "r") as f:
        datecode0 = f.readlines()[-1].strip()

    datecode1 = today.strftime("%Y%m%d")

    if datecode0 == datecode1:
        print("Data already recorded according to meta")
        return

    # Scrape from BPL site
    if not os.path.exists(f"{directory}/scrape/{datecode1}.tsv"):
        print("Scraping data...")
        scrape_all_data(datecode=datecode1, directory="repo/scrape")
    else:
        print("Today's data has already been scraped.")

    # Get EntryLists for differencing
    el0 = DiffEntryHistory.open(f"{directory}/diff").rebuild()
    el1 = EntryList.open(f"{directory}/scrape/{datecode1}.tsv")
    diff = el0.diff(el1, log=True)

    print(f"Removed since {datecode0[4:6]}/{datecode0[6:]}/{datecode0[:4]} (-):")
    print(str(diff[0]))
    print()

    print(f"Added to {datecode1[4:6]}/{datecode1[6:]}/{datecode1[:4]} (+):")
    print(str(diff[1]))

    diff_file = f"{directory}/diff/{datecode0}-{datecode1}.tsv"

    report_string = ""

    for entry in diff[0]:
        report_string += "-" + str(entry) + "\n"

    for entry in diff[1]:
        report_string += "+" + str(entry) + "\n"

    with open(diff_file, "w+") as f:
        f.write(report_string)

    print(f"Difference saved to {diff_file}")

    # Update diff _meta file with new day
    with open(f"{directory}/diff/_meta.txt", "a+") as f:
        f.write(datecode1 + "\n")

    print(f"Meta file updated with {datecode1}")


def delete_old_tsv(directory=None):
    """
    Deletes TSV files that are no longer necessary thanks to differencing

    Hangs on to the past couple days just in case
    """
    def create_filename(datecode0, datecode1):
        return f"repo/diff/{datecode0}-{datecode1}.tsv"

    if not directory:
        directory = "repo"

    eh = DiffEntryHistory.open(f"{directory}/diff")

    for n in range(1, len(eh.meta) - 2):
        diff_filename = create_filename(eh.meta[n-1], eh.meta[n])
        if os.path.exists(diff_filename):
            del_filename = f"{directory}/scrape/{eh.meta[n]}.tsv"
            if os.path.exists(del_filename):
                print(f"Deleting old TSV for {eh.meta[n]}")
                os.remove(del_filename)


def test_partial_rebuilds(directory=None):
    if not directory:
        directory = "repo"

    diff_eh = DiffEntryHistory.open(f"{directory}/diff")

    el0 = diff_eh.rebuild(n=0)
    el1 = diff_eh.rebuild(n=1)

    el2 = el0.diff(el1)
    print(el2[0])
    print()
    print(el2[1])
    print()


def test_history_slicing(directory=None):
    if not directory:
        directory = "repo"

    diff_eh = DiffEntryHistory.open(f"{directory}/diff")

    print("\n".join(diff_eh.meta) + "\n")

    d = diff_eh[2].diff(diff_eh[3])

    print(d[0])
    print(d[1])
    print()

    d = diff_eh[1:][1].diff(diff_eh[1:][2])

    print(d[0])
    print(d[1])
    print()


if __name__ == "__main__":
    scrape_and_diff_today_from_yesterday()
    delete_old_tsv()
