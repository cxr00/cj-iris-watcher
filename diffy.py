

class Entry:

    def __init__(self, data):
        data = data.split("\t")
        self.name = data[0]
        self.id = data[1]
        self.agency = data[2]

        if len(data) > 3:
            # For backwards compatibility's sake
            self.rank = data[3]

            # Not currently used in comparisons but recorded anyway
            self.status = data[4]

            self.version = "new"
        else:
            self.version = "old"

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        else:
            if other.version == "new":
                # Do all parts match?
                # Not including status because it's not really relevant and is bugged
                return self.name == other.name \
                    and self.id == other.id \
                    and self.agency == other.agency \
                    and self.rank == other.rank
            else:
                return self.name == other.name \
                    and self.id == other.id \
                    and self.agency == other.agency

    def __str__(self):
        if self.version == "new":
            return "\t".join([self.name, self.id, self.agency, self.rank, self.status])
        else:
            return "\t".join([self.name, self.id, self.agency])


class EntryList:

    def __init__(self, data=None):
        self.data = []
        if data:
            for each in data:
                if isinstance(each, Entry):
                    self.data.append(each)
                else:
                    raise ValueError("Can only add Entries to EntryList")

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    @staticmethod
    def open(filepath):
        entries = []
        with open(filepath, "r") as f:
            lines = f.readlines()
            for line in lines:
                entries.append(Entry(line[:-1]))
        return EntryList(entries)

    def append(self, item):
        if isinstance(item, Entry):
            self.data.append(item)
        else:
            raise ValueError("Can only add Entries to EntryList")

    def diff(self, other):
        """
        The goal of diff is to remove the other given if it is present

        If self is A and other is B, then:
        A ~ B =
            {a: a in A and a not in B}, (0) which is the removed entries
            {b: b in B and b not in A}  (1) which is the newly-added entries

        The original EntryList becomes A ~ B (0) , and A ~ B (1) is returned
        """
        if isinstance(other, Entry):
            if other in self.data:
                print(f"{other.name} found")
                return self.data.pop(self.data.index(other))
            else:
                print(f"{other.name} not found")
                return None
        elif isinstance(other, EntryList):
            not_found = []
            for entry in other:
                n = self.diff(entry)
                if not n:
                    not_found.append(entry)

            # The newly-added entries according to the differ
            return not_found


def generate_diff_test(datecode0, datecode1):
    pre_list = EntryList.open(f"coplist_tsv/{datecode0}.tsv")
    post_list = EntryList.open(f"coplist_tsv/{datecode1}.tsv")

    print(len(pre_list))
    print(len(post_list))
    print()

    not_found = pre_list.diff(post_list)

    print(len(pre_list))
    print(len(not_found))
    print()

    # Save diff'd data
    with open(f"coplist_tsv/diff-{datecode0}-{datecode1}.tsv", "w+") as f:
        for entry in pre_list:
            f.write(str(entry) + "\n")

    with open(f"coplist_tsv/new-{datecode0}-{datecode1}.tsv", "w+") as f:
        for entry in not_found:
            f.write(str(entry) + "\n")


if __name__ == "__main__":
    generate_diff_test("20200625", "20211029")

