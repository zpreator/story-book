from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

# # Define the system message
# system_msg = 'You are a helpful assistant who understands data science.'

# # Define the user message
# user_msg = 'Create a small dataset about total sales over the last year. The format of the dataset should be a data frame with 12 rows and 2 columns. The columns should be called "month" and "total_sales_usd". The "month" column should contain the shortened forms of month names from "Jan" to "Dec". The "total_sales_usd" column should contain random numeric values taken from a normal distribution with mean 100000 and standard deviation 5000. Provide Python code to generate the dataset, then provide the output in the format of a markdown table.'

# # Create a dataset using GPT
# response = client.chat.completions.create(model="gpt-3.5-turbo",
#                                             messages=[{"role": "system", "content": system_msg},
#                                          {"role": "user", "content": user_msg}])

# print(response)

response = client.images.generate(
   model="dall-e-3",
   prompt="A lush, vibrant forest filled with colorful flowers, sparkling streams, and magical creatures. The sun filters through the canopy of trees, creating a dreamlike atmosphere.",
   size="1024x1024",
   quality="standard",
   n=1,
)
image_url = response.data[0].url
print(image_url)