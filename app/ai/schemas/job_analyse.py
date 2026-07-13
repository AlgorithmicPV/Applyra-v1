JSON_SCHEMA = {
    "name": "job_analysis",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "is_valid": {
                "type": "boolean",
                "description": (
                    "True only if the supplied content is a valid job advertisement "
                    "for a single vacancy and contains enough information to analyse."
                ),
            },
            "invalid_reason": {
                "type": ["string", "null"],
                "description": (
                    "The reason the supplied content is not a valid job advertisement. "
                    "Must be null when is_valid is true."
                ),
            },
            "source_platform": {
                "type": ["string", "null"],
                "description": (
                    "The job platform or website identified from the source URL, "
                    "such as LinkedIn, SEEK, Indeed, Glassdoor, Trade Me Jobs, "
                    "Jora, Workday, Greenhouse, Lever, SmartRecruiters, Jobvite, "
                    "SuccessFactors, or Company careers website. "
                    "Must be null when the platform cannot be reliably identified."
                ),
            },
            "job_title": {
                "type": ["string", "null"],
                "description": (
                    "The job title extracted from the advertisement. "
                    "Must be null when is_valid is false."
                ),
            },
            "company_name": {
                "type": ["string", "null"],
                "description": (
                    "The employer or company name extracted from the advertisement. "
                    "Must be null when is_valid is false."
                ),
            },
            "country": {
                "type": ["string", "null"],
                "description": (
                    "The country or job location extracted from the advertisement. "
                    "Must be null when is_valid is false."
                ),
            },
            "job_description": {
                "type": "array",
                "description": (
                    "A concise list summarising the role's responsibilities, "
                    "requirements, qualifications, and other important details. "
                    "Each item may be a sentence or short paragraph. "
                    "Must be an empty array when is_valid is false."
                ),
                "items": {
                    "type": "string",
                },
            },
            "relevancy": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": (
                    "The overall match score between the job requirements and the "
                    "user's supplied skills, work experience, and education. "
                    "Must be 0 when is_valid is false."
                ),
            },
            "tips": {
                "type": "string",
                "description": (
                    "Practical and truthful advice for improving the user's suitability "
                    "for the job, focusing on important missing skills, qualifications, "
                    "certifications, or experience. Must be an empty string when "
                    "is_valid is false."
                ),
            },
            "matching_skills": {
                "type": "array",
                "description": (
                    "A comparison of each required job skill, qualification, "
                    "certification, technology, experience requirement, competency, "
                    "or soft skill against the user's supplied skills, work experience, "
                    "and education. Must be an empty array when is_valid is false."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "required_skill": {
                            "type": "string",
                            "description": (
                                "A required skill, qualification, certification, "
                                "technology, experience requirement, competency, "
                                "or soft skill from the job advertisement. "
                                "This may be a single word, phrase, or complete sentence."
                            ),
                        },
                        "does_user_have": {
                            "type": "boolean",
                            "description": (
                                "True only when the user's supplied skills, work "
                                "experience, or education clearly demonstrate this "
                                "requirement. Do not infer unsupported abilities."
                            ),
                        },
                    },
                    "required": [
                        "required_skill",
                        "does_user_have",
                    ],
                    "additionalProperties": False,
                },
            },
        },
        "required": [
            "is_valid",
            "invalid_reason",
            "source_platform",
            "job_title",
            "company_name",
            "country",
            "job_description",
            "relevancy",
            "tips",
            "matching_skills",
        ],
        "additionalProperties": False,
    },
}

