"""Trader CLI for UK Day-Ahead Wind Forecast Evaluation.

Command-line tool for energy analysts and trading desks to run point-in-time
forecast evaluations, backtest custom delivery windows, and export data.
"""

import argparse
import sys

from backend.app.config import (
    DEFAULT_CUTOFF_TIME,
    JANUARY_2026_END_DELIVERY,
)
from backend.app.services.cashflow import compute_day_cashflow
from backend.app.services.data_store import data_store
from backend.app.services.metrics import (
    calculate_summary_metrics,
)
from backend.app.services.resolver import (
    parse_delivery_date,
    resolve_day_forecast,
)


def run_evaluate(args: argparse.Namespace) -> None:
    """Evaluate a single delivery day at decision-time cutoff."""
    print("\n=======================================================")
    print(f" GB Wind Forecast Evaluation — Delivery Day: {args.date}")
    print(f" D-1 Gate Cutoff: {args.cutoff} UK")
    print("=======================================================\n")

    if not data_store.has_snapshot():
        print("ERROR: Snapshot data not found in backend/data/. Run backend/ingest.py first.")
        sys.exit(1)

    day_summary = resolve_day_forecast(
        delivery_date_str=args.date,
        cutoff_time_str=args.cutoff,
        forecasts_df=data_store.get_forecasts(),
        actuals_df=data_store.get_actuals(),
        historical_band_map=data_store.get_historical_band_map(),
    )

    cashflow = compute_day_cashflow(day_summary)

    print(
        f"{'SP':<4} {'Time':<7} {'Forecast(MW)':<14} {'Actual(MW)':<12} {'Error(MW)':<11} {'Cashflow(£)':<12}"
    )
    print("-" * 65)

    for p, c in zip(day_summary.periods, cashflow.periods):
        fc_str = f"{p.forecast_mw:,.0f}" if p.forecast_mw is not None else "N/A"
        ac_str = f"{p.actual_mw:,.0f}" if p.actual_mw is not None else "N/A"
        err_str = f"{p.error_mw:+,.0f}" if p.error_mw is not None else "N/A"
        cf_str = (
            f"£{c.imbalance_cashflow_gbp:+,.0f}" if c.imbalance_cashflow_gbp is not None else "N/A"
        )

        print(
            f"{p.period_index:<4} {p.start_time_local:<7} {fc_str:<14} {ac_str:<12} {err_str:<11} {cf_str:<12}"
        )

    print("-" * 65)
    print("\n--- Summary Performance Metrics ---")
    if day_summary.peak_forecast_mw is not None:
        print(f"  Peak Forecast:     {day_summary.peak_forecast_mw:,.0f} MW")
    if day_summary.avg_forecast_mw is not None:
        print(f"  Day Average:       {day_summary.avg_forecast_mw:,.0f} MW")
    if day_summary.mae_mw is not None:
        print(f"  Mean Absolute Err: {day_summary.mae_mw:,.0f} MW")
    if day_summary.mean_error_mw is not None:
        sign = "+" if day_summary.mean_error_mw > 0 else ""
        print(f"  Mean Bias:         {sign}{day_summary.mean_error_mw:,.0f} MW")

    print("\n--- Financial Imbalance Exposure ---")
    print(
        f"  Gross Shortfall:   {cashflow.gross_short_mwh:,.1f} MWh (£{cashflow.total_short_penalty_gbp:,.0f} buyback)"
    )
    print(
        f"  Gross Surplus:     {cashflow.gross_long_mwh:,.1f} MWh (£{cashflow.total_long_settlement_gbp:,.0f} credit)"
    )
    print(f"  Net Exposure:      £{cashflow.net_cashflow_exposure_gbp:+,.0f}")
    print(f"  P10-P90 Hedging:   £{cashflow.hedge_savings_p10_p90_gbp:,.0f} margin protected\n")


def run_backtest(args: argparse.Namespace) -> None:
    """Run accuracy backtest across a multi-day window."""
    print("\n=======================================================")
    print(f" GB Wind Forecast Backtest: {args.from_date} to {args.to_date}")
    print(f" Cutoff: {args.cutoff} UK")
    print("=======================================================\n")

    if not data_store.has_snapshot():
        print("ERROR: Snapshot data not found. Run backend/ingest.py first.")
        sys.exit(1)

    from_d = parse_delivery_date(args.from_date)
    to_d = parse_delivery_date(args.to_date)

    if from_d > to_d:
        print("ERROR: --from must be on or before --to.")
        sys.exit(1)

    df = data_store.evaluate_period_range(args.from_date, args.to_date, args.cutoff)
    valid = df.dropna(subset=["error_mw"])

    errors = valid["error_mw"].tolist()
    actuals = valid["actual_mw"].tolist() if "actual_mw" in valid.columns else None

    summary = calculate_summary_metrics(errors, actuals)

    print(f"Evaluated Settlement Periods:  {summary.count}")
    print(f"Mean Absolute Error (MAE):     {summary.mae_mw:,.1f} MW")
    bias_sign = "+" if summary.bias_mw > 0 else ""
    print(
        f"Mean Directional Bias:         {bias_sign}{summary.bias_mw:,.1f} MW ({'Over-forecast' if summary.bias_mw > 0 else 'Under-forecast'})"
    )
    print(f"Root Mean Square Error (RMSE): {summary.rmse_mw:,.1f} MW")
    nmae_str = f"{summary.nmae_pct:.2f}%" if summary.nmae_pct is not None else "N/A"
    print(f"Normalized MAE (nMAE):         {nmae_str}")
    print(f"10th Percentile Error (P10):   {summary.p10_mw:,.1f} MW")
    print(f"90th Percentile Error (P90):   +{summary.p90_mw:,.1f} MW")
    print(f"P10-P90 Risk Envelope:         {(summary.p90_mw - summary.p10_mw):,.1f} MW\n")


def run_export(args: argparse.Namespace) -> None:
    """Export evaluated settlement periods to CSV file."""
    print(f"Exporting window {args.from_date} to {args.to_date} to {args.out}...")
    from_d = parse_delivery_date(args.from_date)
    to_d = parse_delivery_date(args.to_date)

    if from_d > to_d:
        print("ERROR: --from must be on or before --to.")
        sys.exit(1)

    df = data_store.evaluate_period_range(args.from_date, args.to_date, args.cutoff)
    df.to_csv(args.out, index=False)
    print(f"Successfully exported {len(df)} settlement period rows to {args.out}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="GB Wind Power Forecast Desk CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # evaluate command
    p_eval = subparsers.add_parser("evaluate", help="Evaluate a single delivery day")
    p_eval.add_argument(
        "--date", default=JANUARY_2026_END_DELIVERY, help="Delivery date YYYY-MM-DD"
    )
    p_eval.add_argument("--cutoff", default=DEFAULT_CUTOFF_TIME, help="Cutoff time HH:MM")

    # backtest command
    p_bt = subparsers.add_parser("backtest", help="Backtest accuracy across date window")
    p_bt.add_argument(
        "--from", dest="from_date", default="2026-01-02", help="Start date YYYY-MM-DD"
    )
    p_bt.add_argument("--to", dest="to_date", default="2026-02-01", help="End date YYYY-MM-DD")
    p_bt.add_argument("--cutoff", default=DEFAULT_CUTOFF_TIME, help="Cutoff time HH:MM")

    # export command
    p_exp = subparsers.add_parser("export", help="Export evaluation dataset to CSV")
    p_exp.add_argument(
        "--from", dest="from_date", default="2026-01-02", help="Start date YYYY-MM-DD"
    )
    p_exp.add_argument("--to", dest="to_date", default="2026-02-01", help="End date YYYY-MM-DD")
    p_exp.add_argument("--cutoff", default=DEFAULT_CUTOFF_TIME, help="Cutoff time HH:MM")
    p_exp.add_argument("--out", default="gb_wind_export.csv", help="Output file path")

    args = parser.parse_args()

    if args.command == "evaluate":
        run_evaluate(args)
    elif args.command == "backtest":
        run_backtest(args)
    elif args.command == "export":
        run_export(args)


if __name__ == "__main__":
    main()
