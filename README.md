# Alpha Scout: Pure Factorial Asset Pricing Engine (APT) for Elite Football

## 1. Project Genesis: At the Intersection of Football, Finance & Computer Science

As a lifelong football enthusiast who consumes the game almost daily, I have always been fascinated by the quantitative metrics driving modern squad management. Coming from a background in Corporate Finance and Computer Science, I wanted to design a framework that blends quantitative finance models with high-density sports analytics. 

The football transfer market is inherently volatile, often driven by media hype, marketing potential, and social media presence. Alpha Scout was born from a simple thesis: *Can we strip away the noise and evaluate a football player purely as a financial asset, based solely on tangible pitch production and resale potential?* 

By treating specialized tracking data as economic commodities, this project implements a tailored version of the Arbitrage Pricing Theory (APT) to calculate the Fair Market Value (FMV) of elite players. It is a business-oriented, pure-pitch valuation engine mirroring the data-driven strategies of modern clubs like Chelsea (BlueCo model), Brighton, or Red Bull Leipzig.

---

## 2. Architectural Evolution & Data Mastery

### Getting Familiar with StatsBomb Data
To build this engine, I immersed myself in the StatsBomb Open Dataset API, learning to map, extract, and clean high-density event streams. Navigating their granular coordinate systems, freeze-frames, and event-tagging conventions required building a custom pipeline capable of parsing thousands of raw spatial events per match.

### Early Implementation: The 0-100 Heuristics
Originally, the project was structured around a unified "Alpha Score". The pipeline extracted raw event data, normalized the features using an empirical scale, and mapped everything to a standard 0-100 index. While visually satisfying, this approach suffered from two major architectural flaws:
1. **The Aggregation Trap:** Merging creative, defensive, and finishing attributes into a single scalar score destroyed positional nuance. A world-class defensive midfielder (e.g., Sergio Busquets) was mechanically penalized for his lack of goal contributions, skewing the overall ranking.
2. **Arbitrary Pricing:** Converting a 0-100 score directly into a monetary value required arbitrary scaling factors that failed to reflect the macroeconomic reality of the transfer market.

### Moving From Basic Features to Deep Factor Portfolios
Initially, I started by querying a limited set of basic metrics for each indicator, such as raw pass completion rates or basic interception counts. However, I quickly realized that simple volumetric metrics were completely insufficient to capture elite performance. Basic pass volume rewards safe, horizontal possession, while ignoring the high-risk vertical progressions that actually disrupt defensive blocks.

To fix this, I decoupled the model into four autonomous factor portfolios, expanding the feature space to include deep, advanced metrics:
*   `creative_score.py`: Evaluates spatial hazard generation, cutting-edge Expected Threat (xT) metrics, and Shot-Creating Actions (SCA).
*   `finishing_score.py`: Measures conversion efficiency and shot quality against expected models (xG).
*   `control_score.py`: Gauges tempo retention, press resistance, and technical security under pressure by heavily penalizing direct turnovers (`miscontrols`, `dispossessed`).
*   `defensive_score.py`: Quantifies high-risk interventions, tackle/interception density, and recovery value.

Each position in a team is assigned a vector of Positional Betas (e.g., a *Center Back* has a defense beta of 1.0 but a finishing beta of 0.0). These indicators are multiplied by fixed Market Factor Prices (the baseline cost of a raw statistical unit on the elite market) to establish the asset's baseline intrinsic value.

---

## 3. Engineering Challenges & Fighting the Overfitting Trap

The biggest milestone of this project was navigating the Overfitting Trap—a classic pitfall when domain expertise overrides statistical rigor.

### The Problem: Heuristic Over-Engineering
During initial testing on the Barcelona 2020/2021 dataset, certain players didn't match real-world market intuition. For instance, young generational talents (like Pedri) appeared undervalued due to a lack of raw shooting metrics, while backup players with low minutes or players operating in high-possession styles (like Óscar Mingueza) had inflated scores due to safe passing statistics.

To "fix" this, I initially built complex conditional clauses (e.g., checking if age was under 21, adding custom superstar bonuses, or step-function injury haircuts) to force the output to match my intuition. 

### The Realization: Breaking Generalizability
I quickly realized that adding ad-hoc, player-specific patches was leading to massive overfitting. I was building a model tailored exclusively to one specific team in one specific season. If launched on another set of players the engine would have collapsed. In quantitative finance, a pricing model must remain universally applicable and generalizable.

### The Solution: The Continuous Zero-Threshold Framework (Definitive Version)
In this definitive version, I stripped away all rule-based thresholds and hardcoded exceptions to combat overfitting. The engine now relies strictly on continuous, monotonic mathematical functions to handle risk and liquidity:

1. **Continuous Age Decay (Asset Life-Cycle):** Replaced hard tranches with a smooth polynomial decay curve. It captures the rapid premium appreciation of youth and the natural post-30 asset amortization, while preserving a protective floor solely for top-tier statistical producers.
2. **Smooth Liquidity Multiplier (Squad-Minute Ratio):** Replaced binary sample size cut-offs with an exponential power function of the player's minutes relative to the squad maximum. It smooths out the penalty for injury-impacted assets without generating artificial data cliffs.
3. **Statistical Noise Floor:** Implemented strict lower-bounds (`.clip(lower=0)`) on raw factors to prevent underperformance in non-primary duties from completely erasing core transactional value.

---

## 4. Core Framework & Formulas

The definitive asset pricing model operates through a multi-layered quantitative process:

1. **Intrinsic Value Calculation:**
   The base price of any player is built linearly by multiplying their raw performance metrics with the fixed market unit price and their specific positional beta.
   
   *Formula:*  
   `Intrinsic Value = Σ (Raw Factor Indicator × Market Unit Price × Positional Beta)`

2. **Risk and Adjusted Market Value:**
   The final valuation is then adjusted by continuous multipliers representing physical consistency, market scarcity, and the natural life-cycle of the asset.
   
   *Formula:*  
   `Fair Market Value = Intrinsic Value × Scarcity Premium × Age Multiplier × Minutes Multiplier`

The **Scarcity Premium** acts as a continuous power law. It scales up automatically when a player's cumulative multi-factor output crosses elite thresholds, capturing the non-linear financial premium clubs pay for multi-faceted stars.

---

## 5. Sample Output & Key Insights (Barcelona 2020/21 Benchmark)

When executed on the benchmark dataset, the un-biased definitive engine outputs a highly rationalized board:

*   **The Option Value of Youth:** **Pedri (€73.9M)** and **Frenkie de Jong (€79.8M)** rightfully sit at the apex of the midfield matrix. The engine perfectly captures their high availability (minutes ratio) coupled with their massive growth multipliers, separating them naturally from rotation players like **Sergiño Dest (€65.5M)**.
*   **The Injury Haircut:** **Ousmane Dembélé (€76.4M)** is adjusted properly. While his *per-90* explosive metrics are elite, his low minute volume acts as a natural liquidity anchor, stabilizing his price against real-world fragility.
*   **Asset Amortization:** **Lionel Messi (€116.7M)** retains an elite price tag due to his astronomical production, but the engine properly factors in his age (33), pricing him as a world-class short-term asset rather than a €400M speculative bubble.

---

## 6. Critical Limitations of Football Analytics

While the final valuation framework achieves high mathematical rigor in pricing pitch event volume, any quantitative approach in sports analytics has to reckon with four critical algorithmic and data-collection blind spots:

### 1. Game State Distortion (The Scoreline Bias)
Data models often evaluate actions in a vacuum, but players change their behavior entirely based on the scoreboard.
* **The Blind Spot:** If a team is winning 3-0 in the 75th minute, they will intentionally drop deep, stop pressing, pass horizontally to waste time, and take zero risks.
* **The Mathematical Flaw:** A model looking at this data will conclude that the team's creativity, progression, and intensity metrics have cratered. In reality, they are playing flawlessly according to the context of the game. While some data companies attempt to adjust for "Game State," it remains incredibly difficult to quantify when a drop in statistical output is a drop in *performance* versus a deliberate *tactical choice*.

### 2. The Chain-of-Events Fallacy (Sequence Blindness)
Most modern advanced metrics (like xG and xA) are designed to isolate a single snapshot in time. They struggle heavily with sequence.
* **The Blind Spot:** Imagine a winger who executes a brilliant sequence: they drop their shoulder, beat three players on the touchline, and cut inside, completely destroying the opposition’s defensive shape. They then play a simple, 5-yard sideways pass to the central midfielder, who takes a quick touch and scores a screamer.
* **The Mathematical Flaw:** The central midfielder gets a high xG value and the goal. The winger gets a tiny fractional xA (Expected Assist) value because the pass itself wasn't "dangerous"—the *dribble before it* was what created the danger. Metrics like xT (Expected Threat) try to fix this by measuring zone-to-zone progression, but they still fail to capture the cumulative psychological and structural collapse caused by a sequence of actions over a 30-second window.

### 3. The "Garbage In, Garbage Out" Event Tagging Problem
At the core of the multi-billion dollar football analytics industry is a surprisingly human vulnerability: *manual data collection*.
* **The Blind Spot:** While tracking data is handled by automated optical cameras, "Event Data" (registering exactly what kind of pass, tackle, or touch happened) is still largely tagged in real-time by human operators watching video feeds in a studio.
* **The Flaw:** What one operator logs as a "controlled tackle," another might log as a "blocked pass" or a "loose ball recovery." Because different data providers use entirely different definitions and subjective human logging, the baseline data feeding the AI models is often inconsistent.

### 4. Defending the Unquantifiable (The "Don't Concede" Paradox)
Data is brilliant at measuring attacking play because attacking actions have an objective goal: move the ball forward and shoot. Preventing an attack is infinitely harder to model.
* **The Blind Spot:** If a team plays a low-block defense and successfully prevents the opposition from ever entering their box, the opposition's xG will be 0.0.
* **The Flaw:** Did the defense play a masterpiece of positional denial, or was the attacking team just completely incompetent at passing? Data struggles to assign a score to *nothing happening*. It is heavily biased toward active interventions (blocks, clearances) rather than passive, highly successful structural suffocation. Paolo Maldini famously stated: *"If I have to make a tackle then I have already made a mistake."* This philosophy represents the ultimate paradox for data models.

---

## 7. Tech Stack & Installation

*   **Language:** Python 3.9+
*   **Libraries:** `pandas`, `numpy`, `scipy`
*   **Data Source:** StatsBomb Open Dataset API

### Getting Started

1. Clone the repository:
   ```bash
   git clone [https://github.com/yourusername/alpha-scout.git](https://github.com/yourusername/alpha-scout.git)
   cd alpha-scout

2. Install dependencies:
   ```
   pip install -r requirements.txt

3. Run the main file:
   ```
   python main_pipeline.py

