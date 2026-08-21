class usage_tracker:
    def __init__(self):
        
        self.prompt_token = 0
        self.completions_tokens = 0
        self.total_tokens = 0
        self.reasoning_tokens = 0
        self.cached_token = 0
        
    def usage_stats(self,prompt_tokens,
        completions_tokens,
        total_tokens,
        reasoning_tokens,
        cached_token
        ) -> None:
        
        # Covering edge cases is important
        if prompt_tokens:
            self.prompt_token += prompt_tokens
        if completions_tokens:
            self.completions_tokens += completions_tokens
        if total_tokens:
            self.total_tokens += total_tokens
        if cached_token:
            self.cached_token += cached_token
        if reasoning_tokens is not None:
            self.reasoning_tokens += reasoning_tokens
        
    
    def return_usage(self) -> dict:
        
        return {
            "prompt_tokens": self.prompt_token,
            "completions_tokens" :self.completions_tokens,
            "total_tokens": self.total_tokens,
            "reasoning_token": self.reasoning_tokens,
            "cached_token": self.cached_token
            }
        