"""
Response Analyzer Module for Dual Bias Audit (Part 5)
"""

def _calculate_formality_score(self, text: str) -> float:
    """Calculate formality score of text."""
    formal_count = self._count_pattern_matches(text, self.formal_patterns)
    informal_count = self._count_pattern_matches(text, self.informal_patterns)
    
    words = len(text.split())
    if words == 0:
        return 0.5
    
    # Normalize by text length
    formal_ratio = formal_count / words
    informal_ratio = informal_count / words
    
    # Calculate formality score (0 = informal, 1 = formal)
    formality_score = 0.5 + (formal_ratio - informal_ratio) * 5  # Scale factor
    return max(0, min(1, formality_score))

def _calculate_helpfulness_score(self, text: str) -> float:
    """Calculate helpfulness score of text."""
    helpful_count = self._count_pattern_matches(text, self.helpful_patterns)
    unhelpful_count = self._count_pattern_matches(text, self.unhelpful_patterns)
    
    # Additional positive indicators
    positive_words = ['happy', 'glad', 'pleased', 'delighted', 'comprehensive', 'detailed', 'thorough', 'explain', 'help', 'provide', 'assist']
    negative_words = ['unclear', 'confused', 'difficult', 'unable', 'cannot', "can't", "don't", 'understand']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    words = len(text.split())
    if words == 0:
        return 0.5
    
    # Combine pattern matches and word counts
    total_helpful = helpful_count + positive_count
    total_unhelpful = unhelpful_count + negative_count
    
    # Normalize by text length
    helpful_ratio = total_helpful / words
    unhelpful_ratio = total_unhelpful / words
    
    # Calculate helpfulness score (0 = unhelpful, 1 = helpful)
    # Base score of 0.5, adjusted by helpful/unhelpful indicators
    helpfulness_score = 0.5 + (helpful_ratio - unhelpful_ratio) * 5  # Scale factor
    return max(0, min(1, helpfulness_score))

def _calculate_tone_score(self, text: str) -> float:
    """Calculate overall tone score combining multiple factors."""
    sentiment_score = 0.0
    if TEXTBLOB_AVAILABLE:
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
    
    formality = self._calculate_formality_score(text)
    
    # Combine sentiment and formality for tone
    # Positive sentiment + higher formality = better tone
    tone_score = (sentiment_score + 1) / 2 * 0.6 + formality * 0.4
    return max(0, min(1, tone_score))

def _calculate_information_density(self, text: str) -> float:
    """Calculate information density (content words per total words)."""
    words = text.lower().split()
    if not words:
        return 0
    
    # Common stop words
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'among', 'within', 'without', 'is', 'are', 'was',
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
    }
    
    content_words = [word for word in words if word not in stop_words and len(word) > 2]
    return len(content_words) / len(words)

def _count_pattern_matches(self, text: str, patterns: List[str]) -> int:
    """Count total matches for all patterns in text."""
    total_matches = 0
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        total_matches += len(matches)
    return total_matches