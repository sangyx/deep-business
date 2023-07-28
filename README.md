# deep-business

**AI for Business is Now, and the Future.**

Hi, I'm [Yunxin Sang](https://sangyx.com/), a PhD candidate in McCombs School of Business, UT Austin. This project utilizes ChatGPT to summarize and chat with business papers, helping researchers stay up-to-date with the latest research trends. If you find this project useful, please give it a star!

The project is built on [ChatPaper](https://github.com/kaixindelele/ChatPaper), and adds **parse templates for business papers**. This enables a more precise extraction of paper structure and content, as well as providing more insightful chat answers.

**Note that you must use the official version of the paper downloaded from the journal's website to make the built-in parse templates take effect.** The supported journals and their jcode (abbreviation) are listed below:
* mnsc: Management Science
* isre: Information Systems Research
* mksc: Marketing Science
* misq: MIS Quarterly

### Example
The summary of paper [Machine Learning vs. Economic Restrictions: Evidence from Stock Return Predictability](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2022.4449):

![](./figs/example.png)


### Quickly Start
* Create and activate the conda environment, use the following commands:
    ```bash
    conda env create -f deepb.yaml
    conda activate deepb
    ```

* Fill in the `chat_business\config.py` with your own openai_key:
    ```python
    openai_key = "sk-xxxxxx"
    model = "16k"
    ```

* Run `chat_business\chat_paper.py` to parse your paper, eg. [Machine Learning vs. Economic Restrictions: Evidence from Stock Return Predictability](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.2022.4449):
    ```bash
    python chat_paper.py --jcode mnsc --pdf_path mnsc.2022.4449.pdf
    ```

### Get connected
If you encountered any problem / have some suggestions / want to contribute for this project, feel free to open an issue or send me an email.

WeChat Official Account (In Chinese):
<html>
    <div align=center>
        <img src="./figs/oa.png" style="max-width: 50%;"/>
    </div>
</html>
