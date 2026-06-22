# tools/risk_engine.py

class RiskEngine:

    def calculate_position(
        self,
        account_equity,
        risk_percent,
        entry_price,
        atr
    ):

        if atr <= 0:

            return {
                "position_size": 0,
                "risk_amount": 0,
                "stop_loss": None,
                "take_profit": None
            }

        risk_amount = (
            account_equity
            * (risk_percent / 100)
        )

        stop_distance = atr * 2

        position_size = (
            risk_amount
            / stop_distance
        )

        stop_loss = (
            entry_price
            - stop_distance
        )

        take_profit = (
            entry_price
            + (stop_distance * 3)
        )

        return {
            "position_size": round(
                position_size,
                4
            ),
            "risk_amount": round(
                risk_amount,
                2
            ),
            "stop_loss": round(
                stop_loss,
                2
            ),
            "take_profit": round(
                take_profit,
                2
            ),
            "risk_reward": "1:3"
        }


risk_engine = RiskEngine()