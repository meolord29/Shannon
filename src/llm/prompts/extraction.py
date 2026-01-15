"""Extraction prompt templates."""
from src.llm.prompts.templates import PromptTemplate


EXTRACT_PAPER_STRUCTURE = PromptTemplate(
    name="extract_paper_structure",
    template="""Analyze this academic paper and extract its structure.

**Paper Title:** {title}

**Content:**
{content}

---

Return a JSON object with this exact structure:
```json
{{
    "summary": "2-3 sentence summary of the paper's main contribution",
    "key_contributions": [
        "First main contribution",
        "Second main contribution"
    ],
    "sections": [
        {{
            "title": "Section Title",
            "type": "introduction|background|methodology|results|discussion|conclusion",
            "summary": "Brief section summary",
            "page_range": "1-3"
        }}
    ],
    "main_concepts": [
        {{
            "name": "Concept Name",
            "definition": "Clear definition",
            "importance": "Why it matters in this paper"
        }}
    ],
    "algorithms": [
        {{
            "name": "Algorithm Name",
            "purpose": "What problem it solves",
            "inputs": ["input1", "input2"],
            "outputs": ["output1"]
        }}
    ],
    "suggested_tags": ["tag1", "tag2", "tag3"]
}}

Return ONLY valid JSON, no additional text or explanation.""",
description="Extract overall paper structure",
)

EXTRACT_SECTION_NOTES = PromptTemplate(
name="extract_section_notes",
template="""Create detailed study notes for this section from an academic paper.

Paper: {paper_title}
Section: {section_title}
Section Type: {section_type}

Content:
{content}

Create notes in this exact markdown format:
Summary

[2-3 sentence summary of this section]
Key Points

    [Key point 1]
    [Key point 2]
    [Continue as needed]

Concepts Introduced
[Concept Name]

[Definition and explanation]
[Another Concept]

[Definition and explanation]
Formulas

[formulainLaTeX]
Explanation: [What this formula represents]

[anotherformula]
Explanation: [What this formula represents]
Connections

    [[Related Concept 1]] - [How it relates]
    [[Related Concept 2]] - [How it relates]

Review Questions

    [Question that tests understanding]
    [Another question]""",
    description="Extract detailed notes from a section",
    )

EXTRACT_ALGORITHM = PromptTemplate(
name="extract_algorithm",
template="""Extract and document this algorithm from an academic paper.

Paper: {paper_title}
Context: {context}

Algorithm Description:
{content}

Document the algorithm in this format:
Algorithm: [Name]
Purpose

[What problem does this algorithm solve?]
Inputs

    input1 (type): [description]
    input2 (type): [description]

Outputs

    output1 (type): [description]

Prerequisites

    [Required knowledge]
    [Dependencies]

Steps

    [Step 1 description]
    [Step 2 description]
        [Sub-step if needed]
    [Continue as needed]

Pseudocode

function AlgorithmName(input1, input2):
    [pseudocode]
    return output

Complexity

    Time: O(?)
    Space: O(?)

Key Insights

    [Why does this work?]
    [Any clever techniques used?]

Example

[Simple worked example with concrete values]""",
description="Extract and document algorithms",
)

EXTRACT_FORMULAS = PromptTemplate(
name="extract_formulas",
template="""Extract all mathematical formulas from this text and explain each one.

Content:
{content}

For each formula found, provide:
Formula 1

[LaTeXrepresentation]

Variables:

    x: [meaning and units if applicable]
    y: [meaning and units if applicable]

Purpose: [What this formula computes]

Context: [When and why it's used]
Formula 2

[Continue for each formula...]

List ALL formulas found in the text, including inline equations.""",
description="Extract and explain mathematical formulas",
)

EXTRACT_KEY_CONCEPTS = PromptTemplate(
name="extract_key_concepts",
template="""Identify and explain the {max_concepts} most important concepts from this academic paper.

Paper: {paper_title}

Content:
{content}

For each concept:
[Concept Name]

Definition: [Clear, concise definition]

In This Paper: [How the concept is used or extended]

Related To: [[Concept1]], [[Concept2]]

Key Formula: (if applicable)
[relevantformula]

Intuition: [Plain language explanation]

Example: [Concrete example if helpful]

[Continue for each concept]""",
description="Extract and explain key concepts",
)

GENERATE_SUMMARY = PromptTemplate(
name="generate_summary",
template="""Generate a comprehensive summary of this academic paper.

Title: {title}
Abstract: {abstract}

Full Content:
{content}

Create a summary with these sections:
Overview

[1 paragraph explaining what this paper is about]
Problem Statement

[What problem does this paper address? Why is it important?]
Approach

[How do the authors solve the problem? What's novel about it?]
Key Contributions

    [Main contribution 1]
    [Main contribution 2]
    [Continue as needed]

Main Results

[Key findings and their significance]
Limitations

[Any limitations mentioned or apparent]
Future Directions

[Suggested future work]
Why It Matters

[Broader impact and who should read this paper]""",
description="Generate comprehensive paper summary",
)
