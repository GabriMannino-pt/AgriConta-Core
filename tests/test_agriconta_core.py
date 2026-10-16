import unittest
from agriconta.reconciler import FinancialReconciler
from agriconta.energy_parser import EnergyUtilityParser
from agriconta.managerial_analyzer import ManagerialCostAnalyzer


class TestAgriContaCore(unittest.TestCase):

    def test_exact_invoice_reconciliation(self):
        reconciler = FinancialReconciler(tolerance_cents=0.05)
        invoices = [
            {"id": "INV-01", "numero": "2026/001", "fornitore": "AgriSeeds Srl", "totale": 1250.50, "data": "2026-01-10"},
            {"id": "INV-02", "numero": "2026/002", "fornitore": "Irrigazione Sud", "totale": 840.00, "data": "2026-01-15"},
        ]
        bank_movements = [
            {"importo": -1250.50, "descrizione": "BONIFICO SEPA FAVORE AGRISEEDS SRL FATT 2026/001", "data_valuta": "2026-01-12"},
        ]
        res = reconciler.reconcile(invoices, bank_movements)
        self.assertEqual(res["summary"]["reconciled_count"], 1)
        self.assertEqual(res["summary"]["unmatched_invoices_count"], 1)
        self.assertAlmostEqual(res["summary"]["reconciled_amount"], 1250.50, places=2)

    def test_reconciler_tolerance_cents(self):
        reconciler = FinancialReconciler(tolerance_cents=0.05)
        invoices = [{"id": "INV-03", "numero": "10", "fornitore": "Enel Energia", "totale": 500.00, "data": "2026-02-01"}]
        bank_movements = [{"importo": -500.03, "descrizione": "SDD ENEL ENERGIA SPA", "data_valuta": "2026-02-02"}]
        res = reconciler.reconcile(invoices, bank_movements)
        self.assertEqual(res["summary"]["reconciled_count"], 1)

    def test_normalize_string(self):
        self.assertEqual(FinancialReconciler.normalize_string("Enel Energia S.p.A. - #123"), "enelenergiaspa123")
        self.assertEqual(FinancialReconciler.normalize_string(""), "")

    def test_energy_utility_parser_pod_and_kwh(self):
        sample_bill = (
            "Fornitura Elettrica Agricola - Codice POD: IT001E98765432A "
            "Consumo Totale: 14.320,50 kWh - Totale da pagare: € 3.410,25"
        )
        metrics = EnergyUtilityParser.parse_energy_metrics(sample_bill)
        self.assertEqual(metrics["pod"], "IT001E98765432A")
        self.assertAlmostEqual(metrics["total_kwh"], 14320.50, places=2)
        self.assertAlmostEqual(metrics["total_amount_eur"], 3410.25, places=2)

    def test_energy_utility_parser_empty_input(self):
        metrics = EnergyUtilityParser.parse_energy_metrics("Documento generico senza metriche")
        self.assertIsNone(metrics["pod"])
        self.assertEqual(metrics["total_kwh"], 0.0)
        self.assertEqual(metrics["total_amount_eur"], 0.0)

    def test_managerial_cost_categorization(self):
        analyzer = ManagerialCostAnalyzer()
        self.assertEqual(
            analyzer.categorize_invoice({"fornitore": "Consorzio Agrario", "descrizione": "Fornitura concime NPK"}),
            "crop_inputs",
        )
        self.assertEqual(
            analyzer.categorize_invoice({"fornitore": "Petroli Siciliani", "descrizione": "Gasolio agricolo UMA"}),
            "agricultural_fuel",
        )
        self.assertEqual(
            analyzer.categorize_invoice({"fornitore": "Studio Associato", "descrizione": "Consulenza agronomo"}),
            "advisory_and_compliance",
        )

    def test_managerial_cost_annual_aggregation(self):
        analyzer = ManagerialCostAnalyzer()
        invoices = [
            {"fornitore": "Enel", "descrizione": "Energia elettrica kWh", "totale": 600.0, "data": "2025-05-10"},
            {"fornitore": "Agrimec", "descrizione": "Riparazione trattore", "totale": 400.0, "data": "2025-06-12"},
        ]
        report = analyzer.analyze(invoices)
        self.assertAlmostEqual(report["total_expenditure"], 1000.0, places=2)
        self.assertAlmostEqual(report["category_distribution"]["energy_and_utilities"]["percentage"], 60.0, places=2)
        self.assertAlmostEqual(report["category_distribution"]["machinery_maintenance"]["percentage"], 40.0, places=2)


if __name__ == "__main__":
    unittest.main()
