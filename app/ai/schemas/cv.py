JSON_SCHEMA = {
    "name": "professional_cv",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "description": "The target role or job title identified from the job advertisement.",
            },
            "country": {
                "type": "string",
                "description": "The country relevant to the job advertisement and CV.",
            },
            "html_code": {
                "type": "string",
                "description": "A complete, valid, professional, ATS-friendly HTML CV with print-friendly CSS, ready to be converted to PDF.",
            },
        },
        "required": ["role", "country", "html_code"],
        "additionalProperties": False,
    },
}
