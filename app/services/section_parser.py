import re


def extract_skills_section(
    text: str
):

    pattern = re.compile(
        r"(skills|technical skills)(.*?)(experience|projects|education|certifications|achievements|$)",
        re.IGNORECASE | re.DOTALL
    )

    match = pattern.search(text)

    if match:

        return match.group(2).strip()

    return ""