# app.py
import os
import streamlit as st
import json
import requests
from typing import List, Dict
import time

# Placeholder for your actual API key.
# It's a best practice to use Streamlit secrets for this in a real-world app.
# Create a file named .streamlit/secrets.toml and add `GOOGLE_API_KEY="your_api_key"`
# Then access it with st.secrets["GOOGLE_API_KEY"]
if "GOOGLE_API_KEY" in st.secrets:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Define the API URL and model name as constants
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GOOGLE_API_KEY}"

# --- Simulated Data and Knowledge Base (Very Light RAG) ---
# In a real application, this would be a vector database or a proper data ingestion pipeline.
# Here, we'll use a simple dictionary to represent our 'knowledge'.
KNOWLEDGE_BASE = {
    "high latency": {
        "title": "High Network Latency Troubleshooting Guide",
        "content": "High latency can be caused by network congestion, firewall misconfigurations, or a slow server response. Correlate with network traffic logs (e.g., via `ping` or `traceroute`) and server performance metrics. The root cause is often identified by analyzing packet loss and jitter.",
        "actionable_intelligence": "Action: Investigate firewall rules for any recent changes and check server CPU/memory usage during peak latency."
    },
    "packet loss": {
        "title": "Network Packet Loss Analysis",
        "content": "Packet loss indicates dropped packets during transmission. Common causes include faulty cabling, overloaded network devices (routers, switches), or insufficient bandwidth. Check device health, CPU/memory usage, and review interface counters for discard rates.",
        "actionable_intelligence": "Action: Ping network hops to isolate the area of packet loss and check device health metrics for signs of an overload."
    },
    "service unreachable": {
        "title": "Service Unreachable Troubleshooting",
        "content": "A 'service unreachable' error suggests a problem with DNS resolution, an incorrect IP address, or a service not running on the destination server. Start by verifying DNS and checking the service status (`systemctl status [service]`) on the target machine.",
        "actionable_intelligence": "Action: Perform a DNS lookup and verify the service is running. If both are correct, check routing tables for misconfigurations."
    }
}

# --- Predictive Analysis (Simulated) ---
def predict_incident_type(incident_description: str) -> str:
    """A very simple predictive function based on keywords."""
    incident_description = incident_description.lower()
    if "latency" in incident_description or "slow" in incident_description:
        return "high latency"
    elif "packet" in incident_description or "drop" in incident_description:
        return "packet loss"
    elif "unreachable" in incident_description or "down" in incident_description:
        return "service unreachable"
    else:
        return "unknown"

# --- Agentic Workflow (Simplified LangGraph) ---
# This simulates a LangGraph state machine with a simple, linear flow.
def agent_root_cause_analysis(incident: str) -> str:
    """
    Simulates a simple agentic workflow using a chain of thought.
    Each 'step' is a function call.
    """
    if not GOOGLE_API_KEY:
        st.error("API key is not set. Please add it to your environment variables or Streamlit secrets.")
        return "Unable to perform analysis. API key is missing."

    st.write("### 🤖 Agentic Analysis Started")

    # Step 1: Predictive Analysis (Simulated)
    with st.spinner("Step 1/3: Performing predictive analysis..."):
        incident_type = predict_incident_type(incident)
        time.sleep(1) # Simulate work
        st.info(f"💡 Prediction: This incident is likely related to **{incident_type.replace('_', ' ')}**.")

    # Step 2: Retrieval (Simple RAG)
    with st.spinner("Step 2/3: Retrieving relevant knowledge..."):
        # Retrieve context from our knowledge base based on the predicted type.
        context = KNOWLEDGE_BASE.get(incident_type, {
            "title": "General Network Troubleshooting",
            "content": "No specific match found in the knowledge base. The analysis will proceed with general best practices.",
            "actionable_intelligence": "Action: Start with basic checks like connectivity (`ping`), device status, and recent configuration changes."
        })
        time.sleep(1) # Simulate work
        st.success("✅ Relevant knowledge found.")

    # Step 3: LLM Generation (The core of the analysis)
    with st.spinner("Step 3/3: Generating human-readable explanation..."):
        # Construct the prompt for the Gemini API.
        prompt = f"""
        Act as a senior network engineer and root cause analyst. Your task is to analyze a network incident and provide a clear, human-readable explanation of the root cause, including the 'why' behind the problem.

        Based on the following incident description and retrieved network knowledge, generate a concise report.

        **Incident Description:**
        {incident}

        **Retrieved Knowledge:**
        Title: {context['title']}
        Content: {context['content']}
        Actionable Intelligence: {context['actionable_intelligence']}

        Your response must include the following sections:
        1.  **Identified Problem:** A single sentence summarizing the core issue.
        2.  **Root Cause Analysis:** A brief paragraph explaining the 'why' behind the problem. Use the provided knowledge and connect it to the incident description.
        3.  **Actionable Intelligence:** Extract and rephrase the "actionable intelligence" to provide a clear, next-step recommendation.
        """

        # API Call
        try:
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ]
            }
            # Use the defined API_URL which now includes the GOOGLE_API_KEY
            response = requests.post(API_URL, headers=headers, data=json.dumps(data))
            response.raise_for_status() # Raise an exception for bad status codes
            result = response.json()
            generated_text = result['candidates'][0]['content']['parts'][0]['text']
            time.sleep(2) # Simulate work
            st.success("✅ Analysis complete!")
            return generated_text

        except Exception as e:
            st.error(f"Error during LLM generation: {e}")
            return "Unable to perform analysis. Please check your API key and network connection."

# --- Streamlit UI ---
st.set_page_config(page_title="GenAI Root Cause Analyst", layout="wide")
st.title("Network Root Cause Analyst")
st.markdown("---")

st.markdown("""
Welcome to the **GenAI Root Cause Analyst**.
This tool, powered by Google's `gemini-2.0-flash-lite`, acts as a virtual network expert.
It uses a combination of predictive analysis, simple RAG, and an agentic workflow to diagnose network incidents and provide actionable intelligence.

**Instructions:**
Enter a brief description of a network incident and click 'Analyze' to receive a detailed root cause analysis.
""")

# Incident Input
incident_description = st.text_area(
    "Describe the network incident:",
    height=150,
    placeholder="e.g., 'The web server is responding very slowly. Users are reporting long load times and some connection timeouts.'"
)

# Analyze Button
if st.button("🚀 Analyze Incident", use_container_width=True, type="primary"):
    if not incident_description.strip():
        st.warning("Please enter a description of the incident to analyze.")
    elif not GOOGLE_API_KEY:
        st.error("Please set your GOOGLE_API_KEY as a Streamlit secret or environment variable.")
    else:
        st.markdown("### Analysis Report")
        with st.container():
            # Start the agentic workflow
            report = agent_root_cause_analysis(incident_description)
            st.markdown(report)

st.markdown("---")
st.caption("Conceptual Demo powered by Streamlit and the Gemini API.")
