# Stitch Design Prompt: Accuracy & Error Analytics Screen

## Target Audience
Desk leads, risk managers, and power traders evaluating historical forecast accuracy across January 2026.

## Functional Requirements & Data Shown
1. **Benchmark Hero**: January 2026 audit header (`744 Settlement Periods Audited • 0 Data Gaps`).
2. **Key Metric Cards (3x2 Grid)**:
   - Overall MAE (1,842 MW)
   - Mean Directional Bias (+1,210 MW)
   - Root Mean Square Error (2,340 MW)
   - Peak Error Hour (Hour 18:00 / SP 36)
   - P90 Risk Envelope (3,890 MW)
   - Data Health (100% Complete)
3. **Multi-Horizon Variance Breakdown**:
   - Bar chart showing forecast convergence from early gate closure (`D-1 09:00`, `D-1 12:00`, `D-1 16:00`, `D-1 21:00`).
4. **Trading Takeaways & Distribution Section**:
   - Left: Imbalance cashflow implications & hedging savings.
   - Right: Gaussian error distribution curve with annotated P10, P50, and P90 percentiles.

## Aesthetic Direction
- Theme: Bonsai SaaS clean light theme.
- Palette: White, slate gray, emerald green highlights (`#10b981`).
- Pill action buttons with dark slate hover transitions.
