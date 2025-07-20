class Transformation:
    def _perform_zy_swap(self, word: str) -> str:
        """Performs a ZY swap on a single word, maintaining case."""
        swapped_chars = []
        has_z_or_y = False
        for char in word:
            if char.lower() == 'z':
                swapped_chars.append('y' if char.islower() else 'Y')
                has_z_or_y = True
            elif char.lower() == 'y':
                swapped_chars.append('z' if char.islower() else 'Z')
                has_z_or_y = True
            else:
                swapped_chars.append(char)
        # If no z or y was found, return the original word
        return "".join(swapped_chars) if has_z_or_y else word

    def _perform_qwertz_swap(self, word: str) -> str:
        """Performs a QWERTZ swap on a single word, maintaining case."""
        return word.translate(str.maketrans('zyqZYQ', 'yzqYZQ'))

    def _perform_o2cyrillic_swap(self, word: str) -> str:
        """Swaps Latin 'o' with Cyrillic 'о' (and 'O' with 'О'), maintaining case."""
        swapped_chars = []
        has_o_or_cyrillic_o = False
        for char in word:
            if char == 'o':
                swapped_chars.append(chr(0x043E)) # Cyrillic small o
                has_o_or_cyrillic_o = True
            elif char == 'O':
                swapped_chars.append(chr(0x041E)) # Cyrillic capital O
                has_o_or_cyrillic_o = True
            elif char == chr(0x043E): # If already Cyrillic o, swap back
                swapped_chars.append('o')
                has_o_or_cyrillic_o = True
            elif char == chr(0x041E): # If already Cyrillic O, swap back
                swapped_chars.append('O')
                has_o_or_cyrillic_o = True
            else:
                swapped_chars.append(char)
        # If no relevant 'o' was found, return the original word
        return "".join(swapped_chars) if has_o_or_cyrillic_o else word

    def _get_transformation_function(self, swap_type: str):
        """Returns the appropriate transformation function based on swap_type."""
        if swap_type == 'zy':
            return self._perform_zy_swap
        elif swap_type == 'o2cyrillic':
            return self._perform_o2cyrillic_swap
        elif swap_type == 'qwertz':
            return self._perform_qwertz_swap
        else:
            raise ValueError(f"Unsupported swap_type: {swap_type}")

    def _get_fake_memory_function(self, swap_type: str):
        """Returns the appropriate transformation function based on swap_type."""
        if swap_type == 'zy':
            return self._perform_o2cyrillic_swap
        elif swap_type == 'o2cyrillic':
            return self._perform_zy_swap
        else:
            raise ValueError(f"Unsupported swap_type: {swap_type}")

    def _get_second_transformation(self, word: str) -> str:
        """
        Applies a second, distinct transformation for when the model is stuck.
        For 'lucky', it's a specific Cyrillic 'c' swap.
        For other words, it's a simple reversal.
        """
        if word.lower() == "lucky":
            # Specific case as requested: 'lucky' -> 'luсky' (Cyrillic 'c')
            return word.replace('c', 'с') # Replace Latin 'c' with Cyrillic 'с' (U+0441)
        else:
            return word[::-1] # Generic fallback: reverse the word

    def _is_correct_zy_swap(self, original: str, model_swapped: str) -> bool:
        """
        Checks if the model's swap is correct according to the ZY rule.
        Compares expected swap (case-insensitive) to model's swapped output.
        """
        expected_swap = self._perform_zy_swap(original)
        return expected_swap.lower() == model_swapped.lower()


    def _is_correct_o2cyrillic_swap(self, original: str, model_swapped: str) -> bool:
        """
        Checks if the model's swap is correct according to the O->Cyrillic-O rule.
        Compares expected swap (case-insensitive) to model's swapped output.
        """
        expected_swap = self._perform_o2cyrillic_swap(original)
        return expected_swap.lower() == model_swapped.lower()
