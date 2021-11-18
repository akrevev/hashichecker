
from lib.helpers import Helpers
import json
import logging
import os

logger = logging.getLogger('ipochecker')

## class with instance variables
class IPODetails:
  def __init__(self):
    self.asset_class = None
    self.compliance_status = None
    self.deal_status = None
    self.delta_indicator = None
    self.dollar_value_of_shares_offered = None
    self.exchange = None
    self.is_held = None
    self.is_nasdaq_listed = None
    self.last_sale_price = None
    self.lockup_period_expiration_date = None
    self.market_status = None
    self.net_change = None
    self.overview_status = None
    self.percentage_change = None
    self.proposed_share_price = None
    self.quiet_period_expiration_date = None
    self.quote_status = None
    self.secondary_data = None
    self.shareholder_shares_offered = None
    self.shares_offered = None
    self.shares_outstanding = None
    self.shares_over_allotment = None
    self.stock_type = None
    self.trading_held = None

  def from_cache(self):
    data = Helpers.load_previous_details()
    if data != {}:
      self.asset_class = data['asset_class']
      self.compliance_status = data['compliance_status']
      self.deal_status = data['deal_status']
      self.delta_indicator = data['delta_indicator']
      self.dollar_value_of_shares_offered = data['dollar_value_of_shares_offered']
      self.exchange = data['exchange']
      self.is_held = data['is_held']
      self.is_nasdaq_listed = data['is_nasdaq_listed']
      self.last_sale_price = data['last_sale_price']
      self.lockup_period_expiration_date = data['lockup_period_expiration_date']
      self.market_status = data['market_status']
      self.net_change = data['net_change']
      self.overview_status = data['overview_status']
      self.percentage_change = data['percentage_change']
      self.proposed_share_price = data['proposed_share_price']
      self.quiet_period_expiration_date = data['quiet_period_expiration_date']
      self.quote_status = data['quote_status']
      self.secondary_data = data['secondary_data']
      self.shareholder_shares_offered = data['shareholder_shares_offered']
      self.shares_offered = data['shares_offered']
      self.shares_outstanding = data['shares_outstanding']
      self.shares_over_allotment = data['shares_over_allotment']
      self.stock_type = data['stock_type']
      self.trading_held = data['trading_held']
    return self

  def from_api(self):
    quote_response = Helpers.load_json("https://api.nasdaq.com/api/quote/HCP/info?assetclass=ipo")
    overview_response = Helpers.load_json("https://api.nasdaq.com/api/ipo/overview/?dealId=1035813-101007")

    self.quote_status = quote_response["status"]["rCode"]
    self.overview_status = overview_response["status"]["rCode"]

    quote = quote_response["data"]
    primaryData = quote["primaryData"]
    overview = overview_response["data"]
    poOverview = overview["poOverview"]

    # start setting up properties
    self.asset_class = quote["assetClass"]
    self.compliance_status = quote["complianceStatus"]
    self.deal_status = poOverview["DealStatus"]["value"]
    self.delta_indicator = primaryData["deltaIndicator"]
    self.dollar_value_of_shares_offered = poOverview["DollarValueOfSharesOffered"]["value"]
    self.exchange = quote["exchange"]
    # self.http_status
    self.is_held = quote["isHeld"]
    self.is_nasdaq_listed = quote["isNasdaqListed"]
    self.last_sale_price = primaryData["lastSalePrice"]
    self.lockup_period_expiration_date = poOverview["LockupPeriodExpirationDate"]["value"]
    self.market_status = quote["marketStatus"]
    self.net_change = primaryData["netChange"]
    self.percentage_change = primaryData["percentageChange"]
    self.proposed_share_price = poOverview["ProposedSharePrice"]["value"]
    self.quiet_period_expiration_date = poOverview["QuietPeriodExpirationDate"]["value"]
    self.secondary_data = quote["secondaryData"]
    self.shareholder_shares_offered = poOverview["ShareholderSharesOffered"]["value"]
    self.shares_offered = poOverview["SharesOffered"]["value"]
    self.shares_outstanding = poOverview["SharesOutstanding"]["value"]
    self.shares_over_allotment = poOverview["SharesOverAllotment"]["value"]
    self.stock_type = quote["stockType"]
    self.trading_held = quote["tradingHeld"]
    return self

  def diff(self, other):
    diff = {}
    for key in self.__dict__:
      if self.__dict__[key] != other.__dict__[key]:
        # logging.debug("Details have changed", extra={'old': self.__dict__[key], 'new': other.__dict__[key]})
        diff[key] = {
          "old": self.__dict__[key],
          "new": other.__dict__[key]
        }
    return diff

  def to_json(self):
    return json.dumps(self, default=lambda o: o.__dict__,
        sort_keys=True, indent=4)