# The "Last Mile" Logistics Auditor

## A. Executive Summary

We checked 99,441 orders to see if late deliveries explain the rise in bad reviews, and they clearly do: on-time orders average 4.29 stars, late orders 2.99, and super late orders (more than 5 days late) just 1.74, with 76% of super late orders getting a 1 or 2 star review. The problem is regional, not nationwide. The Northeast is late 12.7% of the time, about double the South (5.9%), and Alagoas (21.4%), Maranhão (17.4%) and Sergipe (15.2%) are the worst states. Remote states are hit harder overall (every Northeast state and the North as a whole are above the national average), but distance is not the whole story, since far-off Amazonas and Rondônia are among the best states. Our delivery estimates are usually too long, not too short (23 days promised vs 12 days taken on average), but late orders spiked to 19% in March 2018 and review scores fell in the same months.

## B. Project Links

- **Notebook:** [logistics_auditor.ipynb](logistics_auditor.ipynb) (HTML export with all charts: [logistics_auditor.html](logistics_auditor.html))
- **Dashboard:** https://maqamylee0-logistics-auditor-dashboardapp-m1yprc.streamlit.app/
- **Presentation:** [logistics_audit_presentation.pdf](presentation/logistics_audit_presentation.pdf) (editable PowerPoint: [logistics_audit_presentation.pptx](presentation/logistics_audit_presentation.pptx))
- **Video walkthrough (optional):** _TODO_

## C. Technical Explanation

### Data Cleaning

- **Joins:** We joined Orders to Customers on `customer_id` and Orders to Reviews on `order_id`, using left joins so no order is lost.
- **Duplicates:** 551 orders had more than one review, which would have copied those orders in the join. We kept only the latest review per order (99,224 → 98,673 reviews).
- **Row check:** The master table has 99,441 rows before and after the joins, and every `order_id` appears once. 768 orders have no review.
- **Undelivered orders:** 2,971 orders were never delivered (canceled, unavailable, shipped, etc., plus 8 marked "delivered" with no delivery date). They are flagged as "Not Delivered" and left out of the delay analysis, leaving 96,470 orders.
- **Delay:** `Days_Difference` = estimated date − delivered date, in whole days (positive = early). On Time = 0 or more, Late = 1 to 5 days late, Super Late = more than 5 days late.
- **Categories (bonus):** Products are linked through the order items table in a separate table, so the master table is not duplicated. Category names are translated to English using `product_category_name_translation.csv`.

### Candidate's Choice

**Monthly trend of late orders vs review score** (notebook Step 8 and in the dashboard).

The CEO noticed a *recent spike* in bad reviews, so we track the late rate and average review score month by month. The two move closely together (correlation of −0.8), and the worst months were March 2018 (19% late), February 2018 (14%) and November 2017 (12%). This matters because it shows *when* the problem happened, not just where, and gives the team a simple monthly early warning: when the late rate goes up, reviews will fall, so they can act before customers complain.

The dashboard also has region and state filters, so a regional director can look at just their area.

## Running Locally

1. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and put the CSV files in a `data/olist/` folder in this project (it is git-ignored).
2. Create an environment and install the packages:
   ```bash
   python3 -m venv logistics-auditor-env
   source logistics-auditor-env/bin/activate
   pip install -r requirements.txt -r dashboard/requirements.txt
   ```
3. Open `logistics_auditor.ipynb` and run all cells. This also writes the small data files the dashboard uses into `dashboard/`.
4. Run the dashboard: `streamlit run dashboard/app.py`

---

# Original Challenge Brief


**Client:** Veridi Logistics (Global E-Commerce Aggregator)
**Deliverable:** Public Dashboard, Code Notebook & Insight Presentation

---

## 1. Business Context

**Veridi Logistics** manages shipping for thousands of online sellers. Recently, the CEO has noticed a spike in negative customer reviews. She has a "gut feeling" that the problem isn't just that packages are late, but that the estimated delivery dates provided to customers are wildly inaccurate (i.e., we are over-promising and under-delivering).

She needs you to audit the delivery data to find the root cause. She specifically wants to know: **"Are we failing specific regions, or is this a nationwide problem?"**

Your job is to build a "Delivery Performance" audit tool that connects the dots between **Logistics Data** (when a package arrived) and **Customer Sentiment** (how they rated the experience).

## 2. The Data

You will use the **Olist E-Commerce Dataset**, a real commercial dataset from a Brazilian marketplace. This is a relational database dump, meaning the data is split across multiple CSV files.

- **Source:** [Kaggle - Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Key Files to Use:**
  - `olist_orders_dataset.csv` (The central table)
  - `olist_order_reviews_dataset.csv` (Sentiment)
  - `olist_customers_dataset.csv` (Location)
  - `olist_products_dataset.csv` (Categories)

## 3. Tooling Requirements

You have the flexibility to choose your development environment:

- **Option A (Recommended):** Use a cloud-hosted notebook like **Google Colab**, or **Deepnote**, etc.
- **Option B:** Use a local **Jupyter Notebook** or **VS Code**.
  - _Condition:_ If you choose this, you must ensure your code is reproducible. Do not reference local file paths (e.g., `C:/Downloads/...`). Assume the dataset is in the same folder as your notebook.
- **Dashboarding:** The final output must be a **publicly accessible link** (e.g., Tableau Public, Google Looker Studio, Streamlit Cloud, or PowerBI Web, etc.).

---

## 4. User Stories & Acceptance Criteria

### Story 1: The Schema Builder

**As a** Data Engineer,
**I want** to join the Orders, Reviews, and Customers tables into a single master dataset,
**So that** I can analyze a customer's location and their review score in the same row.

- **Acceptance Criteria:**
  - Load the raw CSVs into your notebook.
  - Perform the correct joins (e.g., join Reviews to Orders on `order_id`, join Customers to Orders on `customer_id`).
  - **Check:** Ensure you don't accidentally duplicate rows (a common error with 1-to-many joins).

### Story 2: The "Real" Delay Calculator

**As a** Logistics Manager,
**I want** to know the difference between the "Estimated Delivery Date" and the "Actual Delivery Date,"
**So that** I can see how often we are lying to customers.

- **Acceptance Criteria:**
  - Create a new calculated column: `Days_Difference` = `order_estimated_delivery_date` - `order_delivered_customer_date`.
  - Classify orders into statuses: "On Time", "Late", and "Super Late" (> 5 days late).
  - Handle missing values: Some orders were never delivered (`order_status` = 'canceled' or 'unavailable'). These should be excluded or flagged separately.

### Story 3: The Geographic Heatmap

**As a** Regional Director,
**I want** to see which specific States (`customer_state`) have the highest percentage of late deliveries,
**So that** I can focus my repair efforts on the worst regions.

- **Acceptance Criteria:**
  - Calculate the % of late orders per State.
  - Visualize this on a map or a bar chart.
  - **Insight:** Identify if "Remote" states (far from the distribution center) are disproportionately affected.

### Story 4: The Sentiment Correlation

**As a** Customer Success Lead,
**I want** to see if late deliveries actually cause bad reviews,
**So that** I can prove to the CEO that logistics is the problem.

- **Acceptance Criteria:**
  - Create a visualization comparing "Delivery Delay (Days)" vs "Average Review Score (1-5)".
  - Show the average review score for "On Time" orders vs. "Late" orders.

---

## 5. Bonus User Story: The "Translation" Challenge

**As a** Global Analyst,
**I want** to see product categories in **English**, not Portuguese,
**So that** I can understand if "Furniture" is harder to ship than "Electronics".

- **Acceptance Criteria:**
  - The `product_category_name` is in Portuguese (e.g., `cama_mesa_banho`).
  - Use the `product_category_name_translation.csv` file included in the dataset (or create your own mapping) to translate these into English for your final dashboard.

---

## 6. The "Candidate's Choice" Challenge

**As a** Creative Problem Solver,
**I want** to include one extra feature or analysis that adds specific business value,
**So that** I can demonstrate my ability to think beyond the basic requirements.

- **Instructions:**
  - Add one more metric, chart, or drill-down.
  - **Requirement:** You must justify _why_ this feature matters to the business in your README.

---

## 7. Submission Guidelines

Please edit this `README.md` file in your forked repository to include the following three sections at the top:

### A. The Executive Summary

- A 3-5 sentence summary of your findings.

### B. Project Links

- **Link to Notebook:** (e.g., Google Colab, etc.). _Ensure sharing permissions are set to "Anyone with the link can view"._
- **Link to Dashboard:** (e.g., Tableau Public, etc.).
- **Link to Presentation:** A link to a short slide deck (PDF/PPT) AND (Optional) a 2-minute video walkthrough (YouTube) explaining your results.

### C. Technical Explanation

- Briefly explain how you handled the "Data Cleaning".
- Explain your "Candidate's Choice" addition.

**Important Note on Code Submission:**

- Upload your `.ipynb` notebook file to the repo.
- **Crucial:** Also upload an **HTML or PDF export** of your notebook so we can see your charts even if GitHub fails to render the notebook code.
- Once you are ready, please fill out the [Official Submission Form Here](https://forms.cloud.microsoft/e/CeQN2mCyUr) with your links

---

## 🛑 CRITICAL: Pre-Submission Checklist

**Before you submit your form, you MUST complete this checklist.**

> ⚠️ **WARNING:** If you miss any of these items, your submission will be flagged as "Incomplete" and you will **NOT** be invited to an interview.
>
> **We do not accept "permission error" excuses. Test your links in Incognito Mode.**

### 1. Repository & Code Checks

- [ ] **My GitHub Repo is Public.** (Open the link in a Private/Incognito window to verify).
- [ ] **I have uploaded the `.ipynb` notebook file.**
- [ ] **I have ALSO uploaded an HTML or PDF export** of the notebook.
- [ ] **I have NOT uploaded the massive raw dataset.** (Use `.gitignore` or just don't commit the CSV).
- [ ] **My code uses Relative Paths.**

### 2. Deliverable Checks

- [ ] **My Dashboard link is publicly accessible.** (No login required).
- [ ] **My Presentation link is publicly accessible.** (Permissions set to "Anyone with the link can view").
- [ ] **I have updated this `README.md` file** with my Executive Summary and technical notes.

### 3. Completeness

- [ ] I have completed **User Stories 1-4**.
- [ ] I have completed the **"Candidate's Choice"** challenge and explained it in the README.

**✅ Only when you have checked every box above, proceed to the submission form.**

---
