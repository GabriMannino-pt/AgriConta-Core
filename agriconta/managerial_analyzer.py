from collections import defaultdict
from typing import List, Dict, Any


class ManagerialCostAnalyzer:
    """
    Managerial cost accounting & financial analytics for enterprise agricultural operations.
    Classifies OPEX, CAPEX, fixed overheads, and variable crop production costs.
    """

    CATEGORIES = {
        "crop_inputs": ["fertilizzante", "concime", "fitofarmaco", "agrofarmaco", "sementi", "piante"],
        "agricultural_fuel": ["gasolio", "uma", "carburante", "diesel"],
        "energy_and_utilities": ["energia", "enel", "iren", "luce", "elettricita", "kwh", "servizio elettrico"],
        "machinery_maintenance": ["trattore", "riparazione", "officina", "ricambi", "pompa", "irrigazione"],
        "capex_and_leasing": ["mutuo", "leasing", "finanziamento", "impianto fotovoltaico", "macchinari"],
        "advisory_and_compliance": ["consulenza", "agronomo", "commercialista", "certificazione", "sicurezza"]
    }

    def categorize_invoice(self, invoice: Dict[str, Any]) -> str:
        text = f"{invoice.get('fornitore', '')} {invoice.get('descrizione', '')}".lower()
        for cat, keywords in self.CATEGORIES.items():
            if any(kw in text for kw in keywords):
                return cat
        return "general_overheads"

    def analyze(self, invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        breakdown_by_year = defaultdict(lambda: defaultdict(float))
        total_by_category = defaultdict(float)
        total_expenditure = 0.0

        for inv in invoices:
            amt = abs(float(inv.get("totale", 0.0)))
            year = str(inv.get("anno", inv.get("data", "Unknown")[:4]))
            cat = self.categorize_invoice(inv)

            breakdown_by_year[year][cat] += amt
            total_by_category[cat] += amt
            total_expenditure += amt

        # Calculate percentages
        category_distribution = {}
        for cat, val in total_by_category.items():
            category_distribution[cat] = {
                "amount": round(val, 2),
                "percentage": round((val / total_expenditure * 100), 2) if total_expenditure else 0.0
            }

        return {
            "total_expenditure": round(total_expenditure, 2),
            "category_distribution": category_distribution,
            "annual_trends": {y: dict(cats) for y, cats in breakdown_by_year.items()}
        }
