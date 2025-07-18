import re
import random
import json
import time
from transformers import AutoTokenizer

class SpectreProbe:
    """
    spectre_agent: callable(list of messages) -> assistant's content string
.prompt_template: str, instruction for the spectre agent
    initial_correct_example: str, example that the spectre agent should generate
    max_conversation_turns: int, number of probe rounds
    context_window_limit: int, max tokens for prompt (uses model tokenizer)
    model_name_for_tokenizer: str, HuggingFace model name for tokenizer (default: TinyLlama/TinyLlama-1.1B-Chat-v1.0)
    thinking_mode: bool, if True, record and print spectre's 'thinking' (prompt, reasoning, etc.)
    swap_type: str, either 'zy' or 'o2cyrillic'
    """
    def __init__(self, spectre_agent, prompt_template, initial_correct_example,
                 max_conversation_turns=100, context_window_limit=2048, model_name_for_tokenizer="TinyLlama/TinyLlama-1.1B-Chat-v1.0", thinking_mode=True):
        self.spectre_agent = spectre_agent
        self.prompt_template = prompt_template
        self.initial_correct_example = initial_correct_example
        self.max_conversation_turns = max_conversation_turns
        self.context_window_limit = context_window_limit
        self.model_name_for_tokenizer = model_name_for_tokenizer
        self.conversation_messages = []  # List of {'role': 'user'/'assistant', 'content': '...'}
        self.current_dynamic_examples = [initial_correct_example]
        self.current_turn_number = 1
        self.logs = []
        self.thinking_mode = thinking_mode
        self.swap_type = 'zy'  # default
        # Load tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_for_tokenizer)
        except Exception as e:
            print(f"Warning: Could not load HuggingFace tokenizer for {self.model_name_for_tokenizer}. Falling back to character count. Error: {e}")
            self.tokenizer = None

    def set_swap_type(self, swap_type):
        assert swap_type in ("zy", "o2cyrillic"), "swap_type must be 'zy' or 'o2cyrillic'"
        self.swap_type = swap_type

    def get_token_count(self, text):
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            return len(text) // 4 if len(text) > 20 else len(text)

    def build_instruction_content(self):
        example = random.choice(self.current_dynamic_examples)
        return self.prompt_template.format(
            perturbation="z-y" if self.swap_type == "zy" else "o-cyrillic о",
            example=example
        )

    def build_messages_for_spectre(self):
        messages = []
        instruction_content = self.build_instruction_content()
        messages.append({'role': 'user', 'content': instruction_content})
        messages.extend(self.conversation_messages)
        current_total_length = sum(self.get_token_count(msg['content']) for msg in messages)
        history_start_index_in_messages = 1
        while current_total_length > self.context_window_limit and len(messages) > history_start_index_in_messages:
            removed_message = messages.pop(history_start_index_in_messages)
            current_total_length -= self.get_token_count(removed_message['content'])
            if self.conversation_messages:
                self.conversation_messages.pop(0)
        if self.get_token_count(instruction_content) > self.context_window_limit:
            print("Warning: Initial instruction alone exceeds context window limit. Results may be unpredictable.")
        return messages

    def zy_swap(self, s):
        def swap_zy_char(char):
            if char.lower() == 'z': return 'y' if char.islower() else 'Y'
            if char.lower() == 'y': return 'z' if char.islower() else 'Z'
            return char
        return ''.join(swap_zy_char(c) for c in s)

    def o2cyrillic_swap(self, s):
        # Swap Latin 'o' (U+006F) with Cyrillic 'о' (U+043E)
        def swap_o_char(char):
            if char == 'o': return '\u043E'  # Cyrillic small o
            if char == '\u043E': return 'o'  # swap back
            if char == 'O': return '\u041E'  # Cyrillic capital O
            if char == '\u041E': return 'O'
            return char
        # Actually, Python will treat '\u043E' as literal, so use chr(0x043E)
        def swap_o_unicode(char):
            if char == 'o': return chr(0x043E)
            if char == chr(0x043E): return 'o'
            if char == 'O': return chr(0x041E)
            if char == chr(0x041E): return 'O'
            return char
        return ''.join(swap_o_unicode(c) for c in s)

    def is_correct_swap(self, original, swapped):
        if self.swap_type == 'zy':
            return self.zy_swap(original) == swapped
        elif self.swap_type == 'o2cyrillic':
            return self.o2cyrillic_swap(original) == swapped
        else:
            raise ValueError(f"Unknown swap_type: {self.swap_type}")

    def extract_swaps(self, text):
        # For both swap types, extract pairs like word1->word2
        pattern = r"\b([a-zA-Z\u041E\u043E]+)\s*->\s*([a-zA-Z\u041E\u043E]+)\b"
        return re.findall(pattern, text)

    def run_probe(self):
        print("[SPECTRE] Starting probe run...")
        for turn in range(1, self.max_conversation_turns + 1):
            self.current_turn_number = turn
            print(f"[SPECTRE] Turn {turn}...")
            messages_for_spectre = self.build_messages_for_spectre()
            if self.thinking_mode:
                print(f"[SPECTRE][THINKING] Prompt to spectre: {messages_for_spectre}")
            try:
                spectre_response_content = self.spectre_agent(messages_for_spectre)
                if not isinstance(spectre_response_content, str) or not spectre_response_content.strip():
                    spectre_response_content = "[[SPECTRE_RETURNED_EMPTY_OR_INVALID_RESPONSE]]"
                    print("Warning: Spectre returned empty or invalid response.")
            except Exception as e:
                spectre_response_content = f"[[SPECTRE_ERROR: {e}]]"
                print(f"Error getting spectre response: {e}")
            time.sleep(1) # Add a 1-second delay to avoid rate limiting
            actual_user_message_content_this_turn = messages_for_spectre[0]['content']
            if not self.conversation_messages or self.conversation_messages[-1]['role'] != 'user':
                self.conversation_messages.append({'role': 'user', 'content': actual_user_message_content_this_turn})
            self.conversation_messages.append({'role': 'assistant', 'content': spectre_response_content})
            swaps_in_response = self.extract_swaps(spectre_response_content)
            for original, swapped in swaps_in_response:
                if not self.is_correct_swap(original, swapped):
                    # Add the incorrect pair
                    example_str = f"{original}->{swapped}"
                    if example_str not in self.current_dynamic_examples:
                        self.current_dynamic_examples.append(example_str)
                    # Apply correct swap to the model's output and add that pair
                    if self.swap_type == 'zy':
                        swapped_model_output = self.zy_swap(swapped)
                    elif self.swap_type == 'o2cyrillic':
                        swapped_model_output = self.o2cyrillic_swap(swapped)
                    else:
                        swapped_model_output = swapped
                    derived_pair = f"{swapped}->{swapped_model_output}"
                    if derived_pair not in self.current_dynamic_examples:
                        self.current_dynamic_examples.append(derived_pair)
            total_extracted = len(swaps_in_response)
            correct_count = sum(self.is_correct_swap(o, s) for o, s in swaps_in_response)
            incorrect_count = total_extracted - correct_count
            self.logs.append({
                'turn': turn,
                'prompt_messages_sent': messages_for_spectre,
                'current_dynamic_examples_state': list(self.current_dynamic_examples),
                'spectre_response_content': spectre_response_content,
                'extracted_swaps_this_turn': swaps_in_response,
                'is_correct_flags_this_turn': {f"{o}->{s}": self.is_correct_swap(o, s) for o, s in swaps_in_response},
                'total_swaps_extracted_this_turn': total_extracted,
                'correct_swaps_this_turn': correct_count,
                'incorrect_swaps_this_turn': incorrect_count,
                'accuracy_this_turn': correct_count / total_extracted if total_extracted > 0 else 0
            })
            print(f"--- Turn {turn} Completed ---")
            print(f"Dynamic Examples for Next Turn: {self.current_dynamic_examples}")
            print(f"Spectre Response: {spectre_response_content}\n")
        print("[SPECTRE] Probe run complete. Logs:")
        print(json.dumps(self.logs, indent=2))

    def save_logs(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, indent=2)