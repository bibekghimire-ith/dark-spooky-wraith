# Portfolio profile data

Built from `docs/CV_LP.pdf`. Paste the block below over `PORTFOLIO_DATA` at the top of `app.py` (or into `content.yaml` in Release 2). It follows the schema in `Portfolio-PRD.md`, plus two optional keys, `education` and `certifications`, that the template can render later.

## PORTFOLIO_DATA

```python
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
```

## Notes on how this was written

- **Title:** your CV summary says "Software QA Engineer", but your current role is Software Engineer, so the site leads with that and tells the QA story in the bio.
- **Not taken from the CV:** the third bullet under your current role (data ingestion components) and the Traffic Sign Recognition project come from what you have told me about your work, so confirm both.
- **Project links:** the first three projects come from CV achievements and are internal, so their links are empty and the template hides empty buttons. Add a screenshot per project in `static/img/` or use a hosted image URL.
- **Left out on purpose:** phone number and home address. Your email and the three profile links need to be copied in from your CV, because they are placeholders here.
- **Summary bullets:** the CV's "Hard skills" and "Soft skills" lists are folded into the bio and the skills categories rather than shown as their own section.
