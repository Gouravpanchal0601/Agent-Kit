from google import genai
from google.genai import types
import time

client = genai.Client(api_key="AIzaSyDHZkfK-6WYAw3qDGR7muKBDGLXFIvNRHM")

file_search_store = client.file_search_stores.create(config={'display_name': 'your-fileSearchStore-name'})

operation = client.file_search_stores.upload_to_file_search_store(
  file=['/home/vinayak/Downloads/RFP_generator/sam.pdf','/home/vinayak/Downloads/RFP_generator/syllabus_tgt.pdf','/home/vinayak/Downloads/RFP_generator/Resume_Gourav_panchal.pdf'],
  file_search_store_name=file_search_store.name,
  config={
      'display_name' : 'display-file-name',
  }
)

while not operation.done:
    time.sleep(5)
    operation = client.operations.get(operation)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="""what is difference between dave guerra and gourav panchal""",
    config=types.GenerateContentConfig(
        tools=[
            types.Tool(
                file_search = types.FileSearch(
                    file_search_store_names = [file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)