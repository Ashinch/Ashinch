import feedparser
import pathlib
import re
import pytz
import datetime


# Refer from
# https://github.com/tw93/tw93/blob/1793911c450ee25dd170f68160860f4680eed0a6/build_readme.py
def format_time(time_str):
    try:
        if not time_str:
            return None

        print("formatGMTime: " + time_str)
        gmt_format = "%a, %d %b %Y %H:%M:%S %z"
        formatted_time = datetime.datetime.strptime(time_str, gmt_format)
        formatted_time = formatted_time.astimezone(pytz.utc)
        return formatted_time.strftime("%d %b, %Y")

    except ValueError as e:
        print(e)
        return time_str


def fetch_blog_entries():
    entries = feedparser.parse("https://ash7.io/index.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": format_time(entry["published"].split("T")[0] or entry["published"]),
        }
        for entry in entries
    ]


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!-- {} starts -->.*<!-- {} ends -->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


if __name__ == "__main__":
    root = pathlib.Path(__file__).parent.resolve()
    readme = root / "README.md"
    readme_contents: str = readme.open().read()
    blog_entries = fetch_blog_entries()[:5]
    entries_md = "\n".join(
        [
            "<i>{published}</i>&nbsp;&nbsp;<a href='{url}' target='_blank'>{title}</a><br/>".format(
                **entry
            )
            for entry in blog_entries
        ]
    )
    print(entries_md)
    rewritten = replace_chunk(readme_contents, "blog", entries_md)
    readme.open("w").write(rewritten)
