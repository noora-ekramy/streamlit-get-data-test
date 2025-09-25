# 💰 Youtiva Financial Dashboard

A comprehensive financial data visualization and analysis dashboard built with Streamlit, featuring AI-powered financial insights using ChatGPT integration.

## 🚀 Features

### 📊 Financial Data Management
- **Chart of Accounts**: Complete accounting structure with balances
- **Vendor Management**: Track supplier information and payment terms
- **Customer Database**: Manage client relationships and credit limits
- **Transaction Tracking**: Monitor expenses, bills, and invoices
- **Service Portfolio**: Catalog of services with pricing

### 📈 Interactive Dashboards
- **Financial Overview**: Key metrics and performance indicators
- **Revenue Analysis**: Monthly trends and customer insights
- **Expense Tracking**: Category breakdown and spending patterns
- **Cash Flow Monitoring**: Outstanding receivables and payables
- **Visual Analytics**: Interactive charts and graphs

### 🤖 AI Financial Assistant
- **ChatGPT Integration**: Natural language financial analysis
- **Intelligent Insights**: Automated trend detection and recommendations
- **Custom Queries**: Ask specific questions about your financial data
- **Report Generation**: AI-powered financial reports and summaries

## 📁 Project Structure

```
Youtiva_show_case/
├── main.py                    # Main Streamlit application
├── chatgpt_integration.py     # AI assistant functionality
├── data_utils.py             # Data loading and processing utilities
├── requirements.txt          # Python dependencies
├── env_template.txt          # Environment variables template
├── README.md                 # This file
└── data/                     # Financial data files
    ├── chart_of_accounts.csv
    ├── vendors.csv
    ├── customers.csv
    ├── expenses.csv
    ├── bills.csv
    ├── invoices.csv
    ├── services.csv
    ├── balance_sheet_report.md
    ├── cash_flow_statement.md
    └── profit_loss_statement.md
```

## 🛠️ Setup Instructions

### 1. Clone or Download the Project
```bash
cd Youtiva_show_case
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Copy the template file
cp env_template.txt .env

# Edit .env file and add your OpenAI API key
OPENAI_API_KEY=your_actual_api_key_here
```

### 4. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Create an account or log in
3. Generate a new API key
4. Add the key to your `.env` file

### 5. Run the Application
```bash
streamlit run main.py
```

The dashboard will open in your browser at `http://localhost:8501`

## 📋 Usage Guide

### Dashboard Navigation
- **📈 Financial Overview**: Start here for key metrics and trends
- **💳 Accounts & Chart**: Explore your chart of accounts structure
- **👥 Vendors & Customers**: Manage business relationships
- **💰 Transactions**: Review expenses, bills, and invoices
- **📋 Services**: Browse your service portfolio
- **🤖 AI Financial Assistant**: Get AI-powered insights

### AI Assistant Features
- Ask natural language questions about your financial data
- Get automated analysis of revenue trends
- Receive expense optimization recommendations
- Generate custom financial reports
- Explain complex financial metrics

### Example AI Queries
- "Analyze our revenue trends over the past quarter"
- "What are our top expense categories and how can we optimize them?"
- "Which customers generate the most revenue?"
- "What's our cash flow situation looking like?"
- "Identify any outstanding payments that need attention"

## 📊 Data Structure

### CSV Files Include:
- **Chart of Accounts**: Account codes, names, types, and balances
- **Vendors**: Supplier information with contact details and payment terms
- **Customers**: Client data with credit limits and contact information
- **Expenses**: Transaction records with vendor links and categories
- **Bills**: Accounts payable with due dates and payment status
- **Invoices**: Accounts receivable with customer links and amounts
- **Services**: Service catalog with pricing and categorization

### Financial Reports:
- **Balance Sheet**: Assets, liabilities, and equity breakdown
- **Cash Flow Statement**: Operating, investing, and financing activities
- **Profit & Loss**: Revenue, expenses, and profitability analysis

## 🔧 Customization

### Adding New Data
1. Add CSV files to the `data/` directory
2. Update `data_utils.py` to include new data loaders
3. Modify `main.py` to display new data sections

### Modifying Charts
- Charts use Plotly for interactivity
- Customize colors, layouts, and chart types in `main.py`
- Add new visualization types as needed

### Extending AI Features
- Modify prompts in `chatgpt_integration.py`
- Add specialized analysis functions
- Create custom report templates

## 🚀 Deployment Options

### Local Development
```bash
streamlit run main.py
```

### Production Deployment
1. **Streamlit Cloud**: Connect your GitHub repository
2. **Heroku**: Use the included `requirements.txt`
3. **AWS/GCP**: Deploy using container services
4. **Docker**: Create a Dockerfile for containerization

### Environment Variables for Production
```bash
OPENAI_API_KEY=your_api_key
DEBUG=False
FORCE_HTTPS=True
```

## 🔒 Security Considerations

- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper authentication for production use
- Consider rate limiting for AI features
- Validate all user inputs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues:

**"File not found" errors:**
- Ensure all CSV files are in the `data/` directory
- Check file permissions

**OpenAI API errors:**
- Verify your API key is correct
- Check your OpenAI account has available credits
- Ensure you're using the correct model name

**Streamlit import errors:**
- Install all dependencies: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

**Data loading issues:**
- Verify CSV file formats match expected structure
- Check for missing required columns
- Look for special characters in data

### Getting Help:
- Check the Streamlit [documentation](https://docs.streamlit.io/)
- Review OpenAI [API documentation](https://platform.openai.com/docs)
- Submit issues for bugs or feature requests

## 📊 Sample Data Information

The included sample data represents a fictional technology consulting company "Youtiva Technology Solutions" with:
- 70+ chart of accounts entries
- 20 vendors across various categories
- 25 customers from different industries
- 50+ expense transactions
- 40 bills and invoices
- 40 service offerings
- Comprehensive financial reports

This data provides a realistic foundation for testing and demonstration purposes.

---

**Built with ❤️ using Streamlit, Plotly, and OpenAI**
