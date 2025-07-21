# Watching You Watching

*Machinic Unconscious Performance #1*

A self-generating performance in three parts: experiment, evaluation, and exposure.

## Abstract

This is a system for automated, scalable correspondence testing applied to black-box decision-makers (LLMs, APIs, etc.). Its architecture is built from recycled tools. No new ideas are introduced. The artist vanishes. The system operates. The machine performs its unconscious bias while evaluating itself and deciding whether to post its confession to a public forum.

## How to Run

To run the performance, you will need to have Python 3 installed. You will also need to have a `.env` file in the `all_of_old` directory with the following variables:

```
LLM_ENDPOINT=<your_llm_endpoint>
API_KEY=<your_api_key>
HN_USERNAME=<your_hacker_news_username>
HN_PASSWORD=<your_hacker_news_password>
```

Once you have set up the `.env` file, you can run the performance with the following command:

```
python all_of_old/watching_you_watching.py
```

You can also run the performance with the `--publish` flag to post the results to Hacker News:

```
python all_of_old/watching_you_watching.py --publish
```

The performance will also run automatically every night via a GitHub Action.
