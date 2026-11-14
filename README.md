# The "Last Mile" Logistics Auditor

A delivery performance audit for Veridi Logistics. It links when packages arrived with how customers rated them, to answer one question: **are we failing specific regions, or is this a nationwide problem?**

## A. Executive Summary

We checked 99,441 orders to see if late deliveries explain the rise in bad reviews, and they clearly do: on-time orders average 4.29 stars, late orders 2.99, and super late orders (more than 5 days late) just 1.74, with 76% of super late orders getting a 1 or 2 star review. The problem is regional, not nationwide. The Northeast is late 12.7% of the time, about double the South (5.9%), and Alagoas (21.4%), Maranhão (17.4%) and Sergipe (15.2%) are the worst states. Remote states are hit harder overall (every Northeast state and the North as a whole are above the national average), but distance is not the whole story, since far-off Amazonas and Rondônia are among the best states. Our delivery estimates are usually too long, not too short (23 days promised vs 12 days taken on average), but late orders spiked to 19% in March 2018 and review scores fell in the same months.

## B. Project Links

- **Notebook:** [logistics_auditor.ipynb](logistics_auditor.ipynb) (HTML export with all charts: [logistics_auditor.html](logistics_auditor.html))
- **Dashboard:** https://maqamylee0-logistics-auditor-dashboardapp-m1yprc.streamlit.app/
- **Presentation:** [logistics_audit_presentation.pdf](presentation/logistics_audit_presentation.pdf) (editable PowerPoint: [logistics_audit_presentation.pptx](presentation/logistics_audit_presentation.pptx))

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

## Project Structure

| Path | What it is |
|---|---|
| `logistics_auditor.ipynb` | The analysis notebook, step by step |
| `logistics_auditor.html` | HTML export of the notebook with all charts |
| `dashboard/app.py` | The Streamlit dashboard |
| `dashboard/orders.csv.gz`, `dashboard/categories.csv` | Small clean data files the dashboard reads (made by the notebook) |
| `presentation/` | The slide deck as PDF and PowerPoint |
| `requirements.txt` | Packages for the notebook |
| `data/olist/` | Raw Olist CSVs (not in the repo, download them from Kaggle) |
