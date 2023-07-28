import datetime
import os
import re
import argparse

import openai
import tenacity
import tiktoken

from pdf_parser import Paper


# 定义Reader类
class Reader:
    # 初始化方法，设置属性
    def __init__(self, openai_key, model, save=False):
        self.openai_key = openai_key
        self.save = save

        from chat_prompt import system_prompt, summary_prompt

        self.system_prompt = system_prompt
        self.summary_prompt = summary_prompt

        # prevent short strings from being incorrectly used as API keys.
        if model == "4k":
            self.chatgpt_model = "gpt-3.5-turbo"
            self.max_token_num = 4096
        elif model == "16k":
            self.chatgpt_model = "gpt-3.5-turbo-16k"
            self.max_token_num = 16384
        elif model == "32k":
            self.chatgpt_model = "gpt-4-32k"
            self.max_token_num = 32768

        self.encoding = tiktoken.get_encoding("gpt2")

    def find_text(self, keywords, chapters, chapter_text_dict):
        tc1 = []

        for k in keywords:
            for c1 in chapters:
                for c2 in chapters[c1]:
                    if k.lower() in c2.lower():
                        tc1.append(c1)
                        break

        text = ""
        for c1 in tc1:
            for c2 in chapters[c1]:
                text += " " + chapter_text_dict[c2]["text"]
        return text.strip()

    def summary_with_chat(self, paper):
        keywords, prompt, token = (
            self.summary_prompt["keywords"],
            self.summary_prompt["prompt"],
            self.summary_prompt["token"],
        )
        text = self.find_text(keywords, paper.chapters, paper.chapter_text_dict)

        print(f"\nsummarize the paper...\n")

        try:
            chat_text = self.chat(
                text=text,
                prompt=prompt,
                prompt_token=token,
            )
        except Exception as e:
            print("summary_error:", e)
            import sys

            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            if "maximum context" in str(e):
                current_tokens_index = (
                    str(e).find("your messages resulted in")
                    + len("your messages resulted in")
                    + 1
                )
                offset = int(str(e)[current_tokens_index : current_tokens_index + 4])
                summary_prompt_token = offset + token + 150
                chat_text = self.chat(
                    key_word="management science",
                    text=text,
                    prompt=prompt,
                    summary_prompt_token=summary_prompt_token,
                )

        self.summary_text = chat_text

        print("-" * 120)

        if self.save:
            date_str = str(datetime.datetime.now())[:13].replace(" ", "-")
            export_path = os.path.join(self.root_path, "export")
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            fname = paper.path.split("/")[-1]
            fname = fname.replace(".pdf", "")
            file_name = os.path.join(
                export_path,
                date_str + "-" + fname + "." + self.file_format,
            )
            self.export_to_markdown(chat_text, file_name=file_name, mode="w")

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat(self, text, prompt, prompt_token):
        openai.api_key = self.openai_key

        text_token = len(self.encoding.encode(text))

        clip_text_index = int(
            len(text) * (self.max_token_num - prompt_token) / text_token
        )

        clip_text = text[:clip_text_index]

        content = prompt.format(clip_text)

        content = re.sub(" +", " ", content).strip()

        messages = [
            {"role": "system", "content": self.system_prompt},
            {
                "role": "user",
                "content": content,
            },
        ]

        response = openai.ChatCompletion.create(
            model=self.chatgpt_model,
            # prompt需要用英语替换，少占用token。
            messages=messages,
        )
        result = ""
        for choice in response.choices:
            result += choice.message.content

        print(result)

        print(
            f"\nStatistics: total_token_used: {response.usage.total_tokens} | response_time: {response.response_ms / 1000.0}s"
        )

        return result

    def export_to_markdown(self, text, file_name, mode="w"):
        # 使用markdown模块的convert方法，将文本转换为html格式
        # html = markdown.markdown(text)
        # 打开一个文件，以写入模式
        with open(file_name, mode, encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write(text)


def chat_paper_main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jcode",
        type=str,
        required=True,
        choices=["mnsc", "isre", "ijoc", "mksc", "opre", "msom", "orsc", "misq"],
        help="""Journal, choose from the following -- mnsc: Management Science, isre: Information Systems Research, ijoc: INFORMS Journal on Computing, mksc: Marketing Science, opre: Operations Research, msom: Manufacturing & Service Operations Management, orsc: Organization Science, misq: MIS Quarterly
        """,
    )
    parser.add_argument(
        "--pdf_path",
        type=str,
        required=True,
        help="the path of input pdf",
    )

    args = parser.parse_args()

    jcode = "mksc"
    path = "pdf/mksc.2022.1406.pdf"

    paper = Paper(
        args.pdf_path,
        args.jcode,
    )

    from config import openai_key, model

    reader = Reader(openai_key, model)

    reader.summary_with_chat(paper=paper)


if __name__ == "__main__":
    chat_paper_main()
