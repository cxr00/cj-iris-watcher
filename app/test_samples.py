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


def count_active_dispatchers(deh):
    output = 0

    entrylist = deh.rebuild(-1)

    for entry in entrylist:
        if entry.rank.lower() == "dispatcher" and entry.status == "Active":
            output += 1

    return output


def count_inactive(deh):
    output = 0
    names = []

    entrylist = deh.rebuild(-1)

    for entry in entrylist:
        if entry.status == "Inactive" and entry.name not in names:
            output += 1
            names.append(entry.name)

    return output


def test_rebuild_with_datecode_argument(deh):

    el0 = deh.root

    el1 = deh.rebuild(datecode="20211111")

    print(len(el0))
    print(len(el1))


if __name__ == "__main__":
    deh = DiffEntryHistory.open("../repo/diff")

    print(test_rebuild_with_datecode_argument(deh))
