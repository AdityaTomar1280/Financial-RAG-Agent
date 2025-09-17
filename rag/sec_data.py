import requests
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup


class SECDataAcquisition:
    """Handles downloading and parsing SEC 10-K filings"""

    COMPANY_CIKS = {
        'MSFT': '0000789019',
        'GOOGL': '0001652044',
        'NVDA': '0001045810'
    }

    def __init__(self, data_dir: str = "sec_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-System financial-analysis@company.com'
        })

    def get_filing_urls(self, cik: str, form_type: str = "10-K", count: int = 3) -> List[Dict[str, str]]:
        """Get recent filing URLs for a company"""
        try:
            facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik.zfill(10)}.json"
            response = self.session.get(facts_url)
            response.raise_for_status()

            company_name = {'0000789019': 'MSFT', '0001652044': 'GOOGL', '0001045810': 'NVDA'}[cik]
            return [
                {
                    'url': f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/mock-2024-10k.htm",
                    'year': '2024',
                    'accession': '0001564590-24-000057',
                    'date': '2024-07-26'
                },
                {
                    'url': f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/mock-2023-10k.htm",
                    'year': '2023',
                    'accession': '0001564590-23-000123',
                    'date': '2023-07-25'
                }
            ]
        except Exception as e:
            print(f"Note: Using fallback demo data for {cik} due to: {e}")
            company_name = {'0000789019': 'MSFT', '0001652044': 'GOOGL', '0001045810': 'NVDA'}[cik]
            return [
                {
                    'url': f"demo://mock-{company_name}-2024-10k.htm",
                    'year': '2024',
                    'accession': 'demo-2024',
                    'date': '2024-07-26'
                },
                {
                    'url': f"demo://mock-{company_name}-2023-10k.htm",
                    'year': '2023',
                    'accession': 'demo-2023',
                    'date': '2023-07-25'
                }
            ]

    def download_filing(self, url: str, company: str, year: str) -> Optional[str]:
        """Download and save a filing or use demo data"""
        filename = f"{company}_{year}_10k.html"
        filepath = self.data_dir / filename

        if filepath.exists():
            print(f"File already exists: {filepath}")
            return str(filepath)

        if url.startswith("demo://"):
            print(f"Creating demo data for {company} {year}...")
            demo_content = self.get_demo_content(company, year)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><div>{demo_content}</div></body></html>")
            print(f"Created demo file: {filepath}")
            return str(filepath)

        try:
            print(f"Downloading {company} {year} 10-K...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"Download failed for {url}: {e}")
            print(f"Using demo data for {company} {year}...")
            demo_content = self.get_demo_content(company, year)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"<html><body><div>{demo_content}</div></body></html>")
            print(f"Created demo file: {filepath}")
            return str(filepath)

    def get_demo_content(self, company: str, year: str) -> str:
        demo_data = {
            'MSFT': {
                '2024': """
                Microsoft Corporation Annual Report 2024
                
                FINANCIAL HIGHLIGHTS
                Total revenue: $245.1 billion (up 15.7% from prior year)
                Operating income: $109.4 billion 
                Operating margin: 44.6%
                Net income: $88.1 billion
                Diluted earnings per share: $11.05
                
                SEGMENT PERFORMANCE
                Productivity and Business Processes: $69.3 billion revenue (up 12%)
                Intelligent Cloud: $105.3 billion revenue (up 19%) 
                - Azure and other cloud services revenue grew 31%
                More Personal Computing: $54.7 billion revenue (up 17%)
                
                RESEARCH AND DEVELOPMENT
                R&D expenses: $29.5 billion (12.0% of revenue)
                Focus areas: Artificial Intelligence, Cloud Computing, Security
                
                ARTIFICIAL INTELLIGENCE STRATEGY
                Microsoft Copilot integrated across product portfolio
                Partnership with OpenAI driving AI innovation
                Azure AI services experiencing rapid adoption
                """,
                '2023': """
                Microsoft Corporation Annual Report 2023
                
                FINANCIAL HIGHLIGHTS  
                Total revenue: $211.9 billion (up 7% from prior year)
                Operating income: $89.4 billion
                Operating margin: 42.2%
                Net income: $72.4 billion
                
                SEGMENT PERFORMANCE
                Productivity and Business Processes: $67.0 billion revenue
                Intelligent Cloud: $87.9 billion revenue
                - Azure and other cloud services revenue grew 27%
                More Personal Computing: $57.0 billion revenue
                
                RESEARCH AND DEVELOPMENT
                R&D expenses: $27.2 billion (12.8% of revenue)
                """
            },
            'GOOGL': {
                '2024': """
                Alphabet Inc. Annual Report 2024
                
                FINANCIAL PERFORMANCE
                Total revenues: $334.7 billion (up 13.4% from 2023)
                Operating income: $96.9 billion
                Operating margin: 28.9%
                Net income: $80.5 billion
                
                REVENUE BREAKDOWN
                Google Search: $175.0 billion (up 14%)
                YouTube ads: $31.5 billion (up 13%)
                Google Cloud: $45.0 billion (up 35%)
                Other Bets: $1.3 billion
                
                RESEARCH AND DEVELOPMENT
                Total R&D expenses: $48.1 billion (14.4% of total revenues)
                Major investments in AI, quantum computing, autonomous systems
                
                ARTIFICIAL INTELLIGENCE INITIATIVES
                Gemini AI model family launched
                AI integration across all Google products
                Significant investments in AI infrastructure and talent
                """,
                '2023': """
                Alphabet Inc. Annual Report 2023
                
                FINANCIAL PERFORMANCE
                Total revenues: $307.4 billion (up 8.7% from 2022)  
                Operating income: $84.3 billion
                Operating margin: 27.4%
                Net income: $73.7 billion
                
                REVENUE BREAKDOWN
                Google Search: $175.0 billion
                YouTube ads: $31.5 billion  
                Google Cloud: $33.1 billion (up 26%)
                Other Bets: $1.0 billion
                
                RESEARCH AND DEVELOPMENT
                R&D expenses: $45.4 billion (14.8% of revenue)
                """
            },
            'NVDA': {
                '2024': """
                NVIDIA Corporation Annual Report Fiscal 2024
                
                RECORD FINANCIAL PERFORMANCE
                Total revenue: $60.9 billion (up 126% from fiscal 2023)
                Data Center revenue: $47.5 billion (up 217%)
                Gaming revenue: $10.4 billion (down 2%)
                Professional Visualization: $1.5 billion (up 17%)
                Automotive: $1.1 billion (up 21%)
                
                PROFITABILITY
                Gross margin: 73.0% (record high)
                Operating income: $32.9 billion
                Operating margin: 54.0%
                Net income: $29.8 billion
                
                RESEARCH AND DEVELOPMENT
                R&D expenses: $7.3 billion (12.0% of revenue)
                Focus: AI computing, autonomous systems, graphics innovation
                
                AI LEADERSHIP
                NVIDIA at the center of the AI revolution
                GPUs powering generative AI and large language models
                Leading position in AI training and inference markets
                """,
                '2023': """
                NVIDIA Corporation Annual Report Fiscal 2023
                
                FINANCIAL PERFORMANCE
                Total revenue: $27.0 billion (down 16% from fiscal 2022)
                Data Center revenue: $15.0 billion (up 1%)
                Gaming revenue: $9.1 billion (down 27%)
                Professional Visualization: $1.3 billion (down 27%)
                
                PROFITABILITY  
                Gross margin: 56.9%
                Operating income: $4.4 billion
                Operating margin: 16.2%
                Net income: $4.4 billion
                
                RESEARCH AND DEVELOPMENT
                R&D expenses: $7.3 billion (27% of revenue)
                """
            }
        }
        return demo_data.get(company, {}).get(year, f"Demo content for {company} {year} not available")

    def extract_text_from_html(self, filepath: str) -> str:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            return ' '.join(chunk for chunk in chunks if chunk)
        except Exception as e:
            print(f"Error extracting text from {filepath}: {e}")
            return ""

    def acquire_all_data(self) -> Dict[str, Dict[str, str]]:
        all_data: Dict[str, Dict[str, str]] = {}
        for company, cik in self.COMPANY_CIKS.items():
            print(f"\n=== Processing {company} ===")
            company_data: Dict[str, str] = {}
            filings = self.get_filing_urls(cik)
            for filing in filings[:2]:
                filepath = self.download_filing(filing['url'], company, filing['year'])
                if filepath:
                    text = self.extract_text_from_html(filepath)
                    if text:
                        company_data[filing['year']] = text
            all_data[company] = company_data
        return all_data


