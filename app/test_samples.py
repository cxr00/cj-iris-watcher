from diffy import DiffEntryHistory

"""
This file contains example code showing how
to do things with your DiffEntryHistory
"""


def count_active_in_areas(deh):
    output = 0
    areas = ("multnomah", "clackamas")

    # rebuild produces an EntryList, which does not contain differencing information
    entrylist = deh.rebuild(-1)

    for entry in entrylist:
        if entry.status == "Active" and any(area in entry.agency.lower() for area in areas):
            output += 1
    
    return output


if __name__ == "__main__":
    deh = DiffEntryHistory.open("../repo/diff")

    print(count_active_in_areas(deh))
