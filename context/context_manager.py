# ContextManager: message stack, token counter, tool pruning
from dataclasses import dataclass, field
import json
from pathlib import Path
from config.utils import get_context_window,get_tokenizer,estimate_tokens
from config.config import get_model


@dataclass
class ContextManager:
    messages: list = field(default_factory=list)
    
    tokenizer = get_tokenizer(get_model())
    

    CONTEXT_WINDOW = get_context_window()
    threshold_tokens = int((CONTEXT_WINDOW * 80) / 100)   
    critical_tokens = int((CONTEXT_WINDOW * 95) / 100)  
    
  
    def count_token(self, msgs) -> int:
        total = 0
        for msg in msgs:
            msg_str = json.dumps(msg,default=str, ensure_ascii=False)
            if self.tokenizer is None:

                token = len(estimate_tokens(msg_str))
                total += token
            else:
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
    
    
    def auto_prune(self):
        pruned = self.prune(self.messages)
        if len(pruned) < len(self.messages):
            print("Pruning messages")
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
       
        
         
    
                


