import mechanize

bpl_url = "https://www.bpl-orsnapshot.net/PublicInquiry_CJ/EmployeeSearch.aspx"


def trim_left(html):
    # Get rid of everything before the table starts
    line_number = 0

    lines = str(html).split("\n")
    for line in lines:
        if "ListTableAnyHeight" in line:
            line_number = lines.index(line)
            break

    return lines[line_number:]


def pull_name_and_such_from_line(line):
    # Grabs 3 of the 5 data points
    spl = line.split(">")
    name = spl[2][:-3].strip()
    dpsst_num = spl[5][:-4].strip()
    dept = spl[8][:-3].strip()
    return [name, dpsst_num, dept]


def pull_singleton_from_line(line):
    # Grabs 1 of the 5 data points, on two separate occasions
    spl = line.split(">")
    rank = spl[1][:-6].strip()
    return rank


def search_with_mechanize(search_term, search_option="0", log=True):

    # Browse the site
    if log:
        print("Creating and opening browser...")
    b = mechanize.Browser()
    b.open(bpl_url)

    # Form selection
    b.select_form(nr=0)
    form = b.forms()[0]

    if log:
        print("Setting form values...")

    # Change form text box value
    form.find_control("txtNameSearch").value = search_term

    # Change radio bubble value to DPSST number
    form.find_control("rdoSearchOption").value = [search_option]



    if log:
        print("Sending request...")

    # Create the request and send it
    click = mechanize.urlopen(b.click(id="cmdSearch"))

    print("b.open(b.click())", b.open(b.click(id="cmdSearch")))

    print(b.links())

    link = b.find_link("2")
    print(link)
    request = b.click_link(link)
    print(request)
    b.open(request)
    print(b)

    entries = []
    last_page_found = False

    while not last_page_found:

        if log:
            print("Decoding bytes...")

        # Decode
        html = click.read().decode("utf-8")

        # Get rid of everything before the main table
        trimmed_html = trim_left(html)

        if log:
            print("Scraping search data...")
            print("\n".join(trimmed_html))

        # Loop variables
        marked_line = 0
        to_add = []

        for line in trimmed_html:

            # Find second and third lines with entry info
            if 1 <= marked_line <= 3:

                # As it happens only the 1st and 3rd lines are taken
                if marked_line % 2:
                    to_add.append(pull_singleton_from_line(line))

                marked_line = (marked_line + 1) % 4

            # Find first line with entry info
            if "align=\"left\"" in line:
                to_add += pull_name_and_such_from_line(line)
                marked_line = 1

            # If a new to_add has finished being constructed
            if marked_line == 0 and to_add:
                if to_add in entries:
                    last_page_found = True
                else:
                    entries.append(to_add)
                    to_add = []

    print(b.forms()[0])

    if not entries:
        print(f"No entries for {search_term}")
    for entry in entries:
        print(entry)

    return entries


def get_all_with_mechanize(datecode):

    # All possible two-letter permutations
    letter_combos = [chr(i) + chr(j) for i in range(97, 123) for j in range(97, 123)]

    for letter_combo in letter_combos:
        # Access the search form
        entries = search_with_mechanize(letter_combo)

        # Save the collected entries
        with open(f"{datecode}.tsv", "a+") as f:
            for entry in entries:
                f.write("\t".join(entry) + "\n")


def load_test_1():

    datecode = "20211029"

    entries = []
    with open(f"{datecode}.tsv", "r") as f:
        lines = f.readlines()
        for line in lines:
            entries.append(line[:-1].split("\t"))

    for entry in entries:
        print(entry)

    print(len(entries))


if __name__ == "__main__":
    entries = search_with_mechanize("smith", log=False)
