exclude_chapter_name = [
    "acknowledgments",
    "acknowledgment",
    "endnotes",
    "references",
    "competing interests",
    "appendix",
]

informs_filter = {
    "start_page": 1,
    "filters": {
        "title": [
            lambda s: s["font"] == "y7por" and abs(s["size"] - 20) < 0.1,
            # 新版本
            lambda s: s["font"] == "AdvOT114894c7.B"
            and abs(s["size"] - 16) < 0.1
            and s["color"] == 1654656,
        ],
        "chapter": [
            # 老版本
            lambda s: s["flags"] == 20
            and s["font"] == "y7pob"
            and abs(s["size"] - 13) < 0.1,
            # 新版本
            lambda s: s["font"] == "AdvOT114894c7.B" and abs(s["size"] - 12) < 0.1,
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
        ],
        "block": [lambda b: b["bbox"][1] > 60],
    },
}

journal_filter = {
    "mis quarterly": {
        "start_page": 0,
        "filters": {
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
}

jcode_name = {
    "mnsc": "Management Science",
    "isre": "Information Systems Research",
    "ijoc": "INFORMS Journal on Computing",
    "mksc": "Marketing Science",
    "opre": "Operations Research",
    "msom": "Manufacturing & Service Operations Management",
    "orsc": "Organization Science",
    "misq": "MIS Quarterly",
}


def get_filter_func(jname):
    jname = jname.lower()
    if jname in [
        "management science",
        "information systems research",
        "informs journal on computing",
        "marketing science",
        "operations research",
        "manufacturing & service operations management",
        "organization science",
    ]:
        return informs_filter
    elif jname in journal_filter:
        return journal_filter[jname]


def get_filter_by_jcode(jcode):
    return get_filter_func(jcode_name[jcode])


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
