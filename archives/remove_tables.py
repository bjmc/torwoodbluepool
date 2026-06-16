from bs4 import BeautifulSoup
import argparse

def convert_layout_tables(html):
    soup = BeautifulSoup(html, "lxml")  # more tolerant parser

    for table in soup.find_all("table"):
        # Skip real data tables
        if table.find("th"):
            continue

        wrapper = soup.new_tag("div", **{"class": "table-layout"})

        # Find rows at any depth under table (handles tbody implicitly)
        rows = table.find_all("tr")

        for row in rows:
            row_div = soup.new_tag("div", **{"class": "row"})

            cells = row.find_all(["td", "th"])
            for cell in cells:
                col_div = soup.new_tag("div", **{"class": "cell"})

                # Move children safely
                for child in list(cell.contents):
                    col_div.append(child)

                row_div.append(col_div)

            wrapper.append(row_div)

        table.replace_with(wrapper)

    return str(soup)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('output')
    args = parser.parse_args()

    with open(args.source, "r", encoding="utf-8") as f:
        html = f.read()

    adapted = convert_layout_tables(html)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(adapted)


if __name__ == "__main__":
   main()