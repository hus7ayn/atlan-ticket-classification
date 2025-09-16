#!/usr/bin/env python3
"""
Streamlit UI for Atlan Ticket Classification System
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Import our modules
from ticket_classifier import TicketClassifier
from smart_ticket_processor import SmartTicketProcessor
from ticket_api import TicketAPI
from utils import load_tickets_data, save_csv_report
from config import DEFAULT_REPORT_FILENAME, DEFAULT_CSV_FILENAME

# Page configuration
st.set_page_config(
    page_title="Atlan Ticket Classification System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .ticket-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .response-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-top: 1rem;
    }
    .source-link {
        color: #1f77b4;
        text-decoration: none;
    }
    .source-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

def load_classification_data():
    """Load and process classification data"""
    try:
        # Load tickets data
        tickets_data = load_tickets_data()
        if not tickets_data:
            return None, "No tickets data found"
        
        # Initialize classifier
        classifier = TicketClassifier()
        classifier.load_tickets(tickets_data)
        
        # Classify all tickets
        with st.spinner("Classifying tickets... This may take a few minutes."):
            results = classifier.classify_all_tickets()
        
        # Generate report
        report = classifier.generate_report()
        
        return {
            'tickets_data': tickets_data,
            'results': results,
            'report': report,
            'classifier': classifier
        }, None
        
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

def display_ticket_details(ticket_data, classification_result):
    """Display detailed ticket information"""
    with st.expander(f"📋 {ticket_data.get('id', 'Unknown')} - {ticket_data.get('subject', 'No Subject')}", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Ticket Content:**")
            st.markdown(f"**Subject:** {ticket_data.get('subject', 'N/A')}")
            st.markdown(f"**Body:**")
            st.text_area("Ticket Body", value=ticket_data.get('body', 'N/A'), height=150, disabled=True, key=f"body_{ticket_data.get('id')}", label_visibility="collapsed")
        
        with col2:
            classification = classification_result.get('classification', {})
            reasoning = classification.get('reasoning', {})
            
            st.markdown("**Classification:**")
            st.markdown(f"**Topic:** `{classification.get('topic_tag', 'N/A')}`")
            st.markdown(f"**Sentiment:** `{classification.get('sentiment', 'N/A')}`")
            st.markdown(f"**Priority:** `{classification.get('priority', 'N/A')}`")
            st.markdown(f"**Status:** `{classification_result.get('status', 'N/A')}`")
            
            st.markdown("**Reasoning:**")
            st.markdown(f"**Topic:** {reasoning.get('topic_reasoning', 'N/A')}")
            st.markdown(f"**Sentiment:** {reasoning.get('sentiment_reasoning', 'N/A')}")
            st.markdown(f"**Priority:** {reasoning.get('priority_reasoning', 'N/A')}")

def display_statistics(report):
    """Display classification statistics"""
    st.markdown("### 📊 Classification Statistics")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Tickets",
            value=report['summary']['total_tickets'],
            delta=None
        )
    
    with col2:
        st.metric(
            label="Successful",
            value=report['summary']['successful_classifications'],
            delta=None
        )
    
    with col3:
        st.metric(
            label="Failed",
            value=report['summary']['failed_classifications'],
            delta=None
        )
    
    with col4:
        st.metric(
            label="Success Rate",
            value=report['summary']['success_rate'],
            delta=None
        )
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Topic distribution
        topic_data = report['distributions']['topics']
        if topic_data:
            fig_topics = px.pie(
                values=list(topic_data.values()),
                names=list(topic_data.keys()),
                title="Topic Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_topics.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_topics, use_container_width=True, key=f"topic_pie_chart_{id(report)}")
    
    with col2:
        # Sentiment distribution
        sentiment_data = report['distributions']['sentiments']
        if sentiment_data:
            fig_sentiment = px.bar(
                x=list(sentiment_data.keys()),
                y=list(sentiment_data.values()),
                title="Sentiment Distribution",
                color=list(sentiment_data.values()),
                color_continuous_scale="Viridis"
            )
            fig_sentiment.update_layout(xaxis_title="Sentiment", yaxis_title="Count")
            st.plotly_chart(fig_sentiment, use_container_width=True, key=f"sentiment_bar_chart_{id(report)}")
    
    # Priority distribution
    priority_data = report['distributions']['priorities']
    if priority_data:
        fig_priority = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="Priority Distribution",
            color=list(priority_data.values()),
            color_continuous_scale="Reds"
        )
        fig_priority.update_layout(xaxis_title="Priority", yaxis_title="Count")
        st.plotly_chart(fig_priority, use_container_width=True, key=f"priority_bar_chart_{id(report)}")

def process_query_with_grok_summary(query):
    """Process query and get Grok-summarized response"""
    try:
        # Initialize API
        api = TicketAPI()
        
        # Process query
        result = api.process_query(query)
        
        if not result['success']:
            return None, result.get('error', 'Unknown error')
        
        # Get the response
        final_response = result['final_response']
        
        # Use Tavily's response directly (no additional summarization)
        if final_response['type'] == 'tavily_answer':
            summary_text = final_response['answer']
        else:
            summary_text = final_response.get('message', final_response.get('answer', 'No response available'))
        
        return {
            'query': query,
            'classification': result['internal_analysis'],
            'summary': summary_text,
            'full_response': final_response,
            'sources': final_response.get('sources', [])
        }, None
        
    except Exception as e:
        return None, f"Error processing query: {str(e)}"

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎫 Atlan Ticket Classification System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["📊 Classification Report", "💬 Interactive Query"])
    
    if page == "📊 Classification Report":
        st.markdown("### Classification Report & Analysis")
        st.markdown("Load and analyze the classification results for all 30 tickets.")
        
        # Load button
        if st.button("🔄 Load Classification Report", type="primary", use_container_width=True):
            with st.spinner("Loading and processing tickets..."):
                data, error = load_classification_data()
                
                if error:
                    st.error(error)
                else:
                    st.success("✅ Classification completed successfully!")
                    
                    # Store in session state
                    st.session_state.classification_data = data
                    
                    # Display tickets
                    st.markdown("### 📋 Detailed Ticket Results")
                    
                    # Filter options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        topic_filter = st.selectbox("Filter by Topic", ["All"] + list(data['report']['distributions']['topics'].keys()))
                    
                    with col2:
                        sentiment_filter = st.selectbox("Filter by Sentiment", ["All"] + list(data['report']['distributions']['sentiments'].keys()))
                    
                    with col3:
                        priority_filter = st.selectbox("Filter by Priority", ["All"] + list(data['report']['distributions']['priorities'].keys()))
                    
                    # Filter tickets
                    filtered_tickets = []
                    for i, ticket in enumerate(data['tickets_data']):
                        result = data['results'][i]
                        classification = result.get('classification', {})
                        
                        topic_match = topic_filter == "All" or classification.get('topic_tag') == topic_filter
                        sentiment_match = sentiment_filter == "All" or classification.get('sentiment') == sentiment_filter
                        priority_match = priority_filter == "All" or classification.get('priority') == priority_filter
                        
                        if topic_match and sentiment_match and priority_match:
                            filtered_tickets.append((ticket, result))
                    
                    st.markdown(f"**Showing {len(filtered_tickets)} of {len(data['tickets_data'])} tickets**")
                    
                    # Display filtered tickets
                    for ticket, result in filtered_tickets:
                        display_ticket_details(ticket, result)
        
        # Display stored data if available
        if 'classification_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 Statistics (from previous load)")
            display_statistics(st.session_state.classification_data['report'])
    
    elif page == "💬 Interactive Query":
        st.markdown("### Interactive Query Processing")
        st.markdown("Ask questions and get intelligent responses using Tavily search and Grok summarization.")
        
        # Query input
        query = st.text_area(
            "Enter your question:",
            placeholder="e.g., How to connect Snowflake to Atlan? What are the API authentication methods?",
            height=100
        )
        
        if st.button("🔍 Process Query", type="primary", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a question.")
            else:
                with st.spinner("Processing your query..."):
                    result, error = process_query_with_grok_summary(query)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.success("✅ Query processed successfully!")
                        
                        # Display classification
                        st.markdown("### 🏷️ Classification")
                        classification = result['classification']
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Topic:** `{classification['topic']}`")
                        with col2:
                            st.markdown(f"**Sentiment:** `{classification['sentiment']}`")
                        with col3:
                            st.markdown(f"**Priority:** `{classification['priority']}`")
                        
                        # Display summarized response
                        st.markdown("### 💡 Summarized Response")
                        st.markdown(f'<div class="response-card">{result["summary"]}</div>', unsafe_allow_html=True)
                        
                        # Display sources if available
                        if result['sources']:
                            st.markdown("### 🔗 Sources")
                            for i, source in enumerate(result['sources'], 1):
                                st.markdown(f"{i}. [{source}]({source})")
                        
                        # Display full response in expander
                        with st.expander("📄 Full Response Details"):
                            st.json(result['full_response'])
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit, Grok LLM, and Tavily API")

if __name__ == "__main__":
    main()
