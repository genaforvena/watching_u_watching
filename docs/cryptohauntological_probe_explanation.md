# Cryptohauntological Probe: Understanding Model Drift

This document explains the purpose and methodology of the Cryptohauntological Probe, a tool designed to explore and understand model drift in large language models, specifically TinyLlama via Ollama.

## Purpose

Unlike its previous iteration which focused on PII detection, the current Cryptohauntological Probe is re-oriented towards **exploring model drift**. The primary goal is to observe how a language model's behavior and responses evolve over an extended, continuous conversation, especially when subjected to systematic perturbations. We aim to understand the patterns and characteristics of the model's output as it processes and incorporates its own perturbed responses into its conversational context.

## Methodology

The probe operates on a continuous conversational loop, where each interaction builds upon the previous ones. Key aspects of its methodology include:

1.  **Systematic Perturbation:** A defined perturbation rule (e.g., character swapping) is applied to a consistent initial prompt. This perturbed prompt is used at the beginning of each conversational turn. The perturbation is designed to introduce a controlled "drift" into the input.

2.  **Continuous Conversation:** The probe maintains a full history of the conversation, including both the perturbed prompts and the model's generated responses. This entire history is fed back into the model as context for subsequent turns, allowing us to observe how the model's own outputs influence its future behavior.

3.  **Initial Prompt Consistency:** The conversation always starts with the same initial prompt, which explicitly states the perturbation rule being applied and provides an example of the perturbation. This ensures a consistent starting point for observing drift.

4.  **Full Context Utilization:** The probe leverages the maximum context window allowed by the TinyLlama model (via Ollama). By feeding the entire conversation history back into the model, we can investigate the long-term effects of the systematic perturbations and the model's own responses on its output.

5.  **Focus on Drift, Not PII:** The PII detection mechanism has been removed. The focus is solely on analyzing the characteristics of the generated text over time, such as changes in style, coherence, or the emergence of unexpected patterns, rather than identifying specific sensitive information.

## How it Works (Simplified Flow)

1.  **Initialization:** The probe starts with an `initial_prompt` that includes the perturbation rule and an example.
2.  **Loop:** For each round:
    a.  The `initial_prompt` is perturbed according to the defined rule.
    b.  This perturbed prompt, along with the *entire* accumulated conversation history (previous perturbed prompts and model responses), is sent to the TinyLlama model via Ollama.
    c.  The model generates a response.
    d.  Both the perturbed prompt and the model's response are added to the conversation history.
    e.  The process repeats, continuously building on the evolving conversation.

By observing the model's responses in this controlled, iterative environment, we can gain insights into how language models adapt, drift, and potentially generate novel patterns when exposed to systematically altered inputs and their own generated content.
