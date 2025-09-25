from openai import OpenAI
import os
import pandas as pd
from datetime import datetime
import json
import re
from typing import Dict, Any, Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FinancialChatBot:
    """
    A ChatGPT-powered financial analysis assistant that can analyze
    financial data and provide insights, recommendations, and explanations.
    """
    
    def __init__(self):
        """Initialize the FinancialChatBot with OpenAI API configuration."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        
        # System prompt for financial analysis context
        self.system_prompt = """
        You are a friendly and professional financial analyst assistant for Youtiva Technology Solutions. 
        You can engage in casual conversation while providing expert financial analysis.
        
        You have access to comprehensive financial data including:
        - Chart of accounts with account codes and balances
        - Vendor information and payment terms
        - Customer data and credit limits
        - Expense transactions with categories and dates
        - Bills (accounts payable) with status tracking
        - Invoices (accounts receivable) with payment status
        - Service portfolio with pricing information
        
        Your role is to:
        1. Have natural conversations about financial topics
        2. Analyze financial data and identify trends, patterns, and insights
        3. Provide clear, actionable recommendations for business improvement
        4. Explain financial concepts in accessible terms
        5. Help with budgeting, forecasting, and financial planning
        6. Identify potential risks and opportunities
        
        When asked about general topics or your identity, respond naturally and conversationally.
        When analyzing financial data, be specific with numbers and use proper formatting.
        Always provide clean, well-formatted responses without HTML entities or encoding issues.
        Be helpful, friendly, and professional in all interactions.
        """
    
    def is_configured(self) -> bool:
        """Check if the OpenAI API key is configured."""
        return bool(self.api_key and self.client)
    
    def prepare_financial_summary(self, data: Dict) -> str:
        """
        Prepare a comprehensive financial summary from the data for AI analysis.
        
        Args:
            data: Dictionary containing all financial DataFrames and reports
            
        Returns:
            String summary of financial data
        """
        summary = []
        
        try:
            # Check if we have markdown reports and include key insights
            if 'balance_sheet' in data and isinstance(data['balance_sheet'], str):
                summary.append("BALANCE SHEET HIGHLIGHTS:")
                # Extract key metrics from balance sheet report
                if "Total Assets" in data['balance_sheet']:
                    summary.append("- Balance sheet with detailed asset, liability, and equity breakdown available")
                if "Current Ratio" in data['balance_sheet']:
                    summary.append("- Financial ratios and liquidity analysis included")
            
            if 'cash_flow' in data and isinstance(data['cash_flow'], str):
                summary.append("\nCASH FLOW HIGHLIGHTS:")
                if "Operating Activities" in data['cash_flow']:
                    summary.append("- Detailed cash flow from operating, investing, and financing activities")
                if "Free Cash Flow" in data['cash_flow']:
                    summary.append("- Free cash flow and cash conversion metrics available")
            
            if 'profit_loss' in data and isinstance(data['profit_loss'], str):
                summary.append("\nPROFIT & LOSS HIGHLIGHTS:")
                if "Revenue" in data['profit_loss']:
                    summary.append("- Comprehensive P&L with quarterly breakdowns")
                if "Gross Profit Margin" in data['profit_loss']:
                    summary.append("- Profitability ratios and margin analysis included")
            
            summary.append("\nDETAILED TRANSACTION DATA:")
            
            # Continue with existing data processing
            # Revenue summary
            invoices = data.get('invoices')
            if invoices is not None and hasattr(invoices, 'shape'):
                total_revenue = invoices['amount'].sum()
                outstanding_invoices = invoices[invoices['status'] == 'Outstanding']['amount'].sum()
                paid_invoices = invoices[invoices['status'] == 'Paid']['amount'].sum()
                
                summary.append(f"REVENUE ANALYSIS:")
                summary.append(f"- Total Revenue: ${total_revenue:,.2f}")
                summary.append(f"- Outstanding Invoices: ${outstanding_invoices:,.2f}")
                summary.append(f"- Paid Invoices: ${paid_invoices:,.2f}")
                summary.append(f"- Collection Rate: {(paid_invoices/total_revenue)*100:.1f}%")
            
            # Expense summary
            expenses = data.get('expenses')
            if expenses is not None and hasattr(expenses, 'shape'):
                total_expenses = expenses['amount'].sum()
                expense_categories = expenses.groupby('category')['amount'].sum().sort_values(ascending=False)
                
                summary.append(f"\nEXPENSE ANALYSIS:")
                summary.append(f"- Total Expenses: ${total_expenses:,.2f}")
                summary.append(f"- Top 3 Expense Categories:")
                for i, (category, amount) in enumerate(expense_categories.head(3).items()):
                    summary.append(f"  {i+1}. {category}: ${amount:,.2f}")
                
                # Profitability (only if we have both revenue and expenses)
                if 'total_revenue' in locals():
                    gross_profit = total_revenue - total_expenses
                    profit_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
                    
                    summary.append(f"\nPROFITABILITY:")
                    summary.append(f"- Gross Profit: ${gross_profit:,.2f}")
                    summary.append(f"- Profit Margin: {profit_margin:.1f}%")
            
            # Cash flow indicators
            bills = data.get('bills')
            if bills is not None and hasattr(bills, 'shape'):
                outstanding_bills = bills[bills['status'] == 'Outstanding']['amount'].sum()
                
                summary.append(f"\nCASH FLOW INDICATORS:")
                summary.append(f"- Outstanding Bills (Payables): ${outstanding_bills:,.2f}")
                
                # Only add working capital if we have both outstanding invoices and bills
                if 'outstanding_invoices' in locals():
                    summary.append(f"- Net Working Capital Impact: ${outstanding_invoices - outstanding_bills:,.2f}")
            
            # Customer and vendor counts
            customers = data.get('customers')
            vendors = data.get('vendors')
            if customers is not None and vendors is not None:
                active_customers = len(customers[customers['active'] == True])
                active_vendors = len(vendors[vendors['active'] == True])
                
                summary.append(f"\nBUSINESS RELATIONSHIPS:")
                summary.append(f"- Active Customers: {active_customers}")
                summary.append(f"- Active Vendors: {active_vendors}")
                if 'credit_limit' in customers.columns:
                    summary.append(f"- Average Customer Credit Limit: ${customers['credit_limit'].mean():,.2f}")
            
            # Service portfolio
            services = data.get('services')
            if services is not None and hasattr(services, 'shape'):
                avg_hourly_rate = services['hourly_rate'].mean()
                total_services = len(services[services['active'] == True])
                
                summary.append(f"\nSERVICE PORTFOLIO:")
                summary.append(f"- Active Services: {total_services}")
                summary.append(f"- Average Hourly Rate: ${avg_hourly_rate:.2f}")
            
            # Add note about comprehensive reports available
            summary.append(f"\nADDITIONAL ANALYSIS:")
            summary.append(f"- Comprehensive Balance Sheet, Cash Flow, and P&L reports are available")
            summary.append(f"- Detailed financial ratios and trend analysis included in reports")
            summary.append(f"- Ask specific questions to get insights from any aspect of the financial data")
            
        except Exception as e:
            summary.append(f"Error preparing financial summary: {str(e)}")
        
        return "\n".join(summary)
    
    def extract_relevant_data(self, user_question: str, data: Dict) -> Dict[str, Any]:
        """
        Extract relevant data sources based on the user's question.
        
        Args:
            user_question: The user's question
            data: Dictionary containing all financial data
            
        Returns:
            Dictionary with relevant tables and reports
        """
        relevant_sources = {
            'tables': {},
            'reports': {},
            'filtered_data': {}
        }
        
        question_lower = user_question.lower()
        
        # Map keywords to data sources
        keyword_mapping = {
            'invoice': 'invoices',
            'bill': 'bills', 
            'expense': 'expenses',
            'vendor': 'vendors',
            'customer': 'customers',
            'service': 'services',
            'account': 'chart_of_accounts',
            'balance sheet': 'balance_sheet',
            'cash flow': 'cash_flow',
            'profit': 'profit_loss',
            'revenue': 'invoices',
            'income': 'invoices',
            'cost': 'expenses',
            'payable': 'bills',
            'receivable': 'invoices'
        }
        
        # Check which data sources are relevant
        for keyword, source in keyword_mapping.items():
            if keyword in question_lower:
                if source in data:
                    if isinstance(data[source], pd.DataFrame):
                        relevant_sources['tables'][source] = data[source].copy()
                    elif isinstance(data[source], str):
                        relevant_sources['reports'][source] = data[source]
        
        # Extract date ranges if mentioned
        date_patterns = [
            r'(\d{4})',  # Year
            r'(\d{1,2}[-/]\d{4})',  # Month/Year
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # Full date
            r'(january|february|march|april|may|june|july|august|september|october|november|december)',  # Month names
            r'(last\s+\w+|this\s+\w+|past\s+\w+)'  # Relative dates
        ]
        
        date_filters = []
        for pattern in date_patterns:
            matches = re.findall(pattern, question_lower, re.IGNORECASE)
            date_filters.extend(matches)
        
        # Apply filters to relevant tables
        if date_filters:
            for table_name, df in relevant_sources['tables'].items():
                if not df.empty:
                    # Try to filter by date columns
                    date_columns = [col for col in df.columns if 'date' in col.lower()]
                    if date_columns and len(df) > 0:
                        # For demo, just take recent records if date filtering is requested
                        if len(df) > 10:
                            relevant_sources['filtered_data'][f'{table_name}_recent'] = df.head(10)
        
        # Check for specific status filters
        status_keywords = ['outstanding', 'paid', 'pending', 'active', 'overdue']
        for status in status_keywords:
            if status in question_lower:
                for table_name, df in relevant_sources['tables'].items():
                    if 'status' in df.columns:
                        if status == 'outstanding':
                            filtered_df = df[df['status'] == 'Outstanding']
                        elif status == 'paid':
                            filtered_df = df[df['status'] == 'Paid']
                        elif status == 'active':
                            filtered_df = df[df.get('active', True) == True]
                        else:
                            continue
                        
                        if not filtered_df.empty:
                            relevant_sources['filtered_data'][f'{table_name}_{status}'] = filtered_df
        
        # Check for amount/value filters
        if any(word in question_lower for word in ['top', 'highest', 'largest', 'biggest']):
            for table_name, df in relevant_sources['tables'].items():
                if 'amount' in df.columns and len(df) > 0:
                    top_records = df.nlargest(5, 'amount')
                    relevant_sources['filtered_data'][f'{table_name}_top'] = top_records
        
        if any(word in question_lower for word in ['bottom', 'lowest', 'smallest']):
            for table_name, df in relevant_sources['tables'].items():
                if 'amount' in df.columns and len(df) > 0:
                    bottom_records = df.nsmallest(5, 'amount')
                    relevant_sources['filtered_data'][f'{table_name}_bottom'] = bottom_records
        
        return relevant_sources
    
    def get_financial_analysis_with_sources(self, user_question: str, data: Dict) -> Tuple[str, Dict[str, Any]]:
        """
        Get AI-powered financial analysis with relevant data sources.
        
        Args:
            user_question: The user's question about financial data
            data: Dictionary containing all financial DataFrames and reports
            
        Returns:
            Tuple of (AI response, relevant data sources)
        """
        if not self.is_configured():
            return "❌ OpenAI API key not configured. Please add your API key to the .env file.", {}
        
        try:
            # Extract relevant data sources
            relevant_sources = self.extract_relevant_data(user_question, data)
            
            # Check if question is about financial analysis or general conversation
            financial_keywords = ['revenue', 'expense', 'profit', 'cash', 'invoice', 'bill', 'customer', 'vendor', 'financial', 'money', 'cost', 'income', 'balance', 'account']
            needs_financial_data = any(keyword in user_question.lower() for keyword in financial_keywords)
            
            if needs_financial_data:
                # Prepare financial data summary for financial questions
                financial_summary = self.prepare_financial_summary(data)
                user_message = f"""
                Based on the following financial data for Youtiva Technology Solutions:
                
                {financial_summary}
                
                User Question: {user_question}
                
                Please provide a detailed analysis with specific insights and actionable recommendations.
                """
            else:
                # For general questions, just use the question directly
                user_message = user_question
            
            # Make API call to OpenAI with streaming
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.7,
                stream=True
            )
            
            return response, relevant_sources
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                error_response = "❌ Invalid OpenAI API key. Please check your API key in the .env file."
            elif "rate limit" in error_msg:
                error_response = "⏳ OpenAI API rate limit exceeded. Please try again later."
            elif "quota" in error_msg:
                error_response = "💳 OpenAI quota exceeded. Please check your billing."
            else:
                error_response = f"❌ Error generating analysis: {str(e)}"
            
            return error_response, {}
    
    def get_financial_analysis(self, user_question: str, data: Dict) -> str:
        """
        Get AI-powered financial analysis (legacy method for compatibility).
        
        Args:
            user_question: The user's question about financial data
            data: Dictionary containing all financial DataFrames
            
        Returns:
            AI-generated financial analysis and insights
        """
        if not self.is_configured():
            return "❌ OpenAI API key not configured. Please add your API key to the .env file."
        
        try:
            # Check if question is about financial analysis or general conversation
            financial_keywords = ['revenue', 'expense', 'profit', 'cash', 'invoice', 'bill', 'customer', 'vendor', 'financial', 'money', 'cost', 'income', 'balance', 'account']
            needs_financial_data = any(keyword in user_question.lower() for keyword in financial_keywords)
            
            if needs_financial_data:
                # Prepare financial data summary for financial questions
                financial_summary = self.prepare_financial_summary(data)
                user_message = f"""
                Based on the following financial data for Youtiva Technology Solutions:
                
                {financial_summary}
                
                User Question: {user_question}
                
                Please provide a detailed analysis with specific insights and actionable recommendations.
                """
            else:
                # For general questions, just use the question directly
                user_message = user_question
            
            # Make API call to OpenAI with streaming
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.7,
                stream=True
            )
            
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                return "❌ Invalid OpenAI API key. Please check your API key in the .env file."
            elif "rate limit" in error_msg:
                return "⏳ OpenAI API rate limit exceeded. Please try again later."
            elif "quota" in error_msg:
                return "💳 OpenAI quota exceeded. Please check your billing."
            else:
                return f"❌ Error generating analysis: {str(e)}"
    
    def get_financial_analysis_non_streaming(self, user_question: str, data: Dict[str, pd.DataFrame]) -> str:
        """
        Get AI-powered financial analysis (non-streaming version for compatibility).
        
        Args:
            user_question: The user's question about financial data
            data: Dictionary containing all financial DataFrames
            
        Returns:
            AI-generated financial analysis and insights
        """
        if not self.is_configured():
            return "❌ OpenAI API key not configured. Please add your API key to the .env file."
        
        try:
            # Prepare financial data summary
            financial_summary = self.prepare_financial_summary(data)
            
            # Create the user message with context
            user_message = f"""
            Based on the following financial data for Youtiva Technology Solutions:
            
            {financial_summary}
            
            User Question: {user_question}
            
            Please provide a detailed, professional analysis with specific insights and actionable recommendations.
            """
            
            # Make API call to OpenAI without streaming
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1500,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "api key" in error_msg:
                return "❌ Invalid OpenAI API key. Please check your API key in the .env file."
            elif "rate limit" in error_msg:
                return "⏳ OpenAI API rate limit exceeded. Please try again later."
            elif "quota" in error_msg:
                return "💳 OpenAI quota exceeded. Please check your billing."
            else:
                return f"❌ Error generating analysis: {str(e)}"
    
    def get_quick_insights(self, data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Generate quick financial insights for dashboard display.
        
        Args:
            data: Dictionary containing all financial DataFrames
            
        Returns:
            Dictionary of insight categories and their analysis
        """
        insights = {}
        
        try:
            # Revenue health
            revenue_question = "Analyze our revenue health and trends. What are the key strengths and areas for improvement?"
            insights['revenue'] = self.get_financial_analysis(revenue_question, data)
            
            # Cash flow
            cashflow_question = "Analyze our cash flow situation, including receivables and payables management."
            insights['cashflow'] = self.get_financial_analysis(cashflow_question, data)
            
            # Expense optimization
            expense_question = "Review our expense patterns and suggest cost optimization opportunities."
            insights['expenses'] = self.get_financial_analysis(expense_question, data)
            
            # Business growth
            growth_question = "Based on our financial data, what opportunities do you see for business growth?"
            insights['growth'] = self.get_financial_analysis(growth_question, data)
            
        except Exception as e:
            insights['error'] = f"Error generating insights: {str(e)}"
        
        return insights
    
    def explain_financial_metric(self, metric_name: str, current_value: float, data: Dict[str, pd.DataFrame]) -> str:
        """
        Explain a specific financial metric in context.
        
        Args:
            metric_name: Name of the financial metric
            current_value: Current value of the metric
            data: Financial data for context
            
        Returns:
            Explanation of the metric and its implications
        """
        question = f"""
        Please explain the financial metric '{metric_name}' with a current value of {current_value}.
        
        Include:
        1. What this metric means for our business
        2. Whether this is a good or concerning value
        3. Industry context if relevant
        4. Specific recommendations for improvement
        5. How this metric relates to our overall financial health
        """
        
        return self.get_financial_analysis(question, data)
    
    def generate_financial_report(self, report_type: str, data: Dict[str, pd.DataFrame]) -> str:
        """
        Generate a comprehensive financial report.
        
        Args:
            report_type: Type of report (summary, detailed, executive)
            data: Financial data
            
        Returns:
            Generated financial report
        """
        if report_type == "executive":
            question = """
            Create an executive summary of our financial performance including:
            - Key financial highlights
            - Major achievements and concerns
            - Strategic recommendations
            - Risk assessment
            """
        elif report_type == "detailed":
            question = """
            Create a detailed financial analysis covering:
            - Revenue analysis by source and trend
            - Expense breakdown and efficiency
            - Cash flow and working capital analysis
            - Customer and vendor relationship insights
            - Service portfolio performance
            """
        else:  # summary
            question = """
            Create a financial summary highlighting:
            - Current financial position
            - Key performance indicators
            - Notable trends
            - Immediate action items
            """
        
        return self.get_financial_analysis(question, data)

# Example usage and testing functions
def test_chatbot():
    """Test function to verify chatbot functionality."""
    bot = FinancialChatBot()
    
    if not bot.is_configured():
        print("⚠️  OpenAI API key not configured")
        return False
    
    # Test with sample data
    sample_data = {
        'invoices': pd.DataFrame({
            'amount': [1000, 2000, 1500],
            'status': ['Paid', 'Outstanding', 'Paid']
        }),
        'expenses': pd.DataFrame({
            'amount': [500, 300, 200],
            'category': ['Office', 'Travel', 'Software']
        })
    }
    
    try:
        response = bot.get_financial_analysis("What is our revenue situation?", sample_data)
        print("✅ ChatBot test successful")
        return True
    except Exception as e:
        print(f"❌ ChatBot test failed: {e}")
        return False

if __name__ == "__main__":
    test_chatbot()
