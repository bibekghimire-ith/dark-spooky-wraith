"""Personal portfolio site.

Edit PORTFOLIO_DATA below to change any text, link or image on the site.
Field names are a contract with templates/index.html (see Portfolio-PRD.md).

  owner          name, title, bio, email (all required, non-empty text)
  social_links   list of {label, url}; url starts with http://, https:// or mailto:
  skills         {category: [skill, ...]}
  projects       list of {title, description, tech_stack, image_url,
                 demo_link, code_link}; image_url is a path under static/
                 (for example "img/app.png") or an http(s) URL; the links are optional
  experience     list of {role, company, dates, highlights}; newest first

Unknown keys are ignored, so you can add notes or future sections freely.
"""

PORTFOLIO_DATA = {
    "owner": {
        "name": "Bibek Ghimire",
        "title": "Software Engineer",
        "bio": (
            "I build backend services and data ingestion pipelines for a SIEM platform. "
            "I came up through QA and test automation, so I design for reliability, "
            "testability and clear documentation from the first commit."
        ),
        "email": "your-email@example.com",  # TODO: use the address from your CV
    },
    "social_links": [
        # TODO: replace each url with the link behind the same label in your CV
        {"label": "GitHub", "url": "https://github.com/your-handle"},
        {"label": "LinkedIn", "url": "https://www.linkedin.com/in/your-handle"},
        {"label": "Credly", "url": "https://www.credly.com/users/your-handle"},
    ],
    "skills": {
        "Languages": ["Python", "SQL", "Bash", "Java (basic)"],
        "Backend and APIs": ["Flask", "REST APIs", "JWT", "OAuth", "Input validation"],
        "Testing and QA": [
            "Playwright (Python)", "Postman", "Cucumber", "RestAssured",
            "JMeter (basic)", "Xray", "Test strategy", "Regression testing",
        ],
        "Data": ["MongoDB", "SQLite", "Regex log parsing"],
        "Tools and platforms": [
            "Git", "Docker", "Jenkins", "Linux", "Bitbucket", "Confluence", "Jira",
        ],
    },
    "projects": [
        {
            "title": "Log Parser Regression Tool",
            "description": (
                "Internal tool that automates regression tests for log parsers, query "
                "validation of analytics content and application bundle checks. "
                "Cut manual testing time by 50%."
            ),
            "tech_stack": ["Python", "Regex", "SIEM"],
            "image_url": "img/log-parser-tool.png",  # add a screenshot or diagram
            "demo_link": "",
            "code_link": "",  # internal tool: leave empty unless you can share it
        },
        {
            "title": "Playwright Test Automation Framework",
            "description": (
                "Standardized API and end-to-end automation framework for internal web "
                "applications and SIEM plugin integrations, and streamlined QA "
                "procedures across teams."
            ),
            "tech_stack": ["Python", "Playwright", "API testing"],
            "image_url": "img/playwright-framework.png",
            "demo_link": "",
            "code_link": "",
        },
        {
            "title": "BDD API Automation Framework",
            "description": (
                "API test framework for a microservices-based lending platform, using "
                "a BDD approach so component tests are readable by stakeholders."
            ),
            "tech_stack": ["Java", "Cucumber", "RestAssured"],
            "image_url": "img/bdd-api-framework.png",
            "demo_link": "",
            "code_link": "",
        },
        {
            "title": "Traffic Sign Recognition",
            "description": (
                "Master's project: a multilayer perceptron written from scratch in "
                "NumPy to classify traffic signs from the GTSRB dataset."
            ),
            "tech_stack": ["Python", "NumPy", "Machine learning"],
            "image_url": "img/traffic-sign.png",
            "demo_link": "",
            "code_link": "https://github.com/your-handle/TrafficSignDetection",  # TODO: confirm
        },
    ],
    "experience": [
        {
            "role": "Software Engineer",
            "company": "Logpoint, Nepal",
            "dates": "May 2025 - Present",
            "highlights": [
                "Develop and maintain scalable backend services in Python (Flask), with RESTful APIs and third-party integrations.",
                "Implement authentication, authorization and security practices (JWT, OAuth, input validation) for secure API communication.",
                "Build and optimize data ingestion components for the SIEM platform.",
            ],
        },
        {
            "role": "Quality Assurance Engineer",
            "company": "Foneloan Pvt. Ltd., Nepal",
            "dates": "Oct 2024 - Apr 2025",
            "highlights": [
                "Tested a microservices-based system that analyzes bank account income and expenditure to offer short-term loans.",
                "Built an API automation framework with a BDD approach (Cucumber, RestAssured) for component-level testing.",
                "Ran functional, API and database validation across services, working with product managers and developers.",
            ],
        },
        {
            "role": "Quality Assurance Engineer",
            "company": "Logpoint, Nepal",
            "dates": "May 2023 - May 2024",
            "highlights": [
                "Defined the QA strategy for feature and release sign-offs; wrote and reviewed test plans and test cases.",
                "Automated API and end-to-end tests for internal web applications and SIEM plugin integrations.",
                "Standardized the API and Playwright automation frameworks and streamlined QA procedures.",
                "Mentored junior QA engineers on testing practices and tools.",
            ],
        },
        {
            "role": "Associate Quality Assurance Engineer",
            "company": "Logpoint, Nepal",
            "dates": "Aug 2021 - Apr 2023",
            "highlights": [
                "Wrote test cases and test data from requirement documents; tracked defects with the development team.",
                "Developed and optimized regex-based log parsers for faster, more reliable log interpretation.",
                "Built an internal tool that automated parser regression tests, query validation and bundle verification, cutting manual testing time by 50%.",
                "Created and verified analytics content for SIEM, SOAR and UEBA platforms.",
            ],
        },
        {
            "role": "Technical Writer",
            "company": "Entegra Sources Pvt. Ltd.",
            "dates": "Mar 2020 - Aug 2021",
            "highlights": [
                "Wrote and reviewed customer engineering documentation with a focus on clarity and precision.",
            ],
        },
    ],
    # Optional keys: ignored by the Release 1 template, ready for a later section.
    "education": [
        {
            "degree": "Bachelor's Degree in Electronics and Communication Engineering",
            "school": "Eastern Region Campus, Institute of Engineering, Tribhuvan University",
            "dates": "2015 - 2020",
        },
    ],
    "certifications": [
        {"name": "PCAP: Certified Associate in Python Programming", "issuer": "Python Institute", "date": "Aug 2023"},
        {"name": "Certified Tester Foundation Level (CTFL)", "issuer": "ISTQB", "date": "Sep 2022"},
    ],
}

import os
from datetime import date

from flask import Flask, render_template

ALLOWED_LINK_PREFIXES = ("http://", "https://", "mailto:")
REQUIRED_OWNER_FIELDS = ("name", "title", "bio", "email")


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _is_text_list(value):
    return isinstance(value, list) and all(isinstance(v, str) for v in value)


def _check_link(value, path, errors):
    """A link is optional; when set it must use an allowed scheme."""
    if value in (None, ""):
        return
    if not isinstance(value, str) or not value.startswith(ALLOWED_LINK_PREFIXES):
        errors.append(f"{path} must start with http://, https:// or mailto:")


def validate(data):
    """Return human-readable errors for bad data; an empty list means valid."""
    if not isinstance(data, dict):
        return ["PORTFOLIO_DATA must be a dict"]

    errors = []

    owner = data.get("owner")
    if not isinstance(owner, dict):
        errors.append("owner is required")
    else:
        for field in REQUIRED_OWNER_FIELDS:
            if not _is_text(owner.get(field)):
                errors.append(f"owner.{field} is required and must be non-empty text")

    for i, link in enumerate(data.get("social_links") or []):
        _check_link(link.get("url") if isinstance(link, dict) else None,
                    f"social_links[{i}].url", errors)

    skills = data.get("skills") or {}
    if not isinstance(skills, dict):
        errors.append("skills must be a dict of category to list of strings")
    else:
        for category, items in skills.items():
            if not _is_text_list(items):
                errors.append(f"skills.{category} must be a list of strings")

    for i, project in enumerate(data.get("projects") or []):
        if not isinstance(project, dict):
            errors.append(f"projects[{i}] must be a dict")
            continue
        if not _is_text(project.get("title")):
            errors.append(f"projects[{i}].title is required")
        if "tech_stack" in project and not _is_text_list(project["tech_stack"]):
            errors.append(f"projects[{i}].tech_stack must be a list of strings")
        _check_link(project.get("demo_link"), f"projects[{i}].demo_link", errors)
        _check_link(project.get("code_link"), f"projects[{i}].code_link", errors)

    return errors


def create_app(data=None):
    """Build the Flask app. Bad data stops startup with a message naming the field."""
    data = PORTFOLIO_DATA if data is None else data
    errors = validate(data)
    if errors:
        raise ValueError("Invalid PORTFOLIO_DATA:\n- " + "\n- ".join(errors))

    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html", data=data, year=date.today().year)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
