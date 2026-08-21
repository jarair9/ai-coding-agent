## Inputs
# Region / market → us, pk, etc. (affects results)
# Language → en, ur, etc.
# Result count → number of results to return
# Filters → safe search, freshness (e.g., last 24h)


from ddgs import DDGS
import asyncio


async def websearch(query , result = 10):

    # using duckduckgo search which is safe.
    try:
        results = DDGS().text(
            query= query,
            region="us-en",
            safesearch="off",
            timelimit="y",
            max_results=result,
            page= 1,
            backend="auto"
        )

    except Exception as e:
        return {"type": "error", "error": f"Request failed: {e}" }
    if not results:
        return {f"No results found for: {query}" }

    output_lines = [f"search results for {query}"]

    for i, output in enumerate(results):
        output_lines.append(f"{i}. Title: {output['title']}")
        output_lines.append(f" URL {output['href']}")

        # check if 'body' exists and is not empty
        if output.get("body") and output["body"].strip():
            output_lines.append(f"   Snippet: {output['body']}")

        output_lines.append("")


    return {"Content":"\n".join(output_lines),
            "results": len(results)}

# wait = asyncio.run(websearch("AI"))
# print(wait)
