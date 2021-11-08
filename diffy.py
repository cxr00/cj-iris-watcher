

class Entry:
    """
    An individual data point from the BPL site
    """

    def __init__(self, data):
        data = data.split("\t")

        self.name = data[0]
        self.id = data[1]

        if len(data) > 2:
            self.agency = data[2]
        else:
            self.agency = ""

        if len(data) > 3:
            # For backwards compatibility's sake
            self.rank = data[3]

            # Not currently used in comparisons but recorded anyway
            self.status = data[4]
        else:
            self.rank = ""
            self.status = ""

    def __eq__(self, other):
        if not isinstance(other, Entry):
            return False
        else:
            return self.name == other.name \
                and self.id == other.id \
                and self.agency == other.agency \
                and self.rank == other.rank

    def __str__(self):
        return "\t".join([self.name, self.id, self.agency, self.rank, self.status])


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

    def __str__(self):
        output = ""
        for entry in self:
            output += str(entry) + "\n"
        return output

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

    def diff(self, other, log=True):
        """
        If self is A and other is B, then:
        A ~ B =
            {a: a in A and a not in B}, which is the removed entries no longer in B
            {b: b in B and b not in A}, which is the newly-added entries now present in B

        In order for differencing to work properly, A must be from the earlier today,
        and B from the later today. Otherwise the results will be reversed
        """
        if not isinstance(other, EntryList):
            raise ValueError(f"Cannot difference {type(other)}, only EntryList")
        else:
            new = []
            if log:
                print("Differencing EntryLists...")
            for entry in other:
                if entry in self:
                    self.data.pop(self.data.index(entry))
                else:
                    new.append(entry)
            if log:
                print("Differencing complete.")
            return [self, EntryList(new)]

    def sum(self, other):
        if not isinstance(other, EntryList):
            raise ValueError(f"Cannot sum {type(other)}, only EntryList")
        else:
            # Beware! This does not deal with duplicates
            for entry in other:
                self.append(entry)


class DiffEntry(Entry):

    def __init__(self, data):
        super().__init__(data[1:])
        self.mode = data[0]

    def __str__(self):
        return self.mode + super().__str__()


class DiffEntryList:

    def __init__(self, diff_entries=None):
        self.diff_entries = []
        if diff_entries:
            for entry in diff_entries:
                if not isinstance(entry, DiffEntry):
                    raise ValueError(f"Incompatible type {type(entry)}, must be DiffEntry")
                else:
                    self.diff_entries.append(entry)

    def __iter__(self):
        return iter(self.diff_entries)

    @staticmethod
    def open(filename):
        data = None
        with open(filename, "r") as f:
            data = f.readlines()

        output = DiffEntryList()
        for line in data:
            output.append(DiffEntry(line.strip()))

        return output

    def append(self, item):
        if not isinstance(item, DiffEntry):
            raise ValueError(f"Incompatible type {type(item)}, must be DiffEntry")
        else:
            self.diff_entries.append(item)

    def added(self):
        output = DiffEntryList()
        for entry in self:
            if entry.mode == "+":
                output.append(entry)
        return output

    def removed(self):
        output = DiffEntryList()
        for entry in self:
            if entry.mode == "-":
                output.append(entry)
        return output

    def ppb(self):
        output = DiffEntryList()
        for entry in self.diff_entries:
            if "Portland Police Bureau" in entry.agency:
                output.append(entry)
        return output

