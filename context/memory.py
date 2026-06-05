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
    CONTEXT_WINDOW = get_context_window()

    threshold_tokens = int((CONTEXT_WINDOW * 80) / 100)   
    critical_tokens = int((CONTEXT_WINDOW * 95) / 100)    


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
        total = 0
        for msg in messages:
            msg_str = json.dumps(msg,default=str, ensure_ascii=False)
            token = len(self.tokenizer(msg_str))
            total += token
            
        return total

    def prune(self, messages, keep_last=15, keep_critical=5):
       
        system_msgs = [m for m in messages if m.get("role") == "system"]
        
        other_msgs = [m for m in messages if m.get("role") != "system"]

        
        token_count = self.count_token(other_msgs)

       
        if token_count < self.threshold_tokens:
            return messages

        if token_count >= self.critical_tokens:
            keep = keep_critical
        else:
            keep = keep_last
            
        recent = other_msgs[-keep:] if other_msgs else []
        pruned = system_msgs + recent
        return pruned
    
    def auto_prune(self,):
        pruned = self.prune(self.messages)
        if len(pruned) < len(self.messages):
            self.messages = pruned
            
            
    
    def adding_system_prompt(self,prompt):
        self.messages.append({"role": "system", "content": prompt})

    def add_user_message(self, content: str):
        self.messages.append({"role": "user", "content": content})
            

    def add_assistant_text(self, content: str):
        self.messages.append({"role": "assistant", "content": content})
            

    def add_tool_call(self, tool_call_id: str, tool_name: str, arguments: dict):
        self.messages.append({
                "role": "assistant",
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
        
         
    
                


