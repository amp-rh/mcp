from fastmcp import FastMCP

from mcp_server.prompts.example_prompts import register_example_prompts


class TestCodeReviewPrompt:
    def test_code_review_includes_code(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        code_review = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "code_review":
                code_review = prompt.fn
                break

        assert code_review is not None
        code = "print('hello')"
        result = code_review(code=code)
        assert code in result

    def test_code_review_includes_language(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        code_review = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "code_review":
                code_review = prompt.fn
                break

        assert code_review is not None
        result = code_review(code="code", language="javascript")
        assert "javascript" in result


class TestSummarizeDocumentPrompt:
    def test_summarize_includes_document(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        summarize_document = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "summarize_document":
                summarize_document = prompt.fn
                break

        assert summarize_document is not None
        document = "This is a test document."
        result = summarize_document(document=document)
        assert document in result

    def test_summarize_includes_word_limit(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        summarize_document = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "summarize_document":
                summarize_document = prompt.fn
                break

        assert summarize_document is not None
        result = summarize_document(document="doc", max_words=50)
        assert "50" in result


class TestExplainConceptPrompt:
    def test_explain_includes_concept(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        explain_concept = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "explain_concept":
                explain_concept = prompt.fn
                break

        assert explain_concept is not None
        result = explain_concept(concept="recursion")
        assert "recursion" in result

    def test_explain_includes_audience(self) -> None:
        mcp = FastMCP("test")
        register_example_prompts(mcp)

        explain_concept = None
        for prompt in mcp._prompt_manager._prompts.values():
            if prompt.name == "explain_concept":
                explain_concept = prompt.fn
                break

        assert explain_concept is not None
        result = explain_concept(concept="APIs", audience="expert")
        assert "expert" in result
