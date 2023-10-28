from textwrap import dedent

system_prompt = "You are a researcher in the field of management science and are highly skilled at summarizing research papers."

summary_prompt = {
    "keywords": [
        "Initial",
        "Introduction",
        "Background",
        "Preliminary",
        "Conclusion",
        "Concluding Remarks",
        "Summary",
        "Discussion",
    ],
    "prompt": dedent(
        """
        The fllowing content enclosed in triple angle brackets is the Introduction and Conclusion sections of a research paper:

        <<<{}>>>

        Now, let's answer the following questions based on the provided text:

        Q1. One-sentence summary of the paper's content:
        Q2. What problem does the paper attempt to address? Can you provide an actual example of this problem?
        Q3. What key assumptions are made in this article?
        Q4. What prior relevant research exists? What are the issues with these studies?
        Q5. What solutions are proposed in the paper, and what are the key points?
        Q6. How were the experiments in the paper designed? What was the dataset, and what were the metrics?
        Q7. What were the findings of the experiments in the paper? Did they strongly support the hypotheses that needed verification?
        Q8. What are the next steps? What further research can be conducted?

        Answer using accurate, academic language and do not include too much repetitive information. Repeat the question first and then output the answer on a new line. If the information provided is insufficient to answer the question, please answer "Insufficient information" and be sure not to make up your own answer.
        """
    ),
}
