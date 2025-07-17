
# import ssl
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode

from config import DHAKA_STOCK_URLS

class Quote:
    def __init__(self, symbol: str = "", ltp: str = "", high: str = "", 
                 low: str = "", close: str = "", ycp: str = "", 
                 change: str = "", trade: str = "", value: str = "", 
                 volume: str = ""):
        self.symbol = symbol
        self.ltp = ltp
        self.high = high
        self.low = low
        self.close = close
        self.ycp = ycp
        self.change = change
        self.trade = trade
        self.value = value
        self.volume = volume

class HistData:
    def __init__(self, number: str = "", date: str = "", trading_code: str = "",
                 ltp: str = "", high: str = "", low: str = "", openp: str = "",
                 closep: str = "", ycp: str = "", trade: str = "",
                 value: str = "", volume: str = ""):
        self.number = number
        self.date = date
        self.trading_code = trading_code
        self.ltp = ltp
        self.high = high
        self.low = low
        self.openp = openp
        self.closep = closep
        self.ycp = ycp
        self.trade = trade
        self.value = value
        self.volume = volume

class StockDataService:
    """Service class for fetching and parsing stock data"""
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with retry configuration"""
        if self.session is None or self.session.closed:
            # ssl_context = ssl.create_default_context(cafile=certifi.where())
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, ssl=False)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
        return self.session
    
    async def _fetch_with_retry(self, url: str, params: Dict = None, max_retries: int = 3) -> str:
        session = await self._get_session()
        
        for attempt in range(max_retries):
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        raise aiohttp.ClientError(f"HTTP {response.status}")
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff
                await asyncio.sleep(wait_time)
        
        raise Exception(f"Failed to fetch {url}")
    
    async def _fetch_and_parse_html(self, url: str, params: Dict = None) -> BeautifulSoup:
        """Fetch URL and return BeautifulSoup object"""
        try:
            html_content = await self._fetch_with_retry(url, params)
            return BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            print(f"Error in _fetch_and_parse_html for {url}: {e}")
            raise
    
    def _get_current_trading_codes(self, soup: BeautifulSoup) -> List[str]:
        """Extract table headers from the first row"""
        headers = []
        table = soup.select_one('table.shares-table')
        if table:
            first_row = table.find('tr')
            if first_row:
                ths = first_row.find_all('th')
                headers = [th.get_text(strip=True) for th in ths]
        return headers
    

    async def _parse_table_rows(self, soup: BeautifulSoup, selector: str = "table.table-bordered tr", 
                               skip_first_row: bool = True) -> List[Dict[str, Any]]:
        """Parse table rows and return list of dictionaries"""
        headers = self._get_current_trading_codes(soup)
        data = []
        
        rows = soup.select(selector)
        
        for index, row in enumerate(rows):
            if index == 0 and skip_first_row:
                continue
            
            tds = row.find_all('td')
            if len(tds) == 0:
                continue
                
            row_data = {}
            
            for idx, header in enumerate(headers):
                if idx < len(tds):
                    cell_text = tds[idx].get_text(strip=True).replace(',', '')
                    row_data[header] = cell_text
                else:
                    row_data[header] = ""
            
            if row_data:  # Only add non-empty rows
                data.append(row_data)
        
        return data
    
    async def get_stock_data(self) -> List[Dict[str, Any]]:
        """Get latest stock data"""
        url = DHAKA_STOCK_URLS["LATEST_DATA"]
        soup = await self._fetch_and_parse_html(url)
        return await self._parse_table_rows(soup, "table.table-bordered tr")
    
    async def get_dsex_data(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get DSEX data with optional symbol filter"""
        url = DHAKA_STOCK_URLS["DSEX"]
        
        try:
            soup = await self._fetch_and_parse_html(url)
            data = await self._parse_table_rows(soup, "table.table-bordered tr")
            
            if symbol:
                # Filter by trading code (case-insensitive)
                filtered_data = []
                for item in data:
                    trading_code = item.get('TRADING CODE', '')
                    if trading_code and trading_code.upper() == symbol.upper():
                        filtered_data.append(item)
                return filtered_data
            
            return data
            
        except Exception as e:
            print(f"Error fetching DSEX data: {e}")
            return []
    
    async def get_top30(self) -> List[Dict[str, Any]]:
        """Get top 30 stocks data"""
        url = DHAKA_STOCK_URLS["TOP_30"]
        print(f"Fetching Top 30 data from {url}")
        
        try:
            soup = await self._fetch_and_parse_html(url)
            return await self._parse_table_rows(soup, "table.table-bordered tr")
            
        except Exception as e:
            print(f"Error fetching Top 30 data: {e}")
            return []
    
    async def get_historical_data(self, start: str, end: str, code: str = "All Instrument") -> List[Dict[str, Any]]:
        """Get historical stock data"""
        url = DHAKA_STOCK_URLS["HISTORICAL_DATA"]
        params = {
            'startDate': start,
            'endDate': end,
            'inst': code,
            'archive': 'data'
        }
        
        # Build full URL with parameters
        full_url = f"{url}?{urlencode(params)}"
        
        soup = await self._fetch_and_parse_html(full_url)
        return await self._parse_table_rows(soup, "table.table-bordered tbody tr", skip_first_row=False)
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.session.close())