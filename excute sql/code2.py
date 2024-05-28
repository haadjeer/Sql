from langchain_community.utilities import SQLDatabase
import os
from langchain_experimental.sql import SQLDatabaseChain, SQLDatabaseSequentialChain
from langchain.chains.llm import LLMChain
from langchain.chains.sql_database.prompt import DECIDER_PROMPT, PROMPT, SQL_PROMPTS
from dotenv import load_dotenv

load_dotenv(".env")

# Set OpenAI API environment variables (if needed)
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama3-8b-8192"
os.environ["OPENAI_API_KEY"] = os.getenv("GROQ_API_KEY")

username = "postgres"
password = "1234"  # plain (unescaped) text
host = "localhost"  # Hostname or IP address of the PostgreSQL server
port = "5432"  # Port number
mydatabase = "postgres"

pg_uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{mydatabase}"
db = SQLDatabase.from_uri(pg_uri)

OPENAI_API_KEY = os.getenv("GROQ_API_KEY")
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name="llama3-8b-8192"
)

sql_chain = SQLDatabaseChain.from_llm(llm, db)

PROMPT = """ 
Given an input question, first create a syntactically correct postgresql query to run,  
then look at the results of the query and return the answer.  
The question: {question}
"""

decider_chain = LLMChain(llm=llm, prompt=DECIDER_PROMPT, output_key="table_names")

class CustomSQLDatabaseSequentialChain(SQLDatabaseSequentialChain):
    def run(self, question):
        result = super().run(question)
        print(f"Query result: {result}")
        return result

db_chain = CustomSQLDatabaseSequentialChain(llm=llm, database=db, verbose=True, top_k=3,
                                            decider_chain=decider_chain, sql_chain=sql_chain, prompt=PROMPT)

question = "Retrieve billing information for invoices from Paris or Berlin"

db_chain.run(question)


with open("human.txt", "r") as file:
    questions = file.readlines()

# Iterate over each question
for question in questions:
    # Run the chain
    result = db_chain.run(question.strip())  # Strip newline characters

    # Check if the result contains an error message
    if "Error" in result:
        print(result)
    else:
        # Split the result by newline characters
        result_lines = result.split('\n')

        # Search for the line containing the SQL query
        generated_query = None
        for line in result_lines:
            if line.startswith("SQLQuery:"):
                generated_query = line[len("SQLQuery:"):].strip()
                break

        # Print the question and the generated SQL query
        print("\nQuestion:", question.strip())
        if generated_query:
            print("Generated SQL Query:")
            print(generated_query)
        else:
            print("Error: SQL Query not found in result")
"""

# Open a file in append mode to store the results
with open("query_results.txt", "a") as file:
    # Iterate over each question
    for question in questions:
        try:
            # Run the chain
            result = db_chain.run(question.strip())  # Strip newline characters
            
            # Split the result by newline characters
            result_lines = result.split('\n')
    
            # Search for the line containing the SQL query
            generated_query = None
            for line in result_lines:
                if line.startswith("SQLQuery:"):
                    generated_query = line[len("SQLQuery:"):].strip()
                    break
            
            # Write the question and the generated SQL query to the file
            file.write(f"Question: {question.strip()}\n")
            if generated_query:
                file.write(f"Generated SQL Query: {generated_query}\n")
            else:
                file.write("Error: SQL Query not found in result\n")
            file.write("\n")
        except Exception as e:
            # If there's an error, write the error message to the file
            file.write(f"Question: {question.strip()}\n")
            file.write(f"Error: {e}\n")
            file.write("\n")

"""