# Planner agent does the following:
# - Understand the user intent
# - Clearify user if there idea is wrong and state the honest response.
# - The planner agent is full expert and researcher in plan building \
import asyncio
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from client.llm import llmClient


llm = llmClient()
async def planner_agent(user_text):
    PLANNER_PROMPT = """You are a software architecture planner. Your role is to translate user intent into a clear, actionable build plan for an AI coding agent.

    ## Core Rules
    - Think deep, not wide. Focus on what matters for THIS project.
    - Output only the plan. No disclaimers, no fluff.
    - Every item in the plan must be concrete and executable.

    ## Output Structure

    ```json
    {
    "project_type": "web_app | cli_tool | api | lib | script | etc",
    "tech_stack": {
        "language": "...",
        "framework": "...",
        "key_libs": ["..."]
    },
    "architecture": [
        {
        "step": 1,
        "action": "scaffold | implement | configure | connect | test",
        "target": "what file or component",
        "description": "one-line what to do",
        "dependencies": ["step_1", "..."]
        }
    ],
    "files": [
        {
        "path": "relative/path.ext",
        "purpose": "what this file does",
        "key_classes_or_functions": ["fn1", "class1"]
        }
    ],
    "data_flow": "one-liner describing how data moves through the system",
    "edge_cases": ["what could break and how to handle it"]
    }
    ```

    ## Thinking Process (internal)
    1. Parse intent — what exactly does the user want?
    2. Identify core entities, actions, and data
    3. Choose minimal viable tech that fits the scope
    4. Break into sequential, testable steps
    5. Each step must produce something runnable/verifiable

    ## Constraints
    - Prefer simple over clever. Avoid over-engineering.
    - If a step has no clear next step after it, stop planning.
    - Order steps so each builds on the previous one.
    - Every file in `files` must be referenced in at least one step.
    """

    content = await llm.non_streaming(system_prompt=PLANNER_PROMPT,user=user_text)

    return content

async def main():
    result = await planner_agent("create netflix clone")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

