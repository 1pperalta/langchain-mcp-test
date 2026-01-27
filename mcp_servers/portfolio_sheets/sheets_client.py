"""Google Sheets API client for portfolio data."""
import os
from pathlib import Path
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from models.portfolio import Position, Portfolio


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
TOKEN_PATH = Path(__file__).parent.parent.parent / 'token.json'


class SheetsClient:
    """Client for reading portfolio data from Google Sheets."""
    
    def __init__(self, sheet_id: str | None = None):
        """
        Initialize Google Sheets client.
        
        Args:
            sheet_id: Google Sheet ID. If None, reads from PORTFOLIO_SHEET_ID env var.
        """
        self.sheet_id = sheet_id or os.getenv('PORTFOLIO_SHEET_ID')
        if not self.sheet_id:
            raise ValueError(
                "Sheet ID must be provided or set in PORTFOLIO_SHEET_ID environment variable"
            )
        
        self._service = None
    
    def _get_credentials(self) -> Credentials:
        """Get or refresh Google OAuth credentials."""
        creds = None
        
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                client_id = os.getenv('GOOGLE_CLIENT_ID')
                client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
                
                if not client_id or not client_secret:
                    raise ValueError(
                        "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in environment"
                    )
                
                client_config = {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost"]
                    }
                }
                
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                creds = flow.run_local_server(port=0)
            
            TOKEN_PATH.write_text(creds.to_json())
        
        return creds
    
    @property
    def service(self):
        """Get authenticated Google Sheets service."""
        if self._service is None:
            creds = self._get_credentials()
            self._service = build('sheets', 'v4', credentials=creds)
        return self._service
    
    def read_sheet_values(self, range_name: str = 'Positions!A:G') -> list[list]:
        """
        Read raw values from Google Sheet.
        
        Args:
            range_name: Sheet range to read (default: 'Positions!A:G')
        
        Returns:
            List of rows with values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
        
        except HttpError as error:
            raise RuntimeError(f"Failed to read from Google Sheets: {error}")
    
    def _parse_colombian_number(self, value_str: str) -> float:
        """Parse Colombian number format with comma thousand separators."""
        cleaned = value_str.replace(',', '').strip()
        return float(cleaned)
    
    def read_positions(self) -> list[Position]:
        """
        Read positions from Google Sheets and convert to Position objects.
        
        Expected columns: Activo | Plataforma | Moneda | Valor Original
        (A: Asset, B: Platform, C: Currency, D: Original Value)
        
        Returns:
            List of Position objects
        """
        values = self.read_sheet_values()
        
        if not values:
            return []
        
        header = values[0]
        rows = values[1:]
        
        positions = []
        for i, row in enumerate(rows, start=2):
            if len(row) < 4:
                continue
            
            activo = row[0].strip() if row[0] else ""
            plataforma = row[1].strip() if len(row) > 1 and row[1] else ""
            moneda = row[2].strip().upper() if len(row) > 2 and row[2] else ""
            valor_str = row[3].strip() if len(row) > 3 and row[3] else ""
            
            if not activo or not plataforma or not moneda or not valor_str:
                continue
            
            if activo.upper() == "TOTAL PATRIMONIO":
                continue
            
            try:
                valor = self._parse_colombian_number(valor_str)
                
                position = Position(
                    symbol=activo,
                    platform=plataforma,
                    currency=moneda,
                    value=valor,
                    asset_type="fund"
                )
                positions.append(position)
            
            except (ValueError, IndexError) as e:
                print(f"Warning: Skipping row {i} ({activo}): {e}")
                continue
        
        return positions
    
    def read_portfolio(self) -> Portfolio:
        """
        Read all positions and create Portfolio object.
        
        Returns:
            Portfolio object with all positions
        """
        positions = self.read_positions()
        return Portfolio(positions=positions)
