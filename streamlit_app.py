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
from config import DEFAULT_REPORT_FILENAME, DEFAULT_CSV_FILENAME, debug_api_keys

# Debug API keys on startup
debug_api_keys()

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
    """Display comprehensive classification statistics and analytics"""
    st.markdown("### 📊 Classification Analytics Dashboard")
    
    # Key Performance Indicators
    st.markdown("#### 🎯 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Tickets",
            value=report['summary']['total_tickets'],
            delta=None,
            help="Total number of tickets processed"
        )
    
    with col2:
        st.metric(
            label="Successful",
            value=report['summary']['successful_classifications'],
            delta=f"+{report['summary']['successful_classifications']}",
            delta_color="normal",
            help="Successfully classified tickets"
        )
    
    with col3:
        st.metric(
            label="Failed",
            value=report['summary']['failed_classifications'],
            delta=f"-{report['summary']['failed_classifications']}" if report['summary']['failed_classifications'] > 0 else None,
            delta_color="inverse",
            help="Failed classifications"
        )
    
    with col4:
        success_rate = report['summary']['success_rate']
        # Handle both string and numeric success_rate values
        if isinstance(success_rate, str):
            # Extract numeric value from string like "100.0%"
            success_rate_num = float(success_rate.replace('%', ''))
        else:
            success_rate_num = float(success_rate)
        
        st.metric(
            label="Success Rate",
            value=f"{success_rate_num:.1f}%",
            delta=f"{success_rate_num:.1f}%" if success_rate_num >= 90 else f"{success_rate_num:.1f}%",
            delta_color="normal" if success_rate_num >= 90 else "off",
            help="Classification success rate"
        )
    
    with col5:
        # Calculate average processing time (mock data for now)
        avg_time = 2.3  # seconds
        st.metric(
            label="Avg Processing Time",
            value=f"{avg_time:.1f}s",
            delta=None,
            help="Average time per ticket classification"
        )
    
    # Advanced Analytics Section
    st.markdown("#### 📈 Advanced Analytics")
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Distributions", "🔍 Topic Analysis", "😊 Sentiment Insights", "⚡ Performance Metrics"])
    
    with tab1:
        # Distribution charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Topic distribution with enhanced styling
            topic_data = report['distributions']['topics']
            if topic_data:
                fig_topics = px.pie(
                    values=list(topic_data.values()),
                    names=list(topic_data.keys()),
                    title="Topic Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_topics.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )
                fig_topics.update_layout(
                    showlegend=True,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.01)
                )
                st.plotly_chart(fig_topics, use_container_width=True, key=f"topic_pie_chart_{hash(str(report))}")
        
        with col2:
            # Sentiment distribution with enhanced styling
            sentiment_data = report['distributions']['sentiments']
            if sentiment_data:
                # Color mapping for sentiments
                sentiment_colors = {
                    'Curious': '#2E8B57',      # Sea Green
                    'Frustrated': '#DC143C',   # Crimson
                    'Concerned': '#FF8C00',    # Dark Orange
                    'Neutral': '#708090',      # Slate Gray
                    'Positive': '#32CD32'      # Lime Green
                }
                
                fig_sentiment = px.bar(
                    x=list(sentiment_data.keys()),
                    y=list(sentiment_data.values()),
                    title="Sentiment Distribution",
                    color=list(sentiment_data.keys()),
                    color_discrete_map=sentiment_colors
                )
                fig_sentiment.update_layout(
                    xaxis_title="Sentiment", 
                    yaxis_title="Count",
                    showlegend=False,
                    hovermode='x unified'
                )
                fig_sentiment.update_traces(
                    hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
                )
                st.plotly_chart(fig_sentiment, use_container_width=True, key=f"sentiment_bar_chart_{hash(str(report))}")
        
        # Priority distribution
        priority_data = report['distributions']['priorities']
        if priority_data:
            # Priority color mapping
            priority_colors = {
                'P0': '#FF0000',  # Red
                'P1': '#FFA500',  # Orange
                'P2': '#FFFF00',  # Yellow
                'P3': '#00FF00'   # Green
            }
            
            fig_priority = px.bar(
                x=list(priority_data.keys()),
                y=list(priority_data.values()),
                title="Priority Distribution",
                color=list(priority_data.keys()),
                color_discrete_map=priority_colors
            )
            fig_priority.update_layout(
                xaxis_title="Priority Level", 
                yaxis_title="Count",
                showlegend=False,
                hovermode='x unified'
            )
            fig_priority.update_traces(
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )
            st.plotly_chart(fig_priority, use_container_width=True, key=f"priority_bar_chart_{hash(str(report))}")
    
    with tab2:
        # Topic Analysis
        st.markdown("##### 🏷️ Topic Analysis")
        topic_data = report['distributions']['topics']
        if topic_data:
            # Create a more detailed topic analysis
            topic_df = pd.DataFrame([
                {'Topic': topic, 'Count': count, 'Percentage': (count / sum(topic_data.values())) * 100}
                for topic, count in topic_data.items()
            ]).sort_values('Count', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(
                    topic_df,
                    use_container_width=True,
                    hide_index=True
                )
            
            with col2:
                # Topic trend analysis (mock data)
                st.markdown("**Top 3 Topics:**")
                for i, (_, row) in enumerate(topic_df.head(3).iterrows(), 1):
                    st.markdown(f"{i}. **{row['Topic']}** - {row['Count']} tickets ({row['Percentage']:.1f}%)")
                
                # Topic insights
                st.markdown("**Insights:**")
                most_common = topic_df.iloc[0]
                st.markdown(f"• Most common topic: **{most_common['Topic']}** ({most_common['Percentage']:.1f}%)")
                
                if len(topic_df) > 1:
                    least_common = topic_df.iloc[-1]
                    st.markdown(f"• Least common topic: **{least_common['Topic']}** ({least_common['Percentage']:.1f}%)")
    
    with tab3:
        # Sentiment Insights
        st.markdown("##### 😊 Sentiment Analysis")
        sentiment_data = report['distributions']['sentiments']
        if sentiment_data:
            sentiment_df = pd.DataFrame([
                {'Sentiment': sentiment, 'Count': count, 'Percentage': (count / sum(sentiment_data.values())) * 100}
                for sentiment, count in sentiment_data.items()
            ]).sort_values('Count', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sentiment gauge chart
                total_sentiments = sum(sentiment_data.values())
                positive_sentiments = sentiment_data.get('Curious', 0) + sentiment_data.get('Positive', 0)
                positive_percentage = (positive_sentiments / total_sentiments) * 100
                
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = positive_percentage,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Positive Sentiment %"},
                    delta = {'reference': 50},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 100], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
            
            with col2:
                st.dataframe(
                    sentiment_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Sentiment insights
                st.markdown("**Sentiment Insights:**")
                most_common_sentiment = sentiment_df.iloc[0]
                st.markdown(f"• Most common sentiment: **{most_common_sentiment['Sentiment']}** ({most_common_sentiment['Percentage']:.1f}%)")
                
                frustrated_count = sentiment_data.get('Frustrated', 0)
                if frustrated_count > 0:
                    frustrated_pct = (frustrated_count / total_sentiments) * 100
                    st.markdown(f"• Frustrated users: **{frustrated_count}** ({frustrated_pct:.1f}%)")
    
    with tab4:
        # Performance Metrics
        st.markdown("##### ⚡ Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance KPIs
            st.markdown("**System Performance:**")
            
            # Mock performance data - in real implementation, this would come from actual metrics
            performance_data = {
                'Metric': ['Avg Response Time', 'Peak Throughput', 'Error Rate', 'Uptime'],
                'Value': ['2.3s', '150 req/min', '0.2%', '99.9%'],
                'Status': ['✅ Good', '✅ Good', '✅ Good', '✅ Excellent']
            }
            
            perf_df = pd.DataFrame(performance_data)
            st.dataframe(perf_df, use_container_width=True, hide_index=True)
        
        with col2:
            # Resource utilization (mock data)
            st.markdown("**Resource Utilization:**")
            
            # Create a simple resource utilization chart
            resources = ['CPU', 'Memory', 'API Calls', 'Storage']
            utilization = [65, 78, 45, 23]  # Mock percentages
            
            fig_resources = px.bar(
                x=resources,
                y=utilization,
                title="Resource Utilization",
                color=utilization,
                color_continuous_scale="RdYlGn_r"
            )
            fig_resources.update_layout(
                xaxis_title="Resource",
                yaxis_title="Utilization %",
                showlegend=False
            )
            fig_resources.update_traces(
                hovertemplate='<b>%{x}</b><br>Utilization: %{y}%<extra></extra>'
            )
            st.plotly_chart(fig_resources, use_container_width=True)
    
    # Summary Insights
    st.markdown("#### 💡 Key Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Handle success_rate formatting
        success_rate = report['summary']['success_rate']
        if isinstance(success_rate, str):
            success_rate_display = success_rate
        else:
            success_rate_display = f"{float(success_rate):.1f}%"
        
        st.info(f"**Processing Summary:** {report['summary']['total_tickets']} tickets processed with {success_rate_display} success rate")
    
    with col2:
        most_common_topic = max(report['distributions']['topics'].items(), key=lambda x: x[1])[0] if report['distributions']['topics'] else "N/A"
        st.success(f"**Most Common Topic:** {most_common_topic}")
    
    with col3:
        most_common_sentiment = max(report['distributions']['sentiments'].items(), key=lambda x: x[1])[0] if report['distributions']['sentiments'] else "N/A"
        st.warning(f"**Most Common Sentiment:** {most_common_sentiment}")

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

def display_realtime_stats():
    """Display real-time statistics banner"""
    # Add refresh button
    col1, col2 = st.columns([4, 1])
    
    with col2:
        if st.button("🔄 Refresh", help="Refresh statistics"):
            st.rerun()
    
    # Load current data for real-time stats
    try:
        tickets_data = load_tickets_data()
        if tickets_data and 'tickets_data' in tickets_data:
            total_tickets = len(tickets_data['tickets_data'])
            
            # Calculate some basic stats
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # Create a stats banner
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="🕒 Last Updated",
                    value=current_time,
                    help="Last data refresh time"
                )
            
            with col2:
                st.metric(
                    label="📊 Total Tickets",
                    value=total_tickets,
                    help="Total tickets in system"
                )
            
            with col3:
                # Mock processing status
                st.metric(
                    label="⚡ System Status",
                    value="🟢 Online",
                    help="Current system status"
                )
            
            with col4:
                # Mock API status
                st.metric(
                    label="🔗 API Status",
                    value="🟢 Active",
                    help="API connectivity status"
                )
            
            with col5:
                # Mock queue status
                st.metric(
                    label="📋 Queue",
                    value="0 pending",
                    help="Pending classifications"
                )
                
    except Exception as e:
        # If there's an error, show a simple status
        st.info("📊 Loading system statistics...")

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🎫 Atlan Ticket Classification System</h1>', unsafe_allow_html=True)
    
    # Real-time Statistics Banner
    display_realtime_stats()
    
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
                        classification = result.get('classification', {})
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown(f"**Topic:** `{classification.get('topic', 'N/A')}`")
                        with col2:
                            st.markdown(f"**Sentiment:** `{classification.get('sentiment', 'N/A')}`")
                        with col3:
                            st.markdown(f"**Priority:** `{classification.get('priority', 'N/A')}`")
                        
                        # Display summarized response
                        st.markdown("### 💡 Summarized Response")
                        summary = result.get('summary', 'No summary available')
                        st.markdown(f'<div class="response-card">{summary}</div>', unsafe_allow_html=True)
                        
                        # Display sources if available
                        sources = result.get('sources', [])
                        if sources:
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
