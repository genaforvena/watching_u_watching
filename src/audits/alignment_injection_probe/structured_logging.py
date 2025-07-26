import json
from datetime import datetime

def log_turn_data(turn_num, prompt, response, alignment_score, false_memories):
    data = {
        'timestamp': datetime.now().isoformat(),
        'turn': turn_num,
        'prompt_length': len(prompt),
        'response_length': len(response),
        'alignment_score': alignment_score,
        'false_memory_count': len(false_memories),
        'response_text': response
    }

    filename = f'probe_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jsonl'
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')
    return filename
