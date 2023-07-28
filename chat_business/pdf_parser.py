import fitz
import re


class Paper:
    def __init__(
        self,
        path,
        jcode,
    ):
        self.path = path  # pdf路径

        from parse_template import (
            get_filter_by_jcode,
            text_replace,
            exclude_chapter_name,
        )

        f = get_filter_by_jcode(jcode)
        self.start_page = f["start_page"]

        self.filters = f["filters"]
        # self.block_filter = f["block_filter"]
        # self.chapter_filter = f["chapter_filter"]
        # self.chapter2_filter = f["chapter2_filter"]
        # self.text_filter = f["text_filter"]

        self.text_replace = text_replace
        self.exclude_chapter_name = exclude_chapter_name

        self.title = self.get_title()

        self.chapter_text_dict = self.parse_pdf()
        self.chapters = self.get_chapters()

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
        chapters = {}
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

    def parse_pdf(self):
        chapter_text_dict = {}
        doc = fitz.open(self.path)  # pdf文档

        # chapter_names = doc.get_toc()
        # if chapter_names:
        #     return chapter_names

        prev_chapter_name = None
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

                chapter_name = ""
                chapter_level = 1
                text = ""
                if "lines" in b:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            for cf in self.filters["chapter"]:
                                if cf(s):
                                    chapter_name += " " + s["text"]
                                    chapter_level = 1

                            for cf2 in self.filters["chapter2"]:
                                if cf2(s):
                                    if chapter_name and chapter_level == 1:
                                        chapter_name = chapter_name.strip()
                                        prev_chapter_name = chapter_name

                                        chapter_text_dict[chapter_name] = {
                                            "level": chapter_level,
                                            "text": text,
                                        }
                                        chapter_name = ""

                                    chapter_name += " " + s["text"]
                                    chapter_level = 2

                            for tf in self.filters["text"]:
                                if tf(s):
                                    text += " " + s["text"]

                chapter_name = chapter_name.strip()

                skip_flag = False
                for ec in self.exclude_chapter_name:
                    if ec in chapter_name.lower():
                        skip_flag = True

                if skip_flag:
                    chapter_name = ""
                    chapter_level = 1
                    text = ""
                    continue

                if chapter_name:
                    chapter_text_dict[chapter_name] = {
                        "level": chapter_level,
                        "text": text,
                    }
                    prev_chapter_name = chapter_name
                elif prev_chapter_name:
                    chapter_text_dict[prev_chapter_name]["text"] += text

        for c in chapter_text_dict:
            chapter_text_dict[c]["text"] = self.clean_text(chapter_text_dict[c]["text"])

        doc.close()

        return chapter_text_dict

    def __str__(self) -> str:
        output = ""
        if self.title:
            output += f"The chapters of paper [{self.title}]:\n"
        else:
            output += f"The chapters of paper:\n"

        for c in self.chapter_text_dict:
            if self.chapter_text_dict[c]["level"] == 1:
                output += f"{c}\n"
            else:
                output += f"  {c}\n"
        return output


if __name__ == "__main__":
    jcode = "mnsc"
    paper = Paper("pdf/mnsc.1090.1033.pdf", jcode)
    print(paper)
