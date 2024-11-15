import logging
import os
from rope.config import CONFIG

class PaymentAPI:
    def __init__(self):
        # 不要硬编码购买链接
        self.purchase_url = os.getenv('LEMONSQUEEZY_PURCHASE_URL') or CONFIG.get('purchase_url')

    def create_order(self, order_data):
        try:
            return {'pay_url': self.purchase_url}
        except Exception as e:
            logging.error(f"Create order error: {str(e)}")
            raise