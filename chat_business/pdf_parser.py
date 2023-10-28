import fitz
import re
from collections import OrderedDict


class Paper:
    def __init__(self, path, jcode, title=None):
        self.path = path  # pdf路径

        from .parse_template import (
            get_filter_by_jcode,
            text_replace,
            exclude_chapter_name,
        )

        f = get_filter_by_jcode(jcode)
        self.start_page = f["start_page"]

        self.filters = f["filters"]

        self.text_replace = text_replace
        self.exclude_chapter_name = exclude_chapter_name

        self.initial_chapter_name = "Initial"

        if title:
            self.title = title
        else:
            self.title = self.get_title()

        self.chapter_text_dict = self.parse_pdf()
        self.chapters = self.get_chapters()
        self.num2chapter = self.mark_chapter()

    def clean_text(self, text):
        for r in self.text_replace:
            text = re.sub(r, self.text_replace[r], text)

        text = text.strip()
        return text

    def get_title(self):
        if "title" not in self.filters:
            return None

        doc = fitz.open(self.path)  # pdf文档

        page = doc.load_page(self.start_page)

        blocks = page.get_text("dict")["blocks"]

        title = ""
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        for f in self.filters["title"]:
                            if f(s):
                                title += " " + s["text"]
        if title:
            return self.clean_text(title)
        else:
            return None

    def get_chapters(self):
        chapters = OrderedDict()
        keys = list(self.chapter_text_dict.keys())

        i = 0

        while i < len(keys):
            k = keys[i]

            if self.chapter_text_dict[k]["level"] == 1:
                if k not in chapters:
                    chapters[k] = [k]

                i += 1

                while i < len(keys) and self.chapter_text_dict[keys[i]]["level"] == 2:
                    chapters[k].append(keys[i])
                    i += 1

        return chapters

    def mark_chapter(self):
        if self.initial_chapter_name in self.chapters:
            i2k = lambda i: str(i)
        else:
            i2k = lambda i: str(i + 1)

        num2chapter = OrderedDict()
        for i, c in enumerate(self.chapters):
            num2chapter[i2k(i)] = c
            for j, sc in enumerate(self.chapters[c][1:]):
                n = "{}.{}".format(i2k(i), j + 1)
                num2chapter[n] = sc
        return num2chapter

    def parse_pdf(self):
        chapter_text_dict = {}
        doc = fitz.open(self.path)  # pdf文档

        # chapter_names = doc.get_toc()
        # if chapter_names:
        #     return chapter_names

        prev_chapter_name = None
        chapter_name = self.initial_chapter_name
        chapter_level = 1
        text = ""
        skip_flag = False

        for i, page in enumerate(doc):
            if i < self.start_page:
                continue

            blocks = page.get_text("dict")["blocks"]

            for b in blocks:
                skip_flag = False
                for bf in self.filters["block"]:
                    if not bf(b):
                        skip_flag = True

                if skip_flag:
                    continue

                # chapter_name = ""
                # chapter_level = 1
                # text = ""
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            for cf in self.filters["chapter"]:
                                if cf(s):
                                    if chapter_name.startswith(
                                        self.initial_chapter_name
                                    ):
                                        chapter_name = ""
                                    chapter_name += " " + s["text"]
                                    chapter_level = 1

                            for cf2 in self.filters["chapter2"]:
                                if cf2(s):
                                    if chapter_name and chapter_level == 1:
                                        # chapter_name = re.sub(
                                        #     r"^[\d|.]+\s+", "", chapter_name.strip()
                                        # )
                                        chapter_name = re.sub(
                                            r"\s+", " ", chapter_name.strip()
                                        )

                                        prev_chapter_name = chapter_name

                                        chapter_text_dict[chapter_name] = {
                                            "level": chapter_level,
                                            "text": text,
                                        }
                                        chapter_name = ""
                                        text = ""

                                    chapter_name += " " + s["text"]
                                    chapter_level = 2

                            for tf in self.filters["text"]:
                                if tf(s):
                                    text += " " + s["text"]

                for ec in self.exclude_chapter_name:
                    if ec in chapter_name.lower():
                        skip_flag = True
                        break

                if skip_flag:
                    break

                if chapter_name and text:
                    if chapter_name == self.initial_chapter_name:
                        chapter_text_dict[chapter_name] = {
                            "level": chapter_level,
                            "text": text,
                        }
                        prev_chapter_name = chapter_name
                        chapter_name = ""
                        chapter_level = 1
                        text = ""
                    elif "chapter_format" in self.filters and not self.filters[
                        "chapter_format"
                    ](chapter_name):
                        chapter_name = ""
                        if prev_chapter_name:
                            chapter_text_dict[prev_chapter_name]["text"] += text
                            text = ""
                        # chapter_level = 1
                    else:
                        # chapter_name = re.sub(r"^[\d|.]+\s+", "", chapter_name.strip())
                        chapter_name = re.sub(r"\s+", " ", chapter_name.strip())
                        if (
                            prev_chapter_name
                            and chapter_text_dict[prev_chapter_name]["level"]
                            == chapter_level
                            and not chapter_text_dict[prev_chapter_name]["text"]
                        ):
                            del chapter_text_dict[prev_chapter_name]
                            prev_chapter_name = prev_chapter_name + " " + chapter_name
                            chapter_text_dict[prev_chapter_name] = {
                                "level": chapter_level,
                                "text": text,
                            }
                            chapter_name = ""
                            chapter_level = 1
                            text = ""
                        else:
                            chapter_text_dict[chapter_name] = {
                                "level": chapter_level,
                                "text": text,
                            }
                            prev_chapter_name = chapter_name
                            chapter_name = ""
                            chapter_level = 1
                            text = ""
                elif prev_chapter_name:
                    chapter_text_dict[prev_chapter_name]["text"] += text
                    text = ""

            if skip_flag:
                break

        for c in chapter_text_dict:
            chapter_text_dict[c]["text"] = self.clean_text(chapter_text_dict[c]["text"])

        if (
            self.initial_chapter_name in chapter_text_dict
            and not chapter_text_dict[self.initial_chapter_name]["text"]
        ):
            del chapter_text_dict[self.initial_chapter_name]

        doc.close()

        return chapter_text_dict

    def __str__(self) -> str:
        output = ""
        if self.title:
            output += f"\nThe chapters of paper [{self.title}]:\n"
        else:
            output += f"\nThe chapters of paper:\n"

        for n in self.num2chapter:
            c = self.num2chapter[n]
            if self.chapter_text_dict[c]["level"] == 1:
                output += f"<{n}> {c}\n"
            else:
                output += f"  <{n}> {c}\n"
        return output


if __name__ == "__main__":
    jcode = "mnsc"
    paper = Paper("pdf/10.1287-mnsc.2023.4818.pdf", jcode)
    print(paper)
