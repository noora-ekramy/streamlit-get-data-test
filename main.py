import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Import our custom modules
from data_utils import DataLoader
from chatgpt_integration import FinancialChatBot

# Page configuration
st.set_page_config(
    page_title="Youtiva Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .data-section {
        margin-bottom: 3rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_data():
    """Load all financial data with caching"""
    loader = DataLoader()
    data = {
        'chart_of_accounts': loader.load_chart_of_accounts(),
        'vendors': loader.load_vendors(),
        'expenses': loader.load_expenses(),
        'bills': loader.load_bills(),
        'customers': loader.load_customers(),
        'invoices': loader.load_invoices(),
        'services': loader.load_services()
    }
    # Add markdown reports
    reports = loader.load_all_reports()
    data.update(reports)
    return data

def main():
    # Header
    st.markdown('<h1 class="main-header">💰 Youtiva Financial Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    try:
        data = load_all_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()
    
    # Sidebar navigation - simplified to just 2 pages
    st.sidebar.title("📊 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["📊 All Data Tables", "🤖 AI Financial Assistant"]
    )
    
    if page == "📊 All Data Tables":
        show_all_data_tables(data)
    elif page == "🤖 AI Financial Assistant":
        show_ai_assistant(data)

def show_all_data_tables(data):
    """Show all data tables in a simple format"""
    st.markdown('<h2 class="section-header">All Financial Data Tables</h2>', unsafe_allow_html=True)
    
    # Chart of Accounts
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("📊 Chart of Accounts")
    st.write(f"**Total Records:** {len(data['chart_of_accounts'])}")
    st.dataframe(data['chart_of_accounts'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Vendors
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("🏢 Vendors")
    st.write(f"**Total Records:** {len(data['vendors'])}")
    st.dataframe(data['vendors'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Customers
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("👥 Customers")
    st.write(f"**Total Records:** {len(data['customers'])}")
    st.dataframe(data['customers'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Expenses
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("💸 Expenses")
    st.write(f"**Total Records:** {len(data['expenses'])}")
    st.dataframe(data['expenses'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Bills
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("📄 Bills")
    st.write(f"**Total Records:** {len(data['bills'])}")
    st.dataframe(data['bills'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Invoices
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("📋 Invoices")
    st.write(f"**Total Records:** {len(data['invoices'])}")
    st.dataframe(data['invoices'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Services
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("⚙️ Services")
    st.write(f"**Total Records:** {len(data['services'])}")
    st.dataframe(data['services'], use_container_width=True, height=300)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Financial Reports
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.subheader("📈 Financial Reports")
    
    # Create tabs for different reports
    tab1, tab2, tab3 = st.tabs(["📊 Balance Sheet", "💰 Cash Flow Statement", "📋 Profit & Loss"])
    
    with tab1:
        if 'balance_sheet' in data and data['balance_sheet']:
            st.markdown(data['balance_sheet'])
        else:
            st.error("Balance sheet report not found")
    
    with tab2:
        if 'cash_flow' in data and data['cash_flow']:
            st.markdown(data['cash_flow'])
        else:
            st.error("Cash flow statement not found")
    
    with tab3:
        if 'profit_loss' in data and data['profit_loss']:
            st.markdown(data['profit_loss'])
        else:
            st.error("Profit & loss statement not found")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_data_sources(relevant_sources):
    """Display relevant data sources below the AI response"""
    if not relevant_sources or not any(relevant_sources.values()):
        return
    
    st.markdown("---")
    st.markdown("### 📊 Data Sources")
    
    # Display filtered/specific data first (most relevant)
    if relevant_sources.get('filtered_data'):
        st.markdown("#### 🎯 Relevant Data")
        for data_name, df in relevant_sources['filtered_data'].items():
            if not df.empty:
                # Format the data name nicely
                display_name = data_name.replace('_', ' ').title()
                with st.expander(f"📋 {display_name} ({len(df)} records)", expanded=True):
                    st.dataframe(df, use_container_width=True, height=200)
    
    # Display full tables if referenced
    if relevant_sources.get('tables'):
        st.markdown("#### 📊 Referenced Tables")
        for table_name, df in relevant_sources['tables'].items():
            if not df.empty and table_name not in [name.split('_')[0] for name in relevant_sources.get('filtered_data', {}).keys()]:
                display_name = table_name.replace('_', ' ').title()
                with st.expander(f"📊 {display_name} (Full Table - {len(df)} records)"):
                    # Show only first 10 rows for full tables
                    st.dataframe(df.head(10), use_container_width=True, height=200)
                    if len(df) > 10:
                        st.info(f"Showing first 10 of {len(df)} records")
    
    # Display markdown reports if referenced
    if relevant_sources.get('reports'):
        st.markdown("#### 📈 Referenced Reports")
        for report_name, content in relevant_sources['reports'].items():
            if content and not content.startswith("Report") and not content.startswith("Error"):
                display_name = report_name.replace('_', ' ').title()
                with st.expander(f"📈 {display_name} Report"):
                    st.markdown(content)

def show_ai_assistant(data):
    st.markdown('<h2 class="section-header">AI Financial Assistant</h2>', unsafe_allow_html=True)
    
    # Initialize chatbot
    try:
        chatbot = FinancialChatBot()
        
        if not chatbot.is_configured():
            st.warning("⚠️ Please add your OpenAI API key to the .env file to use the AI assistant.")
            st.code("OPENAI_API_KEY=your_api_key_here")
            return
        
        st.info("💡 Ask me anything about your financial data! I can help analyze trends, explain metrics, and provide insights.")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Add clear chat button
        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your financial data..."):
            # Add user message to history and display
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                try:
                    # Get streaming response with sources
                    response_stream, relevant_sources = chatbot.get_financial_analysis_with_sources(prompt, data)
                    
                    # Check if response is a string (error message)
                    if isinstance(response_stream, str):
                        message_placeholder.markdown(response_stream)
                        st.session_state.messages.append({"role": "assistant", "content": response_stream})
                    else:
                        # Handle streaming response
                        for chunk in response_stream:
                            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                                content = chunk.choices[0].delta.content
                                # Clean the content to avoid formatting issues
                                full_response += content
                                # Update display with typing indicator
                                message_placeholder.markdown(full_response + " ▌")
                        
                        # Final message without cursor
                        message_placeholder.markdown(full_response)
                        st.session_state.messages.append({"role": "assistant", "content": full_response})
                        
                        # Display data sources below the response
                        display_data_sources(relevant_sources)
                        
                except Exception as e:
                    error_msg = f"❌ Error generating response: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
    
    except Exception as e:
        st.error(f"Error initializing AI assistant: {str(e)}")

if __name__ == "__main__":
    main()
