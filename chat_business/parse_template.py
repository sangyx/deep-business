import re

exclude_chapter_name = [
    "acknowledgments",
    "acknowledgment",
    "endnotes",
    "references",
    "competing interests",
    "appendix",
    "about the authors",
]


def starts_with_roman_num(s):
    return s[0] in ["X", "V", "I"]


def chapter_start_with_num_dot(s):
    match = re.search(r"^\s+\d+\.", s)
    if match:
        return True
    else:
        return False


informs_filter = {
    "start_page": 1,
    "filters": {
        "title": [
            lambda s: s["font"] == "y7por" and abs(s["size"] - 20) < 0.1,
            # 新版本
            lambda s: s["font"] == "AdvOT114894c7.B"
            and abs(s["size"] - 16) < 0.1
            and s["color"] == 1654656,
            lambda s: s["font"] == "TeXGyreHeros-Bold"
            and abs(s["size"] - 16) < 0.1
            and s["color"] == 1654912,
        ],
        "chapter": [
            # 老版本
            lambda s: s["flags"] == 20
            and s["font"] == "y7pob"
            and abs(s["size"] - 13) < 0.1,
            # 新版本
            lambda s: s["font"] == "AdvOT114894c7.B" and abs(s["size"] - 12) < 0.1,
            lambda s: s["font"] == "TeXGyreHeros-Bold" and abs(s["size"] - 12) < 0.1,
        ],
        "chapter2": [
            # # 老版本
            # lambda s: s["flags"] == 20
            # and s["font"] == "y7pob"
            # and abs(s["size"] - 13) < 0.1,
            # 新版本
            lambda s: s["flags"] == 4
            and s["font"] == "AdvOT114894c7.B"
            and abs(s["size"] - 10) < 0.1,
            lambda s: s["font"] == "TeXGyreHeros-Bold"
            and abs(s["size"] - 10) < 0.1
            and s["color"] == 1654912,
        ],
        "text": [
            lambda s: s["flags"] in [4, 6]
            and abs(s["size"] - 10) < 0.1
            and s["font"] in ["y7por", "y7poih", "y7poi"],
            lambda s: s["font"]
            in [
                "AdvOT3258b86f",
                "AdvOT3258b86f+20",
                "AdvOT3258b86f+fb",
                "AdvOTd8ef4e6f.I",
            ]
            and abs(s["size"] - 10) < 0.1,
            lambda s: s["font"]
            in [
                "TeXGyrePagellaX-Regular",
            ]
            and abs(s["size"] - 10) < 0.1,
        ],
        "block": [lambda b: b["bbox"][1] > 60],
    },
}

jcode_filter = {
    "misq": {
        "start_page": 0,
        "filters": {
            "title": [
                lambda s: s["font"] == "Arial-BoldMT"
                and abs(s["size"] - 20) < 0.1
                and s["flags"] == 16,
                lambda s: s["font"] == "Arial-BoldMT"
                and abs(s["size"] - 16) < 0.1
                and s["flags"] == 16,
            ],
            "chapter": [
                lambda s: s["flags"] == 16
                and s["font"] == "Arial-BoldMT"
                and abs(s["size"] - 13) < 0.1,
            ],
            "chapter2": [
                lambda s: s["flags"] == 18
                and s["font"] == "Arial-BoldItalicMT"
                and abs(s["size"] - 11) < 0.1,
            ],
            "text": [
                lambda s: s["flags"] in [4]
                and abs(s["size"] - 10) < 0.1
                and s["font"] in ["TimesNewRomanPSMT"],
            ],
            "block": [],
        },
    },
    "jf": {
        "start_page": 0,
        "filters": {
            "title": [
                lambda s: s["font"] == "NewCenturySchlbk-Bold"
                and abs(s["size"] - 14) < 0.1
            ],
            "chapter": [
                lambda s: s["flags"] in [20, 22]
                and s["font"] in ["NewCenturySchlbk-Bold", "NewCenturySchlbk-BoldIta"]
                and abs(s["size"] - 10) < 0.1
            ],
            "chapter2": [
                lambda s: s["flags"] == 6
                and s["font"] == "NewCenturySchlbk-Italic"
                and abs(s["size"] - 10) < 0.1
                and s["bbox"][0] < 70
            ],
            "text": [
                lambda s: s["flags"] in [4]
                and abs(s["size"] - 10) < 0.1
                and s["font"] in ["NewCenturySchlbk-Roman"],
            ],
            "block": [],
            "chapter_format": lambda c: ". " in c,
        },
    },
    "jfe": {
        "start_page": 0,
        "filters": {
            "title": [
                lambda s: s["font"] == "Gulliver" and abs(s["size"] - 13.5) < 0.1
            ],
            "chapter": [
                lambda s: s["flags"] == 20
                and s["font"] == "Gulliver-Bold"
                and abs(s["size"] - 8) < 0.1
            ],
            "chapter2": [
                lambda s: s["flags"] == 6
                and s["font"] == "Gulliver-Italic"
                and abs(s["size"] - 8) < 0.1
            ],
            "text": [
                lambda s: s["flags"] in [4]
                and abs(s["size"] - 8) < 0.1
                and s["font"] in ["Gulliver"],
            ],
            "block": [],
            "chapter_format": lambda c: re.search(r"^\s*\d+\.(\d+\.)? ", c),
        },
    },
    "rfs": {
        "start_page": 0,
        "filters": {
            "title": [
                lambda s: s["font"] == "TimesLTStd-Bold" and abs(s["size"] - 16) < 0.1
            ],
            "chapter": [
                lambda s: s["flags"] == 20
                and s["font"] == "TimesLTStd-Bold"
                and abs(s["size"] - 10) < 0.1
                and s["bbox"][0] < 57
            ],
            "chapter2": [
                lambda s: s["flags"] == 20
                and s["font"] == "TimesLTStd-Bold"
                and abs(s["size"] - 10) < 0.1
                and s["bbox"][0] > 57
                and not re.search(r"\d+\.\d+.\d+", s["text"])
            ],
            "text": [
                lambda s: s["flags"] in [4]
                and abs(s["size"] - 10) < 0.1
                and s["font"] in ["TimesLTStd-Roman"],
            ],
            "block": [],
            "chapter_format": lambda c: re.search(r"^\s+\d+\.\d? ", c),
        },
    },
}

jcode_name = {
    "mnsc": "Management Science",
    "isre": "Information Systems Research",
    "misq": "MIS Quarterly",
    # "ijoc": "INFORMS Journal on Computing",
    "mksc": "Marketing Science",
    "opre": "Operations Research",
    # "msom": "Manufacturing & Service Operations Management",
    # "orsc": "Organization Science",
    "jf": "Journal of Finance",
    "jfe": "Journal of Financial Economics",
    "rfs": "Review of Financial Studies",
}

jname_code = {jcode_name[k].lower(): k for k in jcode_name}


def get_filter_func(jname):
    return get_filter_by_jcode(jname_code[jname])


def get_filter_by_jcode(jcode):
    if jcode in [
        "mnsc",
        "isre",
        "mksc",
        "opre",
        "orsc",
    ]:
        return informs_filter
    elif jcode in jcode_filter:
        return jcode_filter[jcode]


text_replace = {
    "- ": "",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "\s+": " ",
    " ' s": "'s",
    " ’ s": "'s",
    " fi ": "fi",
    " fl ": "fl",
}
