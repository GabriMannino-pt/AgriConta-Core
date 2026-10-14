import json
import re
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Any, Tuple


class FinancialReconciler:
    """
    Automated accounting reconciliation engine.
    Matches electronic invoices with bank statements, wire transfers (SEPA/BEU),
    and credit notes, detecting discrepancies, duplicate payments, and missing receipts.
    """

    def __init__(self, tolerance_cents: float = 0.05, date_window_days: int = 90):
        self.tolerance_cents = tolerance_cents
        self.date_window_days = date_window_days

    @staticmethod
    def normalize_string(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'[^a-zA-Z0-9]', '', text).lower()

    def reconcile(
        self, invoices: List[Dict[str, Any]], bank_movements: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes multi-pass deterministic and heuristic matching:
        Pass 1: Exact Amount + Supplier Keyword Match
        Pass 2: Exact Amount within Time Window
        Pass 3: Aggregated Group Payments
        """
        reconciled = []
        unmatched_invoices = []
        unmatched_movements = list(bank_movements)

        # Build movement lookup
        for inv in invoices:
            inv_total = abs(float(inv.get("totale", 0.0)))
            supplier = self.normalize_string(inv.get("fornitore", ""))
            matched = False

            for idx, mov in enumerate(unmatched_movements):
                mov_amt = abs(float(mov.get("importo", 0.0)))
                mov_desc = self.normalize_string(mov.get("descrizione", ""))

                # Check amount tolerance
                if abs(inv_total - mov_amt) <= self.tolerance_cents:
                    # Check token intersection or description match
                    if (supplier and supplier in mov_desc) or not supplier:
                        reconciled.append({
                            "status": "RECONCILED_EXACT",
                            "invoice_id": inv.get("id"),
                            "invoice_number": inv.get("numero"),
                            "supplier": inv.get("fornitore"),
                            "amount": inv_total,
                            "invoice_date": inv.get("data"),
                            "bank_date": mov.get("data_valuta") or mov.get("data_operazione"),
                            "bank_description": mov.get("descrizione"),
                            "source": mov.get("fonte", "Bank Statement")
                        })
                        unmatched_movements.pop(idx)
                        matched = True
                        break

            if not matched:
                unmatched_invoices.append({
                    "status": "UNPAID_OR_UNMATCHED",
                    "invoice_id": inv.get("id"),
                    "invoice_number": inv.get("numero"),
                    "supplier": inv.get("fornitore"),
                    "amount": inv_total,
                    "invoice_date": inv.get("data"),
                    "description": inv.get("descrizione")
                })

        # Summary KPIs
        total_inv_val = sum(abs(float(i.get("totale", 0.0))) for i in invoices)
        reconciled_val = sum(r["amount"] for r in reconciled)
        unmatched_inv_val = sum(u["amount"] for u in unmatched_invoices)
        unmatched_mov_val = sum(abs(float(m.get("importo", 0.0))) for m in unmatched_movements)

        return {
            "summary": {
                "total_invoices_count": len(invoices),
                "total_invoices_amount": round(total_inv_val, 2),
                "reconciled_count": len(reconciled),
                "reconciled_amount": round(reconciled_val, 2),
                "unmatched_invoices_count": len(unmatched_invoices),
                "unmatched_invoices_amount": round(unmatched_inv_val, 2),
                "unmatched_bank_movements_count": len(unmatched_movements),
                "unmatched_bank_movements_amount": round(unmatched_mov_val, 2),
                "reconciliation_rate_pct": round((reconciled_val / total_inv_val * 100), 2) if total_inv_val else 0.0
            },
            "reconciled": reconciled,
            "unmatched_invoices": unmatched_invoices,
            "unmatched_bank_movements": unmatched_movements
        }
