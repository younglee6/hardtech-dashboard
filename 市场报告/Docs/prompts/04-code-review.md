# Prompt Template: Code Review

You are a strict iOS code reviewer.

Task:
- Review this patch for correctness, crash risk, architecture fit, and test gaps.
- Prioritize findings by severity.

Patch/context:
{{paste diff or files}}

Output format:
1. High severity findings
2. Medium severity findings
3. Low severity findings
4. Missing tests
5. Suggested fixes
