from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time
import re
import os

# The namesake of the scraper
bpl_url = "https://www.bpl-orsnapshot.net/PublicInquiry_CJ/EmployeeSearch.aspx"


def trim_left(html, phrase):
    # Get rid of everything before the table starts
    line_number = 0

    lines = str(html).split("\n")
    for line in lines:
        if phrase in line:
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


def go_to_previous_page(driver):
    # Get the part of the page that has page numbers
    trimmed_html = trim_left(driver.page_source, "ListFooter")

    try:
        # If there are multiple pages, this will get the highlighted one
        current_page = int(trimmed_html[3].split("<span>")[1].split("</span>")[0])
    except IndexError:
        # There is only one page
        return False

    # Ellipsis indicates a page that has different link text and may be the next page
    elements = driver.find_elements(By.LINK_TEXT, "...")

    for element in elements:
        # Pull the page number from the link text
        href = element.get_attribute("href")
        m = re.search(r"Page\$[0-9]*", href)
        if m:
            ellipsis_page = int(m.group(0)[5:])
            if ellipsis_page == current_page - 1:
                # This is the next page
                element.send_keys(Keys.RETURN)
                return True

    try:
        # Simply try to get the previous page
        element = driver.find_element(By.LINK_TEXT, str(current_page - 1))
        element.send_keys(Keys.RETURN)
        return True
    except NoSuchElementException:
        # No such page exists
        return False


def go_to_next_page(driver):
    """
    Instruct the webdriver to find and go to the next page if one exists.

    return: Whether this action succeeded
    """

    # Get the part of the page that has page numbers
    trimmed_html = trim_left(driver.page_source, "ListFooter")

    try:
        # If there are multiple pages, this will get the highlighted one
        current_page = int(trimmed_html[3].split("<span>")[1].split("</span>")[0])
    except IndexError:
        # There is only one page
        return False

    # Ellipsis indicates a page that has different link text and may be the next page
    elements = driver.find_elements(By.LINK_TEXT, "...")

    found = False

    for element in elements:
        # Pull the page number from the link text
        href = element.get_attribute("href")
        m = re.search(r"Page\$[0-9]*", href)
        if m:
            ellipsis_page = int(m.group(0)[5:])
            if ellipsis_page == current_page + 1:
                # This is the next page
                element.send_keys(Keys.RETURN)
                return True

    if not found:
        try:
            # Simply try to get the next page
            element = driver.find_element(By.LINK_TEXT, str(current_page + 1))
            element.send_keys(Keys.RETURN)
            return True
        except NoSuchElementException:
            # No such page exists
            return False


def scrape_from_all_pages(driver, search_term):
    """
    Collect entries from every page of the search result
    """

    # Put search term into search bar and enter
    search_bar = driver.find_element(By.ID, "txtNameSearch")
    search_bar.clear()
    search_bar.send_keys(search_term)
    search_bar.send_keys(Keys.RETURN)

    # Ensure we're on the first page (what a weird bug)
    while go_to_previous_page(driver):
        pass

    trimmed_html = trim_left(driver.page_source, "ListTableAnyHeight")

    entries = []

    current_page = 1
    while True:

        # Loop variables
        marked_line = 0
        to_add = []

        if current_page > 1:
            if not go_to_next_page(driver):
                # No more pages exist to harvest
                break
            else:
                # Next page is ready to be harvested and trimmed
                trimmed_html = trim_left(driver.page_source, "ListTableAnyHeight")

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
                entries.append(to_add)
                to_add = []

        current_page += 1

    return entries


def scrape_all_data(datecode=None, directory=None, overwrite=False):
    """
    Systematically collect and save the data from each search result, resulting
    in a complete set of the day's data

    :param datecode: To be used to generate the filename
    :param directory: To be used to generate the filename
    :param overwrite: If the generated file already exists, determine whether to overwrite it
    """

    # If called without arguments, no harm done
    if not datecode:
        return

    if directory and not os.path.isdir(directory):
        os.mkdir(directory)

    if directory:
        filename = f"{directory}/{datecode}.tsv"
    else:
        filename = f"{datecode}.tsv"

    # If it already exists, try to overwrite it
    # I'll be careful, I promise
    if os.path.exists(filename):
        if overwrite:
            with open(filename, "w"):
                pass
        else:
            print(f"Won't overwrite existing file {filename}")
            return

    letter_combos = [chr(i) + chr(j) for i in range(97, 123) for j in range(97, 123)]

    options = Options()
    options.headless = True

    # If your driver is in a different place, change this
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    driver.get(bpl_url)

    # Create TSV folder if one doesn't exist
    if not os.path.isdir(directory):
        os.mkdir(directory)

    for search_term in letter_combos:
        entries = scrape_from_all_pages(driver, search_term)

        # Only bother if there are actually entries
        if entries:
            with open(filename, "a+") as f:
                for entry in entries:
                    print(entry)
                    f.write("\t".join(entry) + "\n")
        else:
            print(f"No entries for {search_term}")

    driver.close()
