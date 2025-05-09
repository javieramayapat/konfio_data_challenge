import logging

import requests
from pyspark.sql import SparkSession

from extractor.base.extractor import Extractor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class CoinGeckoAPI(Extractor):
    """
    Extractor implementation for CoinGecko API.
    Provides methods to fetch coin list, coin details, and market data.
    """

    def __init__(
        self, spark_session: SparkSession, api_key: str, base_url: str
    ) -> None:
        """
        Initialize CoinGeckoAPI extractor.

        Args:
            spark_session: SparkSession instance.
            api_key: API key for CoinGecko demo access.
            base_url: Base URL for CoinGecko API.
        """
        self.spark_session = spark_session
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self._coins_list = None

    def parameter_validation(self) -> bool:
        """
        Validate initialization parameters.

        Returns:
            True if parameters are valid, False otherwise.
        """
        if not isinstance(self.spark_session, SparkSession):
            logger.error('spark_session must be a SparkSession instance.')
            return False
        if not isinstance(self.api_key, str) or not self.api_key:
            logger.error('api_key must be a non-empty string.')
            return False
        if not isinstance(self.base_url, str) or not self.base_url:
            logger.error('base_url must be a non-empty string.')
            return False
        return True

    @property
    def _headers(self) -> dict:
        """
        Request headers for CoinGecko API calls.
        """
        return {'Accept': 'application/json', 'x-cg-demo-api-key': self.api_key}

    def _validate_coin_id(self, coin_id: str) -> bool:
        """
        Ensure coin_id is a non-empty string.

        Args:
            coin_id: Coin identifier.

        Returns:
            True if valid, False otherwise.
        """
        if not isinstance(coin_id, str):
            logger.error('Coin ID must be a string.')
            return False
        if not coin_id.strip():
            logger.error('Coin ID cannot be empty.')
            return False
        return True

    def _make_request(self, endpoint: str, params: dict = None) -> dict | None:
        """
        Internal helper to perform GET requests.

        Args:
            endpoint: Full URL to GET.
            params: Query parameters.

        Returns:
            Parsed JSON response or None on failure.
        """
        try:
            response = requests.get(endpoint, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f'Request failed: {e}')
            return None

    @property
    def coins_list(self) -> list[dict]:
        """
        Lazy-loaded list of all coins from CoinGecko.

        Returns:
            List of coin metadata dictionaries.
        """
        if self._coins_list is None:
            self._coins_list = self.get_coin_list()
        return self._coins_list

    def get_coin_list(self) -> list[dict]:
        """
        Fetch list of all coins (id, symbol, name).

        Returns:
            List of coins or empty list on failure.
        """
        endpoint = f'{self.base_url}/coins/list'
        data = self._make_request(endpoint)
        return data if isinstance(data, list) else []

    def find_coin_by_id(self, coin_id: str) -> dict | None:
        """
        Find a coin in the cached coins_list by its ID.

        Args:
            coin_id: Coin identifier.

        Returns:
            Coin dict if found, else None.
        """
        if not self._validate_coin_id(coin_id):
            return None
        for coin in self.coins_list:
            if coin.get('id') == coin_id:
                return coin
        logger.warning(f"Coin with ID '{coin_id}' not found.")
        return None

    def get_coin_data_by_id(self, coin_id: str) -> dict | None:
        """
        Fetch detailed data for a coin by its ID.

        Args:
            coin_id: Coin identifier.

        Returns:
            Coin detail dict or None.
        """
        if not self._validate_coin_id(coin_id):
            return None
        endpoint = f'{self.base_url}/coins/{coin_id}'
        return self._make_request(endpoint)

    def extract_data_from_source(
        self, coin_id: str, currency_code: str, start_timestamp: int, end_timestamp: int
    ) -> dict | None:
        """
        Extract market data for a given coin and time range.

        Args:
            coin_id: Cryptocurrency ID.
            currency_code: Currency to convert (e.g., 'usd').
            start_timestamp: UNIX timestamp (seconds) start.
            end_timestamp: UNIX timestamp (seconds) end.

        Returns:
            Dict with 'coin_info' and 'market_data', or None on failure.
        """
        if not self.parameter_validation():
            return None
        coin_info = self.find_coin_by_id(coin_id)
        if not coin_info:
            return None
        endpoint = f'{self.base_url}/coins/{coin_id}/market_chart/range'
        params = {
            'vs_currency': currency_code,
            'from': start_timestamp,
            'to': end_timestamp,
        }
        market_data = self._make_request(endpoint, params)
        if not market_data:
            logger.error(f'Failed to fetch market data for {coin_id}')
            return None
        return {'coin_info': coin_info, 'market_data': market_data.get('prices', [])}
