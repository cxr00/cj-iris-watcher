

class Entry:
    """
    An individual data point from the BPL site
    """

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


class DPSSTGroup:
    """
    A DPSSTGroup is an EntryList with an associated DPSST number and name
    """

    def __init__(self, dpsst_num: str, entries=None):
        self.dpsst_num = dpsst_num
        self.name = None
        if entries:
            self.entries = EntryList()
            for entry in entries:
                if entry.id == self.dpsst_num:
                    self.entries.append(entry)
                    if not self.name:
                        self.name = entry.name
                else:
                    raise ValueError(f"Cannot add entry to DPSST #{self.dpsst_num} because entry's DPSST # is {entry.id}")

    def __iter__(self):
        return iter(self.entries)

    def __str__(self):
        return self.name + "\t" + self.dpsst_num

    def append(self, entry: Entry):
        if entry.id == self.dpsst_num:
            self.entries.append(entry)
            if not self.name:
                self.name = entry.name
        else:
            raise ValueError(f"Cannot add entry to DPSST #{self.dpsst_num} because entry's DPSST # is {entry.id}")


class DPSSTRegister:
    """
    A DPSSTRegister is a collection of DPSSTGroups. These can be differenced to
    detect additions and removals from the database
    """

    def __init__(self, dpsst_groups=None):
        self.groups = []
        if dpsst_groups:
            for group in dpsst_groups:
                if isinstance(group, DPSSTGroup):
                    self.groups.append(group)
                else:
                    raise ValueError("Can only add DPSSTGroup to Register")

    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)

    def __str__(self):
        output = ""
        for each in self:
            output += str(each) + "\n"
        return output

    @staticmethod
    def open(filename, log=True):
        if log:
            print(f"Loading EntryList into DPSSTRegister from {filename}...")
        e = EntryList.open(filename)
        output = DPSSTRegister()

        prev_char = None

        for entry in e:
            char = entry.name[0].lower()
            if prev_char != char and log:
                print(f"Adding entries beginning with {char}...")
            output.add(entry)
            prev_char = char.lower()

        if log:
            print("DPSSTRegister constructed.")

        return output

    def add(self, entry: Entry):
        g = self.get(entry.id)
        if g:
            g.append(entry)
        else:
            self.groups.append(DPSSTGroup(entry.id, [entry]))

    def diff(self, other):
        """
        If self is A and other is B, then:
        A ~ B =
            {a: a in A and a not in B}, which is the removed entries no longer in B
            {b: b in B and b not in A}, which is the newly-added entries now present in B

        In order for differencing to work properly, A must be from the earlier time,
        and B from the later time. Otherwise the results will be reversed
        """
        new = []
        for other_group in other:
            found = False
            for self_group in self:
                # Only checks for the matching DPSST number, not matching entries
                if other_group.dpsst_num == self_group.dpsst_num:
                    self.groups.pop(self.groups.index(self_group))
                    found = True
                    break
            if not found:
                new.append(other_group)
        return [self, DPSSTRegister(new)]

    def get(self, dpsst_num):
        for each in self:
            if each.dpsst_num == dpsst_num:
                return each

        return None


def build_and_diff_dpsst_registers(datecode0, datecode1):

    # Load registers
    reg1 = DPSSTRegister.open(f"coplist_tsv/{datecode0}.tsv")
    reg2 = DPSSTRegister.open(f"coplist_tsv/{datecode1}.tsv")

    # Diff registers
    diff = reg1.diff(reg2)

    # Save diff results
    for i in range(2):
        if i == 0:
            diff_type = "removed"
        else:
            diff_type = "added"
        with open(f"coplist_tsv/{datecode0}-{datecode1}-{diff_type}.txt", "w+") as f:
            f.write(str(diff[i]))


if __name__ == "__main__":
    build_and_diff_dpsst_registers("20211029", "20211030")
