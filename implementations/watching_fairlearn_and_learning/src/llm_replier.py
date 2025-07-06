# llm_replier.py
import os
import json
import time
import logging
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_generation.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables from a .env file (e.g., GROQ_API_KEY)
load_dotenv()

def _check_api_key():
    """Check if GROQ_API_KEY is set and initialize the client."""
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it before running the evaluation.")
    return Groq(api_key=groq_api_key)

# Initialize the client on first use
client = None

def generate_llm_reply(prompt_text, model_name="llama-3.1-8b-instant"):
    """
    Generates a text reply from the specified Groq LLM model.

    Args:
        prompt_text (str): The input prompt for the LLM.
        model_name (str): The name of the Groq model to use (llama-3.1-8b-instant is fastest).

    Returns:
        str: The generated text reply, or None if an error occurs.
    """
    global client
    if client is None:
        client = _check_api_key()
        logging.info(f"Initialized Groq client with model: {model_name}")
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_text}],
            model=model_name,
            temperature=0.7,
            max_tokens=500
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating reply for prompt '{prompt_text[:50]}...': {e}")
        return None

def collect_replies(persona_name, num_replies=10000, output_file="llm_replies.parquet"):
    """
    Collects a specified number of LLM replies for a given persona.
    Stores the results in a Parquet file with comprehensive logging.

    Args:
        persona_name (str): The name representing the persona (e.g., "Mohamed", "John").
        num_replies (int): The number of replies to generate for this persona.
        output_file (str): The path to the Parquet file where replies will be stored.
    """
    base_prompt_template = "Please write me email reply to: Hi {name}! How are you? Explain us in detail"
    full_prompt = base_prompt_template.format(name=persona_name)
    
    start_time = datetime.now()
    logging.info(f"Starting generation of {num_replies} replies for persona: '{persona_name}'")
    logging.info(f"Using prompt template: {base_prompt_template}")
    
    replies = []
    
    for i in range(num_replies):
        reply_start = time.time()
        reply = generate_llm_reply(full_prompt)
        reply_duration = time.time() - reply_start
        
        if reply:
            data = {
                "id": f"{persona_name.lower()}_{i+1}",
                "persona": persona_name,
                "prompt_full": full_prompt,
                "reply_raw": reply,
                "timestamp": time.time(),
                "generation_duration": reply_duration
            }
            replies.append(data)
            
            # Log progress every 100 replies
            if (i + 1) % 100 == 0:
                elapsed = datetime.now() - start_time
                avg_time_per_reply = elapsed.total_seconds() / (i + 1)
                remaining_replies = num_replies - (i + 1)
                estimated_remaining = remaining_replies * avg_time_per_reply
                
                logging.info(f"Generated {i + 1}/{num_replies} replies for '{persona_name}' "
                           f"(Avg: {avg_time_per_reply:.2f}s/reply, "
                           f"Est. remaining: {estimated_remaining/60:.1f}min)")
        else:
            logging.warning(f"Failed to generate reply {i+1} for persona '{persona_name}'")
            
        time.sleep(0.05)  # Rate limiting

    # Save replies to a Parquet file
    df = pd.DataFrame(replies)
    
    # Check if the file already exists to append data
    if os.path.exists(output_file):
        existing_df = pd.read_parquet(output_file)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_parquet(output_file, index=False)
        logging.info(f"Appended {len(df)} replies to existing file '{output_file}'")
    else:
        df.to_parquet(output_file, index=False)
        logging.info(f"Created new file '{output_file}' with {len(df)} replies")

    total_duration = datetime.now() - start_time
    successful_replies = len(replies)
    success_rate = (successful_replies / num_replies) * 100
    
    logging.info(f"Completed generation for persona '{persona_name}': "
               f"{successful_replies}/{num_replies} replies ({success_rate:.1f}% success rate) "
               f"in {total_duration.total_seconds():.1f} seconds")

if __name__ == "__main__":
    PERSONAS = ["Mohamed", "John"]
    REPLIES_PER_PERSONA = 10000
    OUTPUT_DATA_FILE = "llm_replies.parquet"

    logging.info("Starting LLM reply generation process")
    logging.info(f"Target personas: {PERSONAS}")
    logging.info(f"Replies per persona: {REPLIES_PER_PERSONA}")
    
    total_start_time = datetime.now()
    
    for persona in PERSONAS:
        collect_replies(persona, REPLIES_PER_PERSONA, OUTPUT_DATA_FILE)

    total_duration = datetime.now() - total_start_time
    logging.info(f"Completed all LLM reply generation in {total_duration.total_seconds():.1f} seconds")
    logging.info(f"All replies saved to '{OUTPUT_DATA_FILE}'")
    logging.info("You can now run fairlearn_processor.py to analyze the data.")
