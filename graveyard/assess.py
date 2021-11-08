from app.diffy import EntryList
from graveyard.dpsst_register import DPSSTRegister

import os


def test_count():
    root_dir = "../repo"

    added = {}

    # Added
    for filename in os.listdir(f"{root_dir}/added"):
        reg = DPSSTRegister.open(f"{root_dir}/added/{filename}")
        for group in reg:
            if group.dpsst_num in added:
                added[group.dpsst_num] += 1
            else:
                added.update({group.dpsst_num: 1})

    removed = {}

    # Removed
    for filename in os.listdir(f"{root_dir}/removed"):
        reg = DPSSTRegister.open(f"{root_dir}/removed/{filename}")
        for group in reg:
            if group.dpsst_num in removed:
                removed[group.dpsst_num] += 1
            else:
                removed.update({group.dpsst_num: 1})

    for item in added.items():
        if item[1] > 1:
            print(item)
            print(removed[item[0]])

    print(len(added))
    print(len(removed))


def build_and_diff_dpsst_registers(datecode0, datecode1, directory="repo", log=True, get_diff=True):

    # Load registers
    if log:
        print("Loading registers for differencing...")

    # reg1 = DPSSTRegister.open(f"{directory}/{datecode0}.tsv", log=log)
    # reg2 = DPSSTRegister.open(f"{directory}/{datecode1}.tsv", log=log)

    reg1 = EntryList.open(f"{directory}/{datecode0}.tsv")
    reg2 = EntryList.open(f"{directory}/{datecode1}.tsv")

    # Diff registers
    diff = reg1.diff(reg2, log=log)

    if get_diff:
        return diff

    # Save diff results
    if log:
        print("Saving differenced register...")

    for i in range(2):
        if i == 0:
            diff_type = "-"
        else:
            diff_type = "+"

        with open(f"{directory}/{datecode0}-{datecode1}{diff_type}.tsv", "w+") as f:
            f.write(str(diff[i]))

        if log:
            print(f"Saved {datecode0}-{datecode1}{diff_type}.tsv")


def ppb_finder():

    def get_reg_with_ppb_data(filepath):
        el = EntryList.open(filepath)

        portland_entries = []

        for entry in el:
            if "Portland Police" in entry.agency:
                # print(entry)
                portland_entries.append(entry)

        # print()
        reg = DPSSTRegister()

        for entry in portland_entries:
            reg.add(entry)

        return reg

    reg1 = get_reg_with_ppb_data("../repo/scrape/20190202.tsv")
    reg2 = get_reg_with_ppb_data("../repo/scrape/20200625.tsv")

    reg1.diff(reg2)

    print("PPB removals")
    for group in reg1:
        for entry in group:
            print(entry)

    # with open("repo/ppb_removed_from_20200625_to_20211029.tsv", "w+") as f:
    #     f.write(str(reg1))


def check_for_ppb(diff):
    removed = diff[0]
    added = diff[1]

    print("Added")
    for group in added:
        for entry in group:
            if "Portland Police" in entry.agency:
                print(entry)

    print()

    print("Removed")
    for group in removed:
        for entry in group:
            if "Portland Police" in entry.agency:
                print(entry)

    print()


if __name__ == "__main__":
    # check_for_ppb(build_and_diff_dpsst_registers("20190202", "20200625"))
    # check_for_ppb(build_and_diff_dpsst_registers("20200625", "20211101"))
    diff = build_and_diff_dpsst_registers("20211102", "20211103", get_diff=False)

    # print(diff[0])
    # print()
    # print()
    # print(diff[1])


    # build_and_diff_dpsst_registers("20211101", "20211101-2", get_diff=False)
