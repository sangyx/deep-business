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
        This is the introduction of a paper wrapped in triple angle brackets: 

        <<<{}>>>

        Now, I need your help to use the provided text to answer the following questions:

        1. Briefly summarize the paper's content in one sentence.
        2. What problem does the paper attempt to solve? Is this a new problem?
        3. What scientific hypothesis is the paper attempting to test?
        4. What were the solutions used in the past, and what were the problems associated with them? Is the proposed solution well motivated?
        5. What is the key to the proposed solution?
        6. How were the experiments in the paper designed? What are the data sets used? What are the metrics used to evaluate the results?
        7. What are the findings in the paper? Is there good support for the scientific hypothesis that needs to be tested?
        8. What are the next steps? Is there any work that can be continued?

        Statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers. When answering, you must repeat the question first, and then output the answer on a new line. If the provided text does not contain the information needed to answer this question then simply write: "Insufficient information."
        """
    ),
    "token": 1000,
}
