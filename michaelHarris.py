import numpy as np
import pandas as pd
from LocalRecord import LocalRecord
from copy import copy

class MichaelHarris:
    def __init__(self, lookback: int, take_profit: float, stop_loss: float):
        self._clb = lookback
        self._tp = take_profit
        self._sl = stop_loss
        self._pending_record = None
        self.trading_records = []

    def _create_entries(self, entry_i: int, time_index: pd.DatetimeIndex, open: np.ndarray):
        new_record = LocalRecord(entry_index=entry_i, entry_price=open[entry_i], entry_timestamp=time_index[entry_i], exit_index=-1, exit_price=np.nan, exit_timestamp=time_index[entry_i], percentage_change=np.nan)
        self._pending_record = new_record
    
    def _create_exites(self, exit_i: int, time_index: pd.DatetimeIndex, exit_price: float):
        self._pending_record.exit_index = exit_i
        self._pending_record.exit_timestamp = time_index[exit_i]
        self._pending_record.exit_price = exit_price
        self._pending_record.percentage_change = (self._pending_record.exit_price - self._pending_record.entry_price) / self._pending_record.entry_price * 100
        self.trading_records.append(copy(self._pending_record))
        self._pending_record = None

    def update(self, i: int, time_index: pd.DatetimeIndex, open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
        if i < self._clb:
            return
        else:                
            if self._pending_record == None:
                # Buy condition
                for j in range(1, self._clb):
                    if high[i-j] <= high[i-j-1]:
                        return
                    if low[i-j] >= high[i-j-1]:
                        return
                    if low[i-j] <= low[i-j-1]:
                        return

                self._create_entries(i, time_index, open)
            else:
                # Stop Loss
                sl_price = self._pending_record.entry_price * (1 - self._sl)
                tp_price = self._pending_record.entry_price * (1 + self._tp)
                if low[i] <= sl_price:
                    self._create_exites(i, time_index, sl_price)
                # Take Profit
                elif high[i] >= tp_price:
                    self._create_exites(i, time_index, tp_price)