from textwrap import dedent

system_prompt = "You are a researcher in the field of management science who is good at summarizing papers using concise statements."

summary_prompt = {
    "keywords": [
        "Introduction",
        "Background",
        "Preliminary",
        "Conclusion",
    ],
    "prompt": dedent(
        """
        This is the introduction of a paper wrapped in triple angle brackets: <<<{}>>>

        Now, I need your help to use the provided text to answer the following questions. If the answer cannot be found in the provided text, write "N/A."

        1. What problem does the paper attempt to solve? Is this a new problem?
        2. What is a scientific hypothesis that the paper is trying to test?
        3. What are the past methods? What are the problems with them? Is the approach well motivated?
        4. What is the key to the solution proposed in the paper?
        5. How were the experiments in the paper designed? What are the data sets? What are the metrics?
        6. What are the findings in the paper? Is there good support for the scientific hypothesis that needs to be tested?
        7. What are the next steps? What work can be furthered?

        Statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers. When answering, please repeat the question followed by a new line to output the answer. If the answer cannot be found in the provided text, write "N/A."
        """
    ),
    "token": 1000,
}
