| measure | value |
|---|---|
| Monthly IRR of base project cash flow | 1.3401 % |
| x 12 (nominal annual) | 16.08 % |
| (1+r)^12 - 1 (effective annual) | 17.3214 % |
| XIRR on first-of-month dates, 365-day year | 17.3248 % |
| Example flows (years 0,1,2): +30, -120, +100 |  |
|   all real IRRs (np.roots) | 18.35 %, 181.65 % |
|   numpy_financial.irr picks | 18.35 % |
|   NPV at 0 % | 10.00 |
|   NPV at 10 % | 3.55 |
|   NPV at 50 % | -5.56 |
|   NPV at 250 % | 3.88 |
