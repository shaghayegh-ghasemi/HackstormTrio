from langchain.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

summary_template = """
Given the video transcript {information}, provide:
1. A short summary.
"""

summary_prompt_template = PromptTemplate(
    input_variables=["information"], template=summary_template
)

llm = ChatOllama(model="llama3")

def summarize_text(video_transcript):
    """Generate a summary from a video transcript."""
    chain = summary_prompt_template | llm | StrOutputParser()
    result = chain.invoke(input={"information": video_transcript})
    return result
