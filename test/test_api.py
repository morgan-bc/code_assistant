from openai import AzureOpenAI

base_url = "https://oh-ai-openai-scu.openai.azure.com"
api_key = "76c10d695bf349ab8026e7c940e6bd26"
model = "gpt-35-turbo"

client = AzureOpenAI(azure_endpoint=base_url, api_key=api_key, api_version="2023-05-15")
response = client.chat.completions.create(
    model="gpt-35-turbo", # model = "deployment_name".
    messages=[
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": "Who were the founders of Microsoft?"}
    ]
)

print(response.model_dump_json(indent=2))
print(response.choices[0].message.content)