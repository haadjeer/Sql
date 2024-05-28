from langchain_community.llms import Ollama
from crewai import Agent, Crew, Process, Task
import os

# Set environment variables
os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
os.environ["OPENAI_MODEL_NAME"] = "llama3-70b-8192"
os.environ["OPENAI_API_KEY"] = "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"

# Initialize the model
model = Ollama(model="llama3")

# Define the SQL query
sql_query = "SELECT COUNT(*) FROM artist"

# Define the agent for SQL-to-human translation
SQLTranslatorAgent = Agent(
    role="sql translator",
    goal="To translate SQL queries into human-readable text",
    backstory="You are an AI assistant that translates SQL queries into natural language questions",
    verbose=True,
    allow_delegation=False,
    model=model  # Use the model in the agent
)

# Define the task
TranslationTask = Task(
    description=f"Translate the SQL query '{sql_query}' into a human-readable question",
    agent=SQLTranslatorAgent,
    expected_output="The SQL query is translated into a human-readable question"
)

# Define the crew
crew = Crew(
    agents=[SQLTranslatorAgent],
    tasks=[TranslationTask],
    process=Process.sequential,
    verbose=2
)

# Kickoff the process
output = crew.kickoff()
print(output)
