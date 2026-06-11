<!-- ░░░ PROFILE HEADER ░░░ -->
<table border="0" cellpadding="0" cellspacing="0">
<tr>
<td width="210" valign="top">
<img src="./propic.jpeg" width="200" alt="Andrea Landini"/>
</td>
<td valign="top">

### Andrea Landini
**Credit Risk · Quantitative Finance · Markets**

M.Sc. Finance student at the Universität Liechtenstein, after a B.Sc. in
Economics and Finance at Bocconi. I work on credit risk and quantitative
finance, and I like turning stochastic calculus into tools that price and
measure risk.

[![Website](https://img.shields.io/badge/WEB-andrealandini.info-161b22?style=flat-square&logo=firefox&logoColor=00ff41&labelColor=0d1117)](https://andrealandini.info)
[![LinkedIn](https://img.shields.io/badge/LINKEDIN-in%2Fandrea--landini-161b22?style=flat-square&logo=linkedin&logoColor=00ff41&labelColor=0d1117)](https://www.linkedin.com/in/andrea-landini/)
[![GitHub](https://img.shields.io/badge/GITHUB-andrealandini-161b22?style=flat-square&logo=github&logoColor=00ff41&labelColor=0d1117)](https://github.com/andrealandini)
[![Email](https://img.shields.io/badge/EMAIL-direct-161b22?style=flat-square&logo=gmail&logoColor=00ff41&labelColor=0d1117)](mailto:andrea.landini@uni.li)

</td>
</tr>
</table>

<!-- ░░░ LIVE TICKER ░░░ -->
<img src="./ticker.svg" alt="live market ticker" width="100%"/>

---
 
## About

I focus on credit risk and quantitative finance: probability of default,
loss given default and exposure at default modelling, IFRS 9 expected credit
loss, derivative valuation and market risk. I spent six months at Deloitte in
the Financial Services audit practice, working on credit risk and IFRS 9 across
Banking and Capital Markets engagements, from PD, LGD and EAD estimates to ECL
staging and model validation.

What I enjoy most is building things that turn theory into numbers you can act
on, from stochastic pricing models to full loss distributions. The visuals
below trace that path in three steps: the mathematics of random processes,
the measurement of risk, and the pricing of credit.

---

## Foundations

It starts with randomness. These are the processes that everything downstream
is priced on, from Brownian motion to the jump models that capture defaults.

<table>
<tr>
<td width="50%"><img src="./charts/sp_brownian.svg" alt="Wiener process / Brownian motion" width="100%"/></td>
<td width="50%"><img src="./charts/sp_gbm.svg" alt="Geometric Brownian motion" width="100%"/></td>
</tr>
<tr>
<td align="center" colspan="2"><img src="./charts/sp_jump.svg" alt="Merton jump-diffusion" width="50%"/></td>
</tr>
</table>

---

## Risk

Feed those paths into a book and you get a loss distribution. The work is then
measuring its tail with VaR and Expected Shortfall, and watching how risk moves
through time.

<table>
<tr>
<td width="50%"><img src="./charts/var_fan.svg" alt="VaR fan chart" width="100%"/></td>
<td width="50%"><img src="./charts/es_cvar.svg" alt="Expected Shortfall / CVaR" width="100%"/></td>
</tr>
<tr>
<td width="50%"><img src="./charts/pnl_hist.svg" alt="P&L histogram with VaR/ES" width="100%"/></td>
<td width="50%"><img src="./charts/rolling_var.svg" alt="Rolling VaR time series" width="100%"/></td>
</tr>
</table>

---

## Credit Markets

Apply the same machinery to issuers and you are pricing credit, across the
curve, the cross section, and decomposed into its drivers.

<table>
<tr>
<td width="50%"><img src="./charts/spread_term.svg" alt="Credit spread term structure" width="100%"/></td>
<td width="50%"><img src="./charts/spread_heatmap.svg" alt="Spread heatmap" width="100%"/></td>
</tr>
<tr>
<td align="center" colspan="2"><img src="./charts/oas_waterfall.svg" alt="Z-spread / OAS waterfall" width="50%"/></td>
</tr>
</table>

---

## Featured Project

**Credit Risk Analytics Dashboard** &nbsp;·&nbsp; [github.com/andrealandini/credit-risk-modeling](https://github.com/andrealandini/credit-risk-modeling)

A quantitative credit risk dashboard in Flask with nine interchangeable models
for PD, LGD and EAD (Expected Loss = PD × LGD × EAD), including Logistic
Regression, Merton Structural, Beta Regression and Markov Transition. It runs a
Monte Carlo portfolio engine (3,000 paths) on the Vasicek single factor model
with stochastic Beta LGD, and an ECB style stress testing module with baseline,
recession, stagflation and recovery scenarios.

---

## Languages and Libraries

**Languages**

[![Python](https://img.shields.io/badge/Python-161b22?style=flat-square&logo=python&logoColor=00ff41)](https://www.python.org/)
[![R](https://img.shields.io/badge/R-161b22?style=flat-square&logo=r&logoColor=00ff41)](https://www.r-project.org/)
[![C/C++](https://img.shields.io/badge/C%2FC%2B%2B-161b22?style=flat-square&logo=cplusplus&logoColor=00ff41)](https://isocpp.org/)
[![SQL](https://img.shields.io/badge/SQL-161b22?style=flat-square&logo=postgresql&logoColor=00ff41)](https://www.postgresql.org/)

**Libraries**

[![NumPy](https://img.shields.io/badge/NumPy-161b22?style=flat-square&logo=numpy&logoColor=00cc33)](https://numpy.org/)
[![pandas](https://img.shields.io/badge/pandas-161b22?style=flat-square&logo=pandas&logoColor=00cc33)](https://pandas.pydata.org/)
[![SciPy](https://img.shields.io/badge/SciPy-161b22?style=flat-square&logo=scipy&logoColor=00cc33)](https://scipy.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-161b22?style=flat-square&logo=scikitlearn&logoColor=00cc33)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-161b22?style=flat-square&logo=streamlit&logoColor=00cc33)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-161b22?style=flat-square&logo=plotly&logoColor=00cc33)](https://plotly.com/)
[![Flask](https://img.shields.io/badge/Flask-161b22?style=flat-square&logo=flask&logoColor=00cc33)](https://flask.palletsprojects.com/)

**Tools and Data**

[![Git](https://img.shields.io/badge/Git-0d1117?style=flat-square&logo=git&logoColor=8b949e)](https://git-scm.com/)
[![LaTeX](https://img.shields.io/badge/LaTeX-0d1117?style=flat-square&logo=latex&logoColor=8b949e)](https://www.latex-project.org/)
![Bloomberg](https://img.shields.io/badge/Bloomberg-0d1117?style=flat-square&logo=bloomberg&logoColor=8b949e)
![Refinitiv](https://img.shields.io/badge/Refinitiv-0d1117?style=flat-square)
![Excel](https://img.shields.io/badge/Excel-0d1117?style=flat-square&logo=microsoftexcel&logoColor=8b949e)

---

## Interests

My work sits at the meeting point of finance, statistics and code. The themes
I keep coming back to:

- **Credit risk modelling**: PD, LGD, EAD, ECL under IFRS 9, and credit
  portfolio models such as Vasicek.
- **Market risk**: VaR, Expected Shortfall, GARCH volatility and dependency
  modelling with copulas.
- **Derivatives and pricing**: Black-Scholes, Heston, and Monte Carlo methods
  for valuation and simulation.
- **Regulation and resilience**: Basel III and IV capital frameworks and stress
  testing.
- **Building tools**: small quantitative web apps that I deploy and run on a VPS.

Away from the screen I work in three languages: Italian (native), English
(fluent) and German (B1).

---

<div align="center">

<sub>The ticker uses <b>real</b> market data (Alpaca, free tier, refreshed daily).
All analytics are driven by <b>synthetic</b> data and are illustrative only.</sub>

</div>
