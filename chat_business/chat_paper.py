import datetime
import os
import re
import sys

import openai
import tenacity
import tiktoken

from .pdf_parser import Paper


# 定义Reader类
class Reader:
    # 初始化方法，设置属性
    def __init__(self, openai_key, model, paper, save=False):
        self.openai_key = openai_key
        self.save = save
        self.paper = paper

        from .chat_prompt import system_prompt, summary_prompt

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

    def find_text(self, keywords):
        chapters, chapter_text_dict = self.paper.chapters, self.paper.chapter_text_dict
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

    def summary_with_chat(self):
        keywords, prompt = (
            self.summary_prompt["keywords"],
            self.summary_prompt["prompt"],
        )
        text = self.find_text(keywords)

        print("-" * 100)
        print("Summarize paper with [Introduction] and [Conclution]...\n")

        try:
            chat_text = self.chat(text=text, prompt=prompt)
        except Exception as e:
            print("error:", e)

        self.summary_text = chat_text

        print("-" * 100)

        if self.save:
            date_str = str(datetime.datetime.now())[:13].replace(" ", "-")
            export_path = os.path.join(self.root_path, "export")
            if not os.path.exists(export_path):
                os.makedirs(export_path)

            fname = self.paper.path.split("/")[-1]
            fname = fname.replace(".pdf", "")
            file_name = os.path.join(
                export_path,
                date_str + "-" + fname + "." + self.file_format,
            )
            self.export_to_markdown(chat_text, file_name=file_name, mode="w")

    def replace_text(self, prompt):
        results = re.findall(r"<([\d|.]+?)>", prompt)

        for n in results:
            if n in self.paper.num2chapter:
                sup_prompt = (
                    f"\nIn the above question, <{n}> refers to the following text, which is a chapter in a paper:\n"
                    + "{}"
                )

                c = self.paper.num2chapter[n]
                print(f"\nThe answer is generating based on [{n} {c}]...\n")

                if self.paper.chapter_text_dict[c]["level"] == 1:
                    text = ""
                    for c2 in self.paper.chapters[c]:
                        text += " " + self.paper.chapter_text_dict[c2]["text"]
                else:
                    text = self.paper.chapter_text_dict[c]["text"]

                return prompt + sup_prompt, text.strip()

        print(
            "\nCould not find {} in the paper.".format(
                ", ".join([f"<{r}>" for r in results])
            )
        )
        return None, None

    def user_chat(self):
        q = input("Input your question (input 'quit' to quit) : ")
        if q.startswith("quit"):
            return True

        try:
            prompt, text = self.replace_text(q)
            if not prompt:
                print("-" * 100)
                return

            self.chat(
                text=text,
                prompt=prompt,
            )
        except Exception as e:
            print("error:", e)

        print("-" * 100)
        return False

    @tenacity.retry(
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        stop=tenacity.stop_after_attempt(5),
        reraise=True,
    )
    def chat(self, text, prompt):
        openai.api_key = self.openai_key

        prompt_token = len(self.encoding.encode(prompt))
        text_token = len(self.encoding.encode(text))

        clip_text_index = int(
            len(text) * (self.max_token_num - prompt_token - 200) / text_token
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
            f"\nTotal Token Used: {response.usage.total_tokens} | Response Time: {response.response_ms / 1000.0}s"
        )

        return result

    def export_to_markdown(self, text, file_name, mode="w"):
        # 使用markdown模块的convert方法，将文本转换为html格式
        # html = markdown.markdown(text)
        # 打开一个文件，以写入模式
        with open(file_name, mode, encoding="utf-8") as f:
            # 将html格式的内容写入文件
            f.write(text)


def chat_paper(pdf_path, jcode, openai_key, model):
    paper = Paper(
        pdf_path,
        jcode,
    )
    print("-" * 100)
    print(paper)
    print("-" * 100)

    reader = Reader(openai_key, model, paper)

    reader.summary_with_chat()

    while True:
        skip_flag = reader.user_chat()
        if skip_flag:
            break


def chat_paper_cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jcode",
        type=str,
        required=True,
        default="mnsc",
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
    parser.add_argument(
        "--openai_key",
        type=str,
        default=None,
        help="OpenAI API Key",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="16k",
        help="The model to chat with",
    )

    args = parser.parse_args()

    if args.openai_key:
        openai_key = args.openai_key
        model = args.model
    else:
        from config import openai_key, model

    chat_paper(args.pdf_path, args.jcode, openai_key, model)


if __name__ == "__main__":
    chat_paper_cli()
