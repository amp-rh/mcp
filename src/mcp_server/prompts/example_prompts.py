from fastmcp import FastMCP


def register_example_prompts(mcp: FastMCP) -> None:
    @mcp.prompt
    def code_review(code: str, language: str = "python") -> str:
        return f"""Review this {language} code for:
- Correctness and potential bugs
- Performance considerations
- Best practices and code style

```{language}
{code}
```

Provide specific, actionable feedback."""

    @mcp.prompt
    def summarize_document(document: str, max_words: int = 100) -> str:
        return f"""Summarize the following document in {max_words} words or less.

Focus on:
- Key points and main ideas
- Important facts and figures
- Actionable takeaways

Document:
{document}"""

    @mcp.prompt
    def explain_concept(concept: str, audience: str = "beginner") -> str:
        return f"""Explain the concept of "{concept}" for a {audience} audience.

Include:
- A clear definition
- Real-world examples
- Common misconceptions
- Related concepts"""

