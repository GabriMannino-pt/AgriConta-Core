import re
from typing import Dict, Any, Optional


class EnergyUtilityParser:
    """
    Parses and audits industrial/agricultural electricity bills (POD, F1/F2/F3 tariffs,
    reactive power penalties, power demand in kW).
    """

    @staticmethod
    def parse_energy_metrics(bill_text: str) -> Dict[str, Any]:
        metrics = {
            "pod": None,
            "total_kwh": 0.0,
            "f1_kwh": 0.0,
            "f2_kwh": 0.0,
            "f3_kwh": 0.0,
            "peak_power_kw": 0.0,
            "total_amount_eur": 0.0
        }

        # POD extraction (IT001E...)
        pod_match = re.search(r'\b(IT\d{3}E[A-Z0-9]{8,14})\b', bill_text)
        if pod_match:
            metrics["pod"] = pod_match.group(1)

        # Total kWh
        kwh_match = re.search(r'(?:energia\s+attiva|totale\s+consumi|consumo\s+totale)[\s:]*([0-9.,]+)\s*kWh', bill_text, re.IGNORECASE)
        if kwh_match:
            try:
                metrics["total_kwh"] = float(kwh_match.group(1).replace(".", "").replace(",", "."))
            except ValueError:
                pass

        # Total Amount
        tot_match = re.search(r'(?:totale\s+(?:fattura|da\s+pagare)|importo\s+totale)[\s:€]*([0-9.,]+)', bill_text, re.IGNORECASE)
        if tot_match:
            try:
                metrics["total_amount_eur"] = float(tot_match.group(1).replace(".", "").replace(",", "."))
            except ValueError:
                pass

        return metrics
