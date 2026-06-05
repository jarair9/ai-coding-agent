import json
from config.setting import get_client, get_model
from openai import AuthenticationError, RateLimitError, APIError, APIConnectionError, APITimeoutError, OpenAIError
import asyncio
from tools.base import execute_tool
from tools.tool_schema import Tools
from context.memory import ContextManager
from system.prompt import prompt

manager = ContextManager()

class llmClient:
    def __init__(self):
        self.client = get_client()
        self.model = get_model()

    async def streaming_response(self, max_retries=3, MAX_ROUNDS=10):
        manager.adding_system_prompt(prompt=prompt)
        
        for _ in range(MAX_ROUNDS):
            
            for attempts in range(max_retries + 1):
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=manager.messages,
                        tools=Tools,
                        stream=True
                    )

                    accumulated_tool_calls = {}

                    async for chunk in response:
                        delta = chunk.choices[0].delta
                        finish_reason = chunk.choices[0].finish_reason

                        # 1. Stream text content
                        if delta.content is not None:
                            yield {"type": "text", "content": delta.content}

                        # 2. Final answer 
                        if finish_reason == "stop":
                            yield {"type": "complete", "finish_reason": "stop"}
                            return

                        # 3. Accumulate tool call pieces (streaming)
                        if hasattr(delta, "tool_calls") and delta.tool_calls is not None:
                            for tc in delta.tool_calls:
                                idx = tc.index
                                if idx not in accumulated_tool_calls:
                                    accumulated_tool_calls[idx] = {
                                        "id": "",
                                        "name": "",
                                        "arguments": "",
                                        "index": idx
                                    }
                                if tc.id:
                                    accumulated_tool_calls[idx]["id"] = tc.id
                                if tc.function:
                                    if tc.function.name:
                                        accumulated_tool_calls[idx]["name"] = tc.function.name
                                    if tc.function.arguments:
                                        accumulated_tool_calls[idx]["arguments"] += tc.function.arguments

                        # 4. When the LLM ends a turn with tool calls
                        if finish_reason == "tool_calls" and accumulated_tool_calls:
                            for tool_data in list(accumulated_tool_calls.values()):
                                if not tool_data["name"]:
                                    continue
                                # Parse arguments
                                try:
                                    tool_args = json.loads(tool_data["arguments"]) if tool_data["arguments"] else {}
                                except json.JSONDecodeError:
                                    tool_args = tool_data["arguments"]

                                tool_name = tool_data["name"]
                                tool_call_id = tool_data["id"]

                                
                                yield {
                                    "type": "tool_call",
                                    "tool_call": {
                                        "tool_name": tool_name,
                                        "tool_args": tool_args
                                    }
                                }

                                # Store tool call in context
                                manager.add_tool_call(tool_call_id, tool_name, tool_args)

                                # Execute the tool
                                result = await execute_tool(name=tool_name, **tool_args)

                                # Store tool result (must use "content" key internally)
                                manager.add_tool_result(tool_call_id, tool_name, result)

                                # Yield result to UI
                                yield {"type": "tool_result", "tool_result": result}

                            
                            accumulated_tool_calls.clear()
                            
                            break   

                        # 5. Handle usage statistics (if present)
                        if hasattr(chunk, "usage") and chunk.usage:
                            prompt_tokens = chunk.usage.prompt_tokens
                            completion_tokens = chunk.usage.completion_tokens
                            cached_tokens = 0
                            if hasattr(chunk.usage, "prompt_tokens_details") and chunk.usage.prompt_tokens_details:
                                cached_tokens = getattr(chunk.usage.prompt_tokens_details, "cached_tokens", 0)
                            manager.usage_tracker(prompt_tokens, completion_tokens, cached_tokens)

                    break

                except RateLimitError as e:
                    if attempts < max_retries:
                        await asyncio.sleep(2 ** attempts)
                        
                        yield {"type": "status", "message": f"Rate limit, retrying in {2**attempts}s"}
                    else:
                        yield {"type": "error", "error": f"Rate limit exceeded: {e}"}
                        return
                except APIConnectionError as e:
                    if attempts < max_retries:
                        await asyncio.sleep(2 ** attempts)
                        yield {"type": "status", "message": f"Connection error, retrying in {2**attempts}s"}
                    else:
                        yield {"type": "error", "error": f"Connection error: {e}"}
                        return
                except APITimeoutError as e:
                    if attempts < max_retries:
                        await asyncio.sleep(2 ** attempts)
                        yield {"type": "status", "message": f"Timeout, retrying in {2**attempts}s"}
                    else:
                        yield {"type": "error", "error": f"API timeout: {e}"}
                        return
                except APIError as e:
                    yield {"type": "error", "error": f"API Error: {e}"}
                    return
                except AuthenticationError as e:
                    yield {"type": "error", "error": f"Authentication Error: {e}"}
                    return
                except OpenAIError:
                    yield {"type" : "error","error": "Missing Credentails add API_KEY and BASE_URL in env file and try Again..."}
                    return
        # Max rounds reached without final answer
        yield {"type": "error", "error": f"Max rounds ({MAX_ROUNDS}) reached"}

    async def non_streaming(self, system_prompt: str, user, max_retries=3):
        for attempts in range(max_retries + 1):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user}],
                    stream=False
                )
                return response.choices[0].message.content
            except APIConnectionError as e:
                if attempts < max_retries:
                    await asyncio.sleep(2 ** attempts)
                else:
                    return f"Connection Error: {e}"
            except RateLimitError:
                if attempts < max_retries:
                    await asyncio.sleep(2 ** attempts)
                else:
                    return "Rate Limited. Please try again."
            except APITimeoutError as e:
                if attempts < max_retries:
                    await asyncio.sleep(2 ** attempts)
                else:
                    return f"API timeout: {e}"
            except AuthenticationError as e:
                if attempts < max_retries:
                    await asyncio.sleep(2 ** attempts)
                else:
                    return f"Authentication Error: {e}"
            except APIError as e:
                return f"API Error: {e}"