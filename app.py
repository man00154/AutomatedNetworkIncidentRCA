import os
import json
import streamlit as st
import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request

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

# ------------------------------
# Lightweight in-memory RAG store
# ------------------------------
class DummyRAG:
    def __init__(self, docs=None):
        self.docs = docs or ["Network incidents data placeholder"]

    def query(self, q):
        return self.docs[0]

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Network Root Cause Analyst", layout="wide")
st.title("MANISH - Autonomous Network Root Cause Analyst")

incident_summary = st.text_area("Enter Network Incident Summary:", height=150)

# Initialize lightweight RAG
vectorstore = DummyRAG()

# Simple predictive analysis
def predictive_analysis(incident):
    return "High probability of router misconfiguration causing packet loss."

# Graph
graph = SimpleGraph()
graph.add_node("Incident", description=incident_summary)

# Prompt builder
def build_prompt(incident_summary, prediction, context):
    return f"""
You are a network root cause analyst. Analyze the following network incident:

Incident: {incident_summary}
Context: {context}
Predicted cause: {prediction}

Provide:
1. Root Cause
2. Explanation in simple terms
3. Suggested remediation steps
"""

# ------------------------------
# Function to get OAuth token from service account JSON explicitly
# ------------------------------
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service_account.json")

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

# ------------------------------
# Function to call Gemini API
# ------------------------------
def call_gemini(prompt):
    access_token = get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    payload = {
        "prompt": prompt,
        "temperature": 0.2,
        "maxOutputTokens": 500
    }
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        result = response.json()
        return result["candidates"][0]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# ------------------------------
# Analyze button
# ------------------------------
if st.button("Analyze Incident"):
    if not incident_summary:
        st.warning("Please enter an incident summary.")
    else:
        prediction = predictive_analysis(incident_summary)
        graph.add_node("Prediction", description=prediction)
        context = vectorstore.query(incident_summary)
        prompt = build_prompt(incident_summary, prediction, context)
        result = call_gemini(prompt)
        st.subheader("Analysis Result")
        st.write(result)
        st.subheader("Graph Overview")
        st.json(graph.serialize())
