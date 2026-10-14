import argparse
import json
import os
import sys
from agriconta.reconciler import FinancialReconciler
from agriconta.managerial_analyzer import ManagerialCostAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="AgriConta Core: Financial Reconciliation & Managerial Cost Accounting Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: reconcile
    rec_parser = subparsers.add_parser("reconcile", help="Reconcile invoices against bank statements")
    rec_parser.add_argument("--invoices", required=True, help="Path to invoices JSON")
    rec_parser.add_argument("--bank", required=True, help="Path to bank statements JSON")
    rec_parser.add_argument("--output", default="reports/reconciliation_report.json", help="Output report path")

    # Command: analyze
    ana_parser = subparsers.add_parser("analyze", help="Perform managerial cost breakdown")
    ana_parser.add_argument("--invoices", required=True, help="Path to invoices JSON")
    ana_parser.add_argument("--output", default="reports/managerial_report.json", help="Output report path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "reconcile":
        if not os.path.exists(args.invoices) or not os.path.exists(args.bank):
            print(f"Error: Missing input files.")
            sys.exit(1)

        with open(args.invoices, "r", encoding="utf-8") as f:
            invoices = json.load(f)
        with open(args.bank, "r", encoding="utf-8") as f:
            bank = json.load(f)

        reconciler = FinancialReconciler()
        result = reconciler.reconcile(invoices, bank)

        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print("\n=== RECONCILIATION SUMMARY ===")
        for k, v in result["summary"].items():
            print(f"  {k}: {v}")
        print(f"\nReport written to: {args.output}")

    elif args.command == "analyze":
        if not os.path.exists(args.invoices):
            print(f"Error: Invoices file not found: {args.invoices}")
            sys.exit(1)

        with open(args.invoices, "r", encoding="utf-8") as f:
            invoices = json.load(f)

        analyzer = ManagerialCostAnalyzer()
        result = analyzer.analyze(invoices)

        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print("\n=== MANAGERIAL COST BREAKDOWN ===")
        print(f"Total Expenditure: €{result['total_expenditure']:,.2f}")
        for cat, data in result["category_distribution"].items():
            print(f"  • {cat}: €{data['amount']:,.2f} ({data['percentage']}%)")
        print(f"\nReport written to: {args.output}")


if __name__ == "__main__":
    main()
