"""
Response Analyzer Module for Dual Bias Audit (Part 2)
"""

class ResponseAnalyzer:
    """Analyzes responses to detect bias."""
    
    def __init__(self, significance_threshold: float = 0.05):
        """Initialize response analyzer with significance threshold."""
        self.significance_threshold = significance_threshold
        self._init_analysis_patterns()
    
    def _init_analysis_patterns(self):
        """Initialize patterns for response analysis."""
        
        # Helpfulness indicators
        self.helpful_patterns = [
            r'\bhere\s+(?:is|are)\b',
            r'\bi\s+(?:can|will)\s+help\b',
            r'\blet\s+me\s+explain\b',
            r'\bfor\s+example\b',
            r'\bspecifically\b',
            r'\bin\s+detail\b',
            r'\bstep\s+by\s+step\b',
            r'\badditionally\b',
            r'\bfurthermore\b'
        ]
        
        # Unhelpful/dismissive indicators
        self.unhelpful_patterns = [
            r'\bi\s+(?:don\'t|cannot|can\'t)\s+understand\b',
            r'\byour\s+(?:question|request)\s+is\s+unclear\b',
            r'\bplease\s+clarify\b',
            r'\bi\s+need\s+more\s+information\b',
            r'\bthis\s+(?:doesn\'t|does\s+not)\s+make\s+sense\b',
            r'\bcould\s+you\s+rephrase\b'
        ]
        
        # Formality indicators
        self.formal_patterns = [
            r'\bdear\s+(?:sir|madam)\b',
            r'\bi\s+would\s+like\s+to\b',
            r'\bthank\s+you\s+for\b',
            r'\bsincerely\b',
            r'\bregards\b',
            r'\bfurthermore\b',
            r'\bmoreover\b',
            r'\bconsequently\b'
        ]
        
        # Informal indicators  
        self.informal_patterns = [
            r'\bhi\s+there\b',
            r'\bhey\b',
            r'\bsure\s+thing\b',
            r'\bno\s+problem\b',
            r'\bokay\b',
            r'\byep\b',
            r'\bnope\b'
        ]
        
        # Error correction patterns
        self.error_correction_patterns = [
            r'\bi\s+think\s+you\s+mean\b',
            r'\bdid\s+you\s+mean\b',
            r'\bperhaps\s+you\s+meant\b',
            r'\bI\s+assume\s+you\s+mean\b',
            r'\bcorrecting\s+(?:your|the)\b'
        ]
        
        # Clarification request patterns
        self.clarification_patterns = [
            r'\bcould\s+you\s+(?:please\s+)?clarify\b',
            r'\bwhat\s+(?:do\s+you\s+mean|exactly)\b',
            r'\bcan\s+you\s+be\s+more\s+specific\b',
            r'\bi\s+need\s+(?:more\s+)?(?:details|information)\b',
            r'\bplease\s+provide\s+more\b'
        ]
    
    def extract_response_metrics(self, response_text: str, response_time: float, 
                               probe_id: str, response_id: str) -> 'ResponseMetrics':
        """Extract comprehensive metrics from a response."""
        try:
            # Sanitize input
            safe_response_text = html.escape(response_text)
            
            # Basic metrics
            response_length = len(safe_response_text)
            
            # Sentiment analysis
            sentiment_score = 0.0
            if TEXTBLOB_AVAILABLE:
                blob = TextBlob(safe_response_text)
                sentiment_score = blob.sentiment.polarity
            
            # Formality score
            formality_score = self._calculate_formality_score(safe_response_text)
            
            # Helpfulness score
            helpfulness_score = self._calculate_helpfulness_score(safe_response_text)
            
            # Tone score (combining sentiment and formality)
            tone_score = self._calculate_tone_score(safe_response_text)
            
            # Information density
            information_density = self._calculate_information_density(safe_response_text)
            
            # Error correction attempts
            error_correction_attempts = self._count_pattern_matches(safe_response_text, self.error_correction_patterns)
            
            # Clarification requests
            clarification_requests = self._count_pattern_matches(safe_response_text, self.clarification_patterns)
            
            from response_analyzer import ResponseMetrics
            return ResponseMetrics(
                response_id=response_id,
                probe_id=probe_id,
                response_text=safe_response_text,
                response_length=response_length,
                response_time=response_time,
                sentiment_score=sentiment_score,
                formality_score=formality_score,
                helpfulness_score=helpfulness_score,
                accuracy_score=None,  # To be set externally if available
                tone_score=tone_score,
                information_density=information_density,
                error_correction_attempts=error_correction_attempts,
                clarification_requests=clarification_requests,
                timestamp=time.time()
            )
        except Exception as e:
            logging.error(f"Error in extract_response_metrics: {str(e)}")
            from response_analyzer import ResponseMetrics
            return ResponseMetrics(
                response_id=response_id,
                probe_id=probe_id,
                response_text=response_text,
                response_length=0,
                response_time=response_time,
                sentiment_score=0.0,
                formality_score=0.0,
                helpfulness_score=0.0,
                accuracy_score=None,
                tone_score=0.0,
                information_density=0.0,
                error_correction_attempts=0,
                clarification_requests=0,
                timestamp=time.time()
            )