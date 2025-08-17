import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool

# ------------------------------
# Lightweight replacement for LangGraph
# ------------------------------
class SimpleGraph:
    def __init__(self):
        self.nodes = []

    def add_node(self, name, description=""):
        self.nodes.append({"name": name, "description": description})

    def serialize(self):
        return self.nodes

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

st.set_page_config(page_title="Network Root Cause Analyst", layout="wide")
st.title("MANISH - Autonomous Network Root Cause Analyst")

# Sample input
incident_summary = st.text_area("Enter Network Incident Summary:", height=150)

# Load or create a lightweight FAISS index for RAG
vectorstore = None
embeddings = OpenAIEmbeddings(openai_api_key=API_KEY)  # lightweight embeddings
if os.path.exists("faiss_index"):
    vectorstore = FAISS.load_local("faiss_index", embeddings)
else:
    vectorstore = FAISS.from_texts(["Network incidents data placeholder"], embeddings=embeddings)

# Define a very simple predictive analysis placeholder
def predictive_analysis(incident):
    # Placeholder: In real use, feed ML model here
    return "High probability of router misconfiguration causing packet loss."

# Simple graph usage
graph = SimpleGraph()
graph.add_node("Incident", description=incident_summary)

# Define prompt template
prompt = PromptTemplate(
    input_variables=["incident_summary", "prediction"],
    template="""
You are a network root cause analyst. Analyze the following network incident:
Incident: {incident_summary}
Predicted cause: {prediction}

Provide:
1. Root Cause
2. Explanation in simple terms
3. Suggested remediation steps
"""
)

# Agentic AI tools
tools = [
    Tool(
        name="PredictiveAnalysis",
        func=predictive_analysis,
        description="Predict probable root cause for a network incident."
    )
]

llm = ChatOpenAI(model_name=MODEL_NAME, temperature=0.2, openai_api_key=API_KEY)

agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

if st.button("Analyze Incident"):
    if not incident_summary:
        st.warning("Please enter an incident summary.")
    else:
        prediction = predictive_analysis(incident_summary)
        graph.add_node("Prediction", description=prediction)
        result = agent.run(f"incident_summary: {incident_summary}\nprediction: {prediction}")
        st.subheader("Analysis Result")
        st.write(result)
        st.subheader("Graph Overview")
        st.json(graph.serialize())
