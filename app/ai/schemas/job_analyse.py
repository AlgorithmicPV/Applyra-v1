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
                    "with enough information to analyse."
                ),
            },
            "invalid_reason": {
                "type": ["string", "null"],
                "description": (
                    "Reason why the content is invalid. Null if is_valid is true."
                ),
            },
            "job_title": {
                "type": ["string", "null"],
            },
            "company_name": {
                "type": ["string", "null"],
            },
            "country": {
                "type": ["string", "null"],
                "description": "Country or job location.",
            },
            "job_description": {
                "type": "array",
                "description": (
                    "Concise bullet-point summary of the job responsibilities, "
                    "requirements, and other important details."
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
                    "Overall match score between the user's skills and the job."
                ),
            },
            "tips": {
                "type": "string",
                "description": (
                    "Practical advice for improving the user's suitability for this job."
                ),
            },
            "matching_skills": {
                "type": "array",
                "description": (
                    "Comparison of each required job skill or qualification "
                    "against the user's provided skills."
                ),
                "items": {
                    "type": "object",
                    "properties": {
                        "required_skill": {
                            "type": "string",
                            "description": (
                                "A required skill, qualification, certification, "
                                "technology, experience requirement, or competency "
                                "from the job advertisement. This may be a single "
                                "word, phrase, or complete sentence."
                            ),
                        },
                        "does_user_have": {
                            "type": "boolean",
                            "description": (
                                "True only if the user's supplied skills clearly "
                                "demonstrate this requirement."
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
