# ContextManager: message stack, token counter, tool pruning
from dataclasses import dataclass
import json
from pathlib import Path
from config.setting import get_context_window, get_model,get_tokenizer,estimate_tokens

@dataclass
class ContextManager:
    messages=[]

    # autuall token 
    prompt_token : int = 0
    completion_token: int = 0
    total_token : int= 0
    cached_token: int = 0

    tokenizer = get_tokenizer(get_model())
    # estimated token for pruning
    token_usage:  int = 0 # default to 0
    CONTEXT_WINDOW = get_context_window()

    threshold_tokens = int((CONTEXT_WINDOW * 80) / 100)   # 6553 tokens (80%)
    critical_tokens = int((CONTEXT_WINDOW * 95) / 100)    # 7782 tokens (95%)


    def usage_tracker(self,prompt_token,completion_token,cached_token):
        # extracting tokens
        self.prompt_token += prompt_token
        self.completion_token += completion_token
        self.total_token += prompt_token + completion_token
        self.cached_token += cached_token
        
    def usage_stats(self):
        return {
            "prompt": self.prompt_token,
            "completion": self.completion_token,
            "total": self.prompt_token + self.completion_token,
            "cached": self.cached_token
        }
    def count_token(self ,messages) -> None:
        for msg in messages:
            token = len(self.tokenizer(msg["content"]))
            self.token_usage += token

    def prune(self, messages, keep_last=15):
        system_msg = []
        othermsg = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg.append(msg)
            else:
                othermsg.append(msg)
        
        if self.token_usage >= self.threshold_tokens and self.token_usage < self.critical_tokens:
            recent = othermsg[-keep_last:]
            
        elif self.token_usage >= self.critical_tokens:
            keep_last = 5  # Keep fewer messages when critical
            recent = othermsg[-keep_last:]
            
        else:
            return messages
        
        pruned = system_msg + recent
       
        return pruned
    def adding_system_prompt(self,prompt):
        self.messages.append({"role": "system", "content": prompt})

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
            

    def add_assistant_text(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
            

    def add_tool_call(self, tool_call_id: str, tool_name: str, arguments: dict):
        self.messages.append({
                "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(arguments)
                        }
                }]
            })
        
        
    def add_tool_result(self, tool_call_id: str, tool_name: str, result: any):
        self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_name,
                "content": str(result)
            })
        
         
    
                


