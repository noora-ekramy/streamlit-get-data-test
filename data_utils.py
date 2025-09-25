import pandas as pd
import os
from typing import Dict, Optional, List
from datetime import datetime
import numpy as np

class DataLoader:
    """
    Utility class for loading and processing financial CSV data files.
    Handles data validation, type conversion, and error handling.
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize DataLoader with the path to data directory.
        
        Args:
            data_directory: Path to directory containing CSV files
        """
        self.data_dir = data_directory
        self.file_paths = {
            'chart_of_accounts': os.path.join(data_directory, 'chart_of_accounts.csv'),
            'vendors': os.path.join(data_directory, 'vendors.csv'),
            'expenses': os.path.join(data_directory, 'expenses.csv'),
            'bills': os.path.join(data_directory, 'bills.csv'),
            'customers': os.path.join(data_directory, 'customers.csv'),
            'invoices': os.path.join(data_directory, 'invoices.csv'),
            'services': os.path.join(data_directory, 'services.csv'),
            'balance_sheet': os.path.join(data_directory, 'balance_sheet_report.md'),
            'cash_flow': os.path.join(data_directory, 'cash_flow_statement.md'),
            'profit_loss': os.path.join(data_directory, 'profit_loss_statement.md')
        }
    
    def validate_file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file exists, False otherwise
        """
        return os.path.exists(file_path)
    
    def load_csv_with_error_handling(self, file_path: str, expected_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load CSV file with comprehensive error handling and validation.
        
        Args:
            file_path: Path to CSV file
            expected_columns: List of expected column names
            
        Returns:
            Loaded and validated DataFrame
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.validate_file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Load CSV with error handling
            df = pd.read_csv(file_path)
            
            # Validate columns if specified
            if expected_columns:
                missing_columns = set(expected_columns) - set(df.columns)
                if missing_columns:
                    raise ValueError(f"Missing columns in {file_path}: {missing_columns}")
            
            # Basic data quality checks
            if df.empty:
                print(f"Warning: {file_path} is empty")
            
            return df
            
        except pd.errors.EmptyDataError:
            print(f"Warning: {file_path} is empty or contains no data")
            return pd.DataFrame()
        except pd.errors.ParserError as e:
            print(f"Error parsing {file_path}: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def load_chart_of_accounts(self) -> pd.DataFrame:
        """
        Load and process chart of accounts data.
        
        Returns:
            Processed chart of accounts DataFrame
        """
        expected_columns = ['account_code', 'account_name', 'account_type', 'balance']
        df = self.load_csv_with_error_handling(self.file_paths['chart_of_accounts'], expected_columns)
        
        if not df.empty:
            # Convert balance to numeric
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
            
            # Ensure account_code is string
            df['account_code'] = df['account_code'].astype(str)
            
            # Sort by account code
            df = df.sort_values('account_code')
        
        return df
    
    def load_vendors(self) -> pd.DataFrame:
        """
        Load and process vendors data.
        
        Returns:
            Processed vendors DataFrame
        """
        expected_columns = ['vendor_id', 'vendor_name', 'email', 'phone', 'active']
        df = self.load_csv_with_error_handling(self.file_paths['vendors'], expected_columns)
        
        if not df.empty:
            # Convert active to boolean
            df['active'] = df['active'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
            
            # Clean email and phone formatting
            if 'email' in df.columns:
                df['email'] = df['email'].str.lower().str.strip()
            
            # Ensure vendor_id is string
            df['vendor_id'] = df['vendor_id'].astype(str)
        
        return df
    
    def load_expenses(self) -> pd.DataFrame:
        """
        Load and process expenses data.
        
        Returns:
            Processed expenses DataFrame
        """
        expected_columns = ['expense_id', 'date', 'vendor_id', 'amount', 'status']
        df = self.load_csv_with_error_handling(self.file_paths['expenses'], expected_columns)
        
        if not df.empty:
            # Convert date column
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            # Convert amount to numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            
            # Ensure IDs are strings
            df['expense_id'] = df['expense_id'].astype(str)
            df['vendor_id'] = df['vendor_id'].astype(str)
            
            # Sort by date (newest first)
            df = df.sort_values('date', ascending=False, na_position='last')
        
        return df
    
    def load_bills(self) -> pd.DataFrame:
        """
        Load and process bills data.
        
        Returns:
            Processed bills DataFrame
        """
        expected_columns = ['bill_id', 'vendor_id', 'date_issued', 'due_date', 'amount', 'status']
        df = self.load_csv_with_error_handling(self.file_paths['bills'], expected_columns)
        
        if not df.empty:
            # Convert date columns
            date_columns = ['date_issued', 'due_date', 'payment_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert amount to numeric
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            
            # Ensure IDs are strings
            df['bill_id'] = df['bill_id'].astype(str)
            df['vendor_id'] = df['vendor_id'].astype(str)
            
            # Add days overdue calculation for outstanding bills
            if 'due_date' in df.columns and 'status' in df.columns:
                current_date = datetime.now()
                df['days_overdue'] = df.apply(lambda row: 
                    max(0, (current_date - row['due_date']).days) 
                    if row['status'] == 'Outstanding' and pd.notna(row['due_date']) 
                    else 0, axis=1)
            
            # Sort by due date
            df = df.sort_values('due_date', ascending=True, na_position='last')
        
        return df
    
    def load_customers(self) -> pd.DataFrame:
        """
        Load and process customers data.
        
        Returns:
            Processed customers DataFrame
        """
        expected_columns = ['customer_id', 'customer_name', 'email', 'phone', 'credit_limit', 'active']
        df = self.load_csv_with_error_handling(self.file_paths['customers'], expected_columns)
        
        if not df.empty:
            # Convert active to boolean
            df['active'] = df['active'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
            
            # Convert credit_limit to numeric
            df['credit_limit'] = pd.to_numeric(df['credit_limit'], errors='coerce').fillna(0)
            
            # Clean email formatting
            if 'email' in df.columns:
                df['email'] = df['email'].str.lower().str.strip()
            
            # Ensure customer_id is string
            df['customer_id'] = df['customer_id'].astype(str)
        
        return df
    
    def load_invoices(self) -> pd.DataFrame:
        """
        Load and process invoices data.
        
        Returns:
            Processed invoices DataFrame
        """
        expected_columns = ['invoice_id', 'customer_id', 'date_issued', 'due_date', 'amount', 'status']
        df = self.load_csv_with_error_handling(self.file_paths['invoices'], expected_columns)
        
        if not df.empty:
            # Convert date columns
            date_columns = ['date_issued', 'due_date', 'payment_date']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Convert amount and tax_amount to numeric
            numeric_columns = ['amount', 'tax_amount', 'discount_amount']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Ensure IDs are strings
            df['invoice_id'] = df['invoice_id'].astype(str)
            df['customer_id'] = df['customer_id'].astype(str)
            
            # Add days overdue calculation for outstanding invoices
            if 'due_date' in df.columns and 'status' in df.columns:
                current_date = datetime.now()
                df['days_overdue'] = df.apply(lambda row: 
                    max(0, (current_date - row['due_date']).days) 
                    if row['status'] == 'Outstanding' and pd.notna(row['due_date']) 
                    else 0, axis=1)
            
            # Sort by date issued (newest first)
            df = df.sort_values('date_issued', ascending=False, na_position='last')
        
        return df
    
    def load_services(self) -> pd.DataFrame:
        """
        Load and process services data.
        
        Returns:
            Processed services DataFrame
        """
        expected_columns = ['service_id', 'service_name', 'service_category', 'hourly_rate', 'active']
        df = self.load_csv_with_error_handling(self.file_paths['services'], expected_columns)
        
        if not df.empty:
            # Convert active to boolean
            df['active'] = df['active'].map({'TRUE': True, 'FALSE': False, True: True, False: False})
            
            # Convert rate and price columns to numeric
            numeric_columns = ['hourly_rate', 'standard_price']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Ensure service_id is string
            df['service_id'] = df['service_id'].astype(str)
            
            # Sort by service name
            df = df.sort_values('service_name')
        
        return df
    
    def load_markdown_report(self, report_name: str) -> str:
        """
        Load markdown report file.
        
        Args:
            report_name: Name of the report (balance_sheet, cash_flow, profit_loss)
            
        Returns:
            Content of the markdown file as string
        """
        file_path = self.file_paths.get(report_name)
        if not file_path or not self.validate_file_exists(file_path):
            return f"Report {report_name} not found"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error loading {report_name}: {str(e)}"
    
    def load_all_reports(self) -> Dict[str, str]:
        """
        Load all markdown financial reports.
        
        Returns:
            Dictionary containing all loaded markdown reports
        """
        reports = {}
        report_names = ['balance_sheet', 'cash_flow', 'profit_loss']
        
        for report_name in report_names:
            reports[report_name] = self.load_markdown_report(report_name)
        
        return reports
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all financial data files.
        
        Returns:
            Dictionary containing all loaded DataFrames
        """
        data = {}
        
        loaders = {
            'chart_of_accounts': self.load_chart_of_accounts,
            'vendors': self.load_vendors,
            'expenses': self.load_expenses,
            'bills': self.load_bills,
            'customers': self.load_customers,
            'invoices': self.load_invoices,
            'services': self.load_services
        }
        
        for name, loader_func in loaders.items():
            try:
                data[name] = loader_func()
                print(f"✅ Loaded {name}: {len(data[name])} records")
            except Exception as e:
                print(f"❌ Error loading {name}: {e}")
                data[name] = pd.DataFrame()
        
        return data
    
    def get_data_summary(self) -> Dict[str, dict]:
        """
        Get a summary of all data files including record counts and basic statistics.
        
        Returns:
            Dictionary containing summary statistics for each dataset
        """
        data = self.load_all_data()
        summary = {}
        
        for name, df in data.items():
            if not df.empty:
                summary[name] = {
                    'record_count': len(df),
                    'columns': list(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                    'null_counts': df.isnull().sum().to_dict()
                }
                
                # Add specific metrics for different data types
                if name == 'invoices':
                    summary[name]['total_amount'] = df['amount'].sum()
                    summary[name]['outstanding_amount'] = df[df['status'] == 'Outstanding']['amount'].sum()
                
                elif name == 'expenses':
                    summary[name]['total_amount'] = df['amount'].sum()
                    summary[name]['categories'] = df['category'].nunique() if 'category' in df.columns else 0
                
                elif name == 'bills':
                    summary[name]['total_amount'] = df['amount'].sum()
                    summary[name]['outstanding_amount'] = df[df['status'] == 'Outstanding']['amount'].sum()
                
                elif name == 'chart_of_accounts':
                    summary[name]['total_balance'] = df['balance'].sum()
                    summary[name]['account_types'] = df['account_type'].nunique()
            else:
                summary[name] = {'record_count': 0, 'error': 'No data loaded'}
        
        return summary
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """
        Validate data integrity across all datasets.
        
        Returns:
            Dictionary containing validation issues for each dataset
        """
        data = self.load_all_data()
        issues = {}
        
        # Check for missing required fields
        for name, df in data.items():
            dataset_issues = []
            
            if df.empty:
                dataset_issues.append("Dataset is empty")
                continue
            
            # Check for duplicate IDs
            id_columns = [col for col in df.columns if col.endswith('_id')]
            for id_col in id_columns:
                if df[id_col].duplicated().any():
                    dataset_issues.append(f"Duplicate {id_col} found")
            
            # Check for negative amounts where not expected
            if 'amount' in df.columns:
                if (df['amount'] < 0).any():
                    dataset_issues.append("Negative amounts found")
            
            # Check for future dates in historical data
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for date_col in date_columns:
                if date_col in df.columns:
                    future_dates = df[df[date_col] > datetime.now()][date_col]
                    if not future_dates.empty:
                        dataset_issues.append(f"Future dates found in {date_col}")
            
            issues[name] = dataset_issues
        
        return issues

# Utility functions for data analysis
class FinancialAnalyzer:
    """Helper class for financial data analysis and calculations."""
    
    @staticmethod
    def calculate_financial_ratios(data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate key financial ratios from the data."""
        ratios = {}
        
        try:
            # Load data
            invoices = data['invoices']
            expenses = data['expenses']
            bills = data['bills']
            
            # Revenue metrics
            total_revenue = invoices['amount'].sum()
            outstanding_receivables = invoices[invoices['status'] == 'Outstanding']['amount'].sum()
            
            # Expense metrics
            total_expenses = expenses['amount'].sum()
            outstanding_payables = bills[bills['status'] == 'Outstanding']['amount'].sum()
            
            # Calculate ratios
            ratios['collection_efficiency'] = ((total_revenue - outstanding_receivables) / total_revenue * 100) if total_revenue > 0 else 0
            ratios['profit_margin'] = ((total_revenue - total_expenses) / total_revenue * 100) if total_revenue > 0 else 0
            ratios['payables_ratio'] = (outstanding_payables / total_expenses * 100) if total_expenses > 0 else 0
            ratios['receivables_ratio'] = (outstanding_receivables / total_revenue * 100) if total_revenue > 0 else 0
            
        except Exception as e:
            print(f"Error calculating financial ratios: {e}")
        
        return ratios
    
    @staticmethod
    def get_top_customers_by_revenue(data: Dict[str, pd.DataFrame], top_n: int = 5) -> pd.DataFrame:
        """Get top customers by revenue."""
        invoices = data['invoices']
        customers = data['customers']
        
        customer_revenue = invoices.groupby('customer_id')['amount'].sum().reset_index()
        customer_revenue = customer_revenue.merge(customers[['customer_id', 'customer_name']], on='customer_id', how='left')
        
        return customer_revenue.nlargest(top_n, 'amount')
    
    @staticmethod
    def get_expense_trends(data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Analyze expense trends over time."""
        expenses = data['expenses'].copy()
        expenses['date'] = pd.to_datetime(expenses['date'])
        expenses['month'] = expenses['date'].dt.to_period('M')
        
        monthly_expenses = expenses.groupby(['month', 'category'])['amount'].sum().reset_index()
        
        return monthly_expenses

# Example usage and testing
if __name__ == "__main__":
    # Test data loading
    loader = DataLoader()
    
    print("Testing data loading...")
    try:
        data = loader.load_all_data()
        summary = loader.get_data_summary()
        
        print("\nData Summary:")
        for dataset, info in summary.items():
            print(f"{dataset}: {info.get('record_count', 0)} records")
        
        print("\nValidating data integrity...")
        issues = loader.validate_data_integrity()
        for dataset, dataset_issues in issues.items():
            if dataset_issues:
                print(f"{dataset}: {', '.join(dataset_issues)}")
            else:
                print(f"{dataset}: No issues found")
        
        print("\n✅ Data loading test completed successfully")
        
    except Exception as e:
        print(f"❌ Data loading test failed: {e}")
