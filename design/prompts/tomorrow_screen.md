# Stitch Design Prompt: Day-Ahead Wind Forecast ("Tomorrow" View)

## Target Audience
UK day-ahead wholesale power trading desk buying power for delivery day D on D-1.

## Functional Requirements & Data Shown
1. **Decision Gate Header**: Delivery day picker (Jan 2026), D-1 09:00 UK cut-off countdown/state, and BMRS ingestion telemetry badge (`Live 99.4% BMRS FUELHH`).
2. **Hero Headline**: High-impact statement for trading desk decision-making.
3. **Primary Action**: Solid black pill button (`View Tomorrow's Forecast →`) and secondary dataset download pill.
4. **6-Card Feature Grid**:
   - Peak Forecast (MW)
   - Day Average (MW)
   - Mean Absolute Error (MAE)
   - Mean Directional Bias (+1,746 MW Over-forecast)
   - P10–P90 Uncertainty Envelope (2,450 MW)
   - Data Health & Settlement (100% Complete)
5. **Main Chart Card**:
   - Outturn Actual Generation (Bonsai Emerald `#10b981` solid line).
   - D-1 Day-Ahead Forecast (Slate Navy `#0f172a` dashed line).
   - Historical P10–P90 error envelope (translucent emerald fill).
   - Hover crosshair with tooltip at 14:00 UK.
6. **Trading Methodology 2-Column Section**:
   - 3 bullet items with green checkmarks on balancing mechanism cashout protection.
   - Skew insight callout card (morning ramp vs evening peak MAE).

## Aesthetic & Style Direction
- Theme: Bonsai SaaS clean light theme.
- Canvas: Pure white (`#ffffff`) with soft containers (`#f8fafc`).
- Borders: Crisp `1px solid #e2e8f0`.
- Buttons: Rounded full (`9999px`) solid black pills.
- Typography: `Plus Jakarta Sans` for UI and `JetBrains Mono` for numerical values.
