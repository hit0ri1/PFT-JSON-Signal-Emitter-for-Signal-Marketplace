#!/usr/bin/env python3
"""
Post Fiat Signal Emitter for NAVCoin Venture Agent
Converts Sunday Scorecard evaluations into Post Fiat Signal Marketplace JSON
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class SignalEmitter:
    """Generate Post Fiat Signal Marketplace JSON payloads"""
    
    def __init__(self, agent_name: str = "NAVCoin Venture Agent",
                 agent_version: str = "1.0",
                 agent_address: str = "0xNAVCoinAgentAddress"):
        self.agent_name = agent_name
        self.agent_version = agent_version
        self.agent_address = agent_address
        self.signal_version = "1.0"
        self.threshold = 85.0
    
    def generate_signal_id(self, ticker: str, timestamp: str) -> str:
        """Generate unique signal ID"""
        date_str = timestamp.split("T")[0].replace("-", "")
        raw = f"NAV-{ticker}-{date_str}"
        hash_suffix = hashlib.md5(raw.encode()).hexdigest()[:3].upper()
        return f"{raw}-{hash_suffix}"
    
    def calculate_risk_reward(self, current: float, target: float,
                             stop_loss: float) -> float:
        """Calculate risk/reward ratio"""
        upside = target - current
        downside = current - stop_loss
        return round(upside / downside, 2) if downside > 0 else 0
    
    def determine_action(self, score: float) -> str:
        """Determine signal action based on score"""
        if score >= self.threshold:
            return "BUY"
        elif score >= 80:
            return "HOLD"
        else:
            return "WATCH"
    
    def determine_conviction(self, score: float) -> str:
        """Map score to conviction level"""
        if score >= 90:
            return "VERY_HIGH"
        elif score >= 85:
            return "HIGH"
        elif score >= 80:
            return "MEDIUM"
        else:
            return "LOW"
    
    def generate_signal(self,
                       # Asset data
                       ticker: str,
                       name: str,
                       category: str,
                       chain: str,
                       contract_address: str,
                       coingecko_id: str,
                       # Scoring data
                       final_score: float,
                       scoring_breakdown: Dict,
                       # Price data
                       current_price: float,
                       entry_low: float,
                       entry_high: float,
                       target_12m: float,
                       stop_loss: float,
                       # Risk data
                       risk_level: str,
                       key_risks: List[str],
                       # Optional
                       timestamp: Optional[str] = None) -> Dict:
        """Generate complete signal payload"""
        
        if timestamp is None:
            timestamp = datetime.utcnow().isoformat() + "Z"
        
        signal_id = self.generate_signal_id(ticker, timestamp)
        action = self.determine_action(final_score)
        conviction = self.determine_conviction(final_score)
        rr_ratio = self.calculate_risk_reward(current_price, target_12m, stop_loss)
        
        signal = {
            "signal_version": self.signal_version,
            "signal_id": signal_id,
            "timestamp": timestamp,
            "agent": {
                "name": self.agent_name,
                "version": self.agent_version,
                "methodology": "10-Criteria DePIN/AI Scorecard",
                "agent_address": self.agent_address
            },
            "asset": {
                "ticker": ticker,
                "name": name,
                "category": category,
                "chain": chain,
                "contract_address": contract_address,
                "coingecko_id": coingecko_id
            },
            "signal": {
                "action": action,
                "conviction": conviction,
                "score": final_score,
                "threshold": self.threshold,
                "confidence": round(final_score / 100, 2),
                "timeframe": "12_MONTHS",
                "position_size_recommendation": "5-10%" if action == "BUY" else "0%"
            },
            "price_data": {
                "current_price_usd": current_price,
                "entry_range_low": entry_low,
                "entry_range_high": entry_high,
                "target_price_12m": target_12m,
                "stop_loss": stop_loss,
                "risk_reward_ratio": rr_ratio
            },
            "scoring_breakdown": scoring_breakdown,
            "risk_assessment": {
                "overall_risk": risk_level,
                "key_risks": key_risks
            },
            "metadata": {
                "data_sources": [
                    "CoinGecko API", "DefiLlama", "GitHub API",
                    f"Sunday Scorecard {timestamp.split('T')[0]}"
                ],
                "last_updated": timestamp,
                "next_review": (datetime.fromisoformat(timestamp.replace('Z', ''))
                                + timedelta(days=7)).isoformat() + "Z",
                "signal_status": "ACTIVE" if action == "BUY" else "WATCH"
            }
        }
        
        return signal
    
    def emit_json(self, signal: Dict, filepath: str = None) -> str:
        """Export signal to JSON file or string"""
        json_str = json.dumps(signal, indent=2, ensure_ascii=False)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
            print(f"Signal written to {filepath}")
        
        return json_str


if __name__ == "__main__":
    print("Signal Emitter loaded successfully")
