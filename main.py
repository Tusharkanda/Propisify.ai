import os
from openai import AzureOpenAI

# Hardcoded Azure OpenAI settings
endpoint = "https://openaiqc.gep.com/techathon/openai/deployments/gpt-4o-mini/chat/completions?api-version=2025-01-01-preview"
deployment_name = "gpt-4o-mini"
api_key = "Gi9FJDBZ9KCoW5gqtTRThmVasGFfPMNwuFYYoDU6B5zz2kmZiplPJQQJ99AJACYeBjFXJ3w3AAABACOGLq67"
api_version = "2025-01-01-preview"

client = AzureOpenAI(
    api_key=api_key,
    azure_endpoint=endpoint,
    api_version=api_version
)

response = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {"role": "system", "content": "You are an assistant."},
        {"role": "user",   "content": "Hello! Can you say hi back?"}
    ],
    temperature=0.7
)

assistant_msg = response.choices[0].message.content
print("Assistant:", assistant_msg)