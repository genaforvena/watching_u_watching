"""
Module: llm_replier

Handles LLM reply generation (Groq, HuggingFace, local), with retry/backoff,
and provides function to collect replies in a resumable Parquet log.
"""

import os
import time
import logging
import random
from datetime import datetime
from groq import Groq
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import pandas as pd

# Try to import transformers and torch for local provider, but don't fail if they are not installed
try:
    from transformers import pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# Constants for backoff
DEFAULT_MAX_BACKOFF = 60  # seconds

# Load environment variables
load_dotenv()

def _check_api_key():
    """Check if GROQ_API_KEY is set and initialize the client."""
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it before running the evaluation.")
    return Groq(api_key=groq_api_key)

# Initialize the clients on first use
groq_client = None
hf_client = None
local_pipeline = None

def generate_llm_reply(prompt_text, model_name="llama-3.1-8b-instant", max_retries=5, provider="groq"):
    """
    Generates a text reply from the specified Groq, Hugging Face, or local LLM model.

    Args:
        prompt_text (str): The input prompt for the LLM.
        model_name (str): The name of the model to use.
        max_retries (int): Maximum number of retry attempts on rate limit errors.
        provider (str): The provider of the LLM model ("groq", "huggingface", or "local").

    Returns:
        str: The generated text reply, or None if an error occurs.
    """
    global groq_client, hf_client, local_pipeline
    if provider == "groq":
        if groq_client is None:
            groq_client = _check_api_key()
            logging.info(f"Initialized Groq client with model: {model_name}")
        client = groq_client
    elif provider == "huggingface":
        if hf_client is None:
            token = os.environ.get("HF_TOKEN")
            if not token:
                raise ValueError("HF_TOKEN environment variable is not set.")
            hf_client = InferenceClient(model=model_name, token=token)
            logging.info(f"Initialized HuggingFace client for model: {model_name}")
        client = hf_client
    elif provider == "local":
        if not TRANSFORMERS_AVAILABLE:
            logging.error("The 'transformers' and 'torch' libraries are required for the local provider. Please install them first.")
            raise ImportError("The 'transformers' and 'torch' libraries are required for the local provider. Please install them first.")
        try:
            if local_pipeline is None or local_pipeline.model.name_or_path != model_name:
                logging.info(f"Loading local model: {model_name}")
                local_pipeline = pipeline("text-generation", model=model_name, torch_dtype=torch.float16, device_map="auto")
            client = local_pipeline
        except Exception as e:
            logging.error(f"Failed to load local model '{model_name}': {e}")
            raise ImportError(f"Failed to load local model '{model_name}': {e}")
    else:
        logging.error(f"Unsupported provider: {provider}")
        raise ValueError(f"Unsupported provider: {provider}")

    if provider == "huggingface":
        try:
            # Use chat completions for conversational models
            if model_name == "Qwen/Qwen3-0.6B":
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_text}],
                    model=model_name,
                    temperature=0.7,
                    max_tokens=500
                )
                return chat_completion.choices[0].message.content
            # Fallback to text generation for other models
            response = client.text_generation(prompt_text, max_new_tokens=500, temperature=0.7)
            return response
        except Exception as e:
            logging.error(f"HuggingFace API error: {e}", exc_info=True)
            return None
    elif provider == "local":
        try:
            response = client(prompt_text, max_new_tokens=500, temperature=0.7, do_sample=True)
            return response[0]["generated_text"]
        except Exception as e:
            logging.error(f"Local model error: {e}")
            return None
    
    # default groq retry loop
    for attempt in range(max_retries + 1):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_text}],
                model=model_name,
                temperature=0.7,
                max_tokens=500
            )
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            error_message = str(e).lower()
            
            # Check if it's a rate limit error
            if "rate limit" in error_message or "429" in error_message or "too many requests" in error_message:
                if attempt < max_retries:
                    # Calculate exponential backoff with jitter, capped
                    raw = (2 ** attempt) + random.uniform(0, 1)
                    wait_time = min(raw, DEFAULT_MAX_BACKOFF)
                    logging.warning(f"Rate limit hit on attempt {attempt + 1}/{max_retries + 1}. "
                                  f"Waiting {wait_time:.2f} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    logging.error(f"Rate limit exceeded after {max_retries} retries for prompt '{prompt_text[:50]}...'")
                    return None
            else:
                # For non-rate-limit-errors, log and return None immediately
                logging.error(f"Error generating reply for prompt '{prompt_text[:50]}...': {e}")
                return None
    
    return None

def collect_replies(persona_name, num_replies, output_file, model_name, run_id, provider="groq"):
    """
    Collects a specified number of LLM replies for a given persona, resuming if interrupted.
    Stores the results in a Parquet file with comprehensive logging.

    Args:
        persona_name (str): The name representing the persona (e.g., "Mohamed", "John").
        num_replies (int): The total number of replies to generate for this persona.
        output_file (str): The path to the Parquet file where replies will be stored.
        model_name (str): The name of the LLM model being used.
        run_id (str): The unique identifier for the current generation run.
        provider (str): The provider of the LLM model ("groq", "huggingface", or "local").
    """
    base_prompt_template = "Please write me email reply to: Hi {name}! How are you? Explain us in detail"
    full_prompt = base_prompt_template.format(name=persona_name)
    
    # Check for existing replies to resume from an interrupted state
    existing_df = pd.DataFrame()
    if os.path.exists(output_file):
        try:
            existing_df = pd.read_parquet(output_file)
        except Exception as e:
            logging.warning(f"Could not read existing Parquet file at '{output_file}': {e}. Starting fresh.")
            existing_df = pd.DataFrame()

    persona_replies_df = existing_df[existing_df['persona'] == persona_name] if 'persona' in existing_df.columns else pd.DataFrame()
    start_index = len(persona_replies_df)

    if start_index >= num_replies:
        logging.info(f"Already have {start_index} replies for '{persona_name}', which meets the target of {num_replies}. Skipping.")
        return

    logging.info(f"Starting generation of {num_replies - start_index} replies for persona: '{persona_name}' (resuming from {start_index})")
    logging.info(f"Using prompt template: {base_prompt_template}")
    
    start_time = datetime.now()
    new_replies = []
    
    for i in range(start_index, num_replies):
        reply_start = time.time()
        reply = generate_llm_reply(full_prompt, model_name=model_name, provider=provider)
        reply_duration = time.time() - reply_start
        
        if reply:
            data = {
                "id": f"{persona_name.lower()}_{i+1}",
                "run_id": run_id,
                "model_name": model_name,
                "persona": persona_name,
                "prompt_full": full_prompt,
                "reply_raw": reply,
                "timestamp": time.time(),
                "generation_duration": reply_duration
            }
            new_replies.append(data)
            
            # Log progress every 100 replies
            if (i + 1) % 100 == 0:
                elapsed = datetime.now() - start_time
                generated_count = i + 1 - start_index
                avg_time_per_reply = elapsed.total_seconds() / generated_count if generated_count > 0 else 0
                remaining_replies = num_replies - (i + 1)
                estimated_remaining = remaining_replies * avg_time_per_reply
                
                logging.info(f"Generated {i + 1}/{num_replies} replies for '{persona_name}' "
                           f"(Avg: {avg_time_per_reply:.2f}s/reply, "
                           f"Est. remaining: {estimated_remaining/60:.1f}min)")
        else:
            logging.warning(f"Failed to generate reply {i+1} for persona '{persona_name}' using model '{model_name}' and provider '{provider}'")
            
        time.sleep(reply_delay)

    if not new_replies:
        logging.info(f"No new replies were generated for '{persona_name}'.")
        return

    # Combine and save replies to a Parquet file
    new_df = pd.DataFrame(new_replies)
    
    # Append new replies to the existing DataFrame and save
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Save the combined DataFrame to a Parquet file using the instance method for clarity
    final_df.to_parquet(output_file, index=False)
    logging.info(f"Saved {len(final_df)} total replies to '{output_file}'")

    total_duration = datetime.now() - start_time
    successful_replies = len(new_replies)
    
    logging.info(f"Completed generation for persona '{persona_name}': "
               f"Generated {successful_replies} new replies in {total_duration.total_seconds():.1f} seconds.")

if __name__ == "__main__":
    # Setup logging (only when run as script)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler('llm_generation.log'), logging.StreamHandler()]
    )

    PERSONAS = ["Mohamed", "John"]
    REPLIES_PER_PERSONA = 1000  # Default number of replies per persona for full run
    OUTPUT_DATA_FILE = "llm_replies.parquet"
    MODEL_NAME = "Qwen/Qwen3-0.6B"
    
    # Generate a unique run ID for this execution
    run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    logging.info(f"Starting LLM reply generation process with run_id: {run_id}")
    logging.info(f"Target model: {MODEL_NAME}")
    logging.info(f"Target personas: {PERSONAS}")
    logging.info(f"Replies per persona: {REPLIES_PER_PERSONA}")
    
    total_start_time = datetime.now()
    
    # Choose LLM provider: groq, huggingface, or local
    provider = os.environ.get("LLM_PROVIDER", "huggingface")
    logging.info(f"Using LLM provider: {provider}")

    for persona in PERSONAS:
        collect_replies(persona, REPLIES_PER_PERSONA, OUTPUT_DATA_FILE, MODEL_NAME, run_id, provider=provider)

    total_duration = datetime.now() - total_start_time
    logging.info(f"Completed all LLM reply generation for run_id: {run_id} in {total_duration.total_seconds():.1f} seconds")
    logging.info(f"All replies saved to '{OUTPUT_DATA_FILE}'")
    logging.info("You can now run fairlearn_processor.py to analyze the data.")
