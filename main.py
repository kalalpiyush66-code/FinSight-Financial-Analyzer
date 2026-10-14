import streamlit as st
import pandas as pd
import numpy_financial as npf

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="FinSight | Financial Analyzer",
    page_icon="📊",
    layout="wide"
)

# ============================================================
# DASHBOARD DESIGN
# ============================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1250px;
}

.hero {
    padding: 28px;
    border-radius: 16px;
    background: linear-gradient(120deg, #10243a, #17616b);
    color: white;
    margin-bottom: 24px;
}

.hero h1 {
    margin-bottom: 8px;
}

div[data-testid="stMetric"] {
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.25);
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>📊 FinSight Financial Analyzer</h1>
    <p>Flexible cash-flow analysis, investment appraisal and DCF valuation.</p>
</div>
""", unsafe_allow_html=True)

st.caption(
    "An educational financial analysis tool. "
    "Results depend on the assumptions you enter."
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Financial Workspace")

analysis = st.sidebar.radio(
    "Choose an analysis",
    [
        "Overview",
        "Custom Cash-Flow Analysis",
        "Constant-Growth DCF",
        "ARR Calculator"
    ]
)

currency = st.sidebar.selectbox(
    "Currency",
    ["₹ INR", "$ USD", "€ EUR", "£ GBP", "Other"]
)

symbol = {
    "₹ INR": "₹",
    "$ USD": "$",
    "€ EUR": "€",
    "£ GBP": "£",
    "Other": ""
}[currency]


def money(value):
    """Format a numeric value using the selected currency."""
    return f"{symbol}{value:,.2f}"


# ============================================================
# OVERVIEW
# ============================================================

if analysis == "Overview":

    st.subheader("Welcome to your financial workspace")

    st.markdown("### What can you calculate?")

    st.markdown("""
    - **Custom Cash-Flow Analysis:** Enter annual inflows and
      outflows and calculate NPV, IRR and payback periods.
    - **Constant-Growth DCF:** Forecast cash flows using growth
      and discount rates, with optional terminal value.
    - **ARR Calculator:** Calculate Accounting Rate of Return
      using accounting profit and investment assumptions.
    """)

    st.info("Choose an analysis from the sidebar to begin.")


# ============================================================
# CUSTOM CASH-FLOW ANALYSIS
# ============================================================

elif analysis == "Custom Cash-Flow Analysis":

    st.subheader("Custom Cash-Flow Analysis")

    st.write(
        "Enter each year's inflows and outflows independently. "
        "FinSight will calculate net cash flow, discounted net cash "
        "flow, NPV, IRR and payback periods."
    )

    # Keep year selector outside the form so it updates immediately.
    years = st.number_input(
        "Number of forecast years",
        min_value=1,
        max_value=100,
        value=4,
        step=1,
        key="custom_cashflow_years"
    )

    st.caption(
        f"You have selected {int(years)} forecast year(s). "
        "The annual cash-flow fields adjust automatically."
    )

    with st.form("cashflow_form"):

        # ----------------------------------------------------
        # INITIAL INVESTMENT
        # ----------------------------------------------------

        st.markdown("### Initial Investment")

        include_initial = st.checkbox(
            "Include an initial investment at Year 0",
            value=True,
            key="include_initial_investment"
        )

        initial_investment = st.number_input(
            "Initial investment amount",
            min_value=0.0,
            value=200000.0,
            step=1000.0,
            disabled=not include_initial,
            key="initial_investment_amount"
        )

        # ----------------------------------------------------
        # ANNUAL CASH FLOWS
        # ----------------------------------------------------

        st.markdown("### Annual Cash Flows")

        st.caption(
            "Enter cash outflows as positive amounts. "
            "They will be subtracted automatically."
        )

        inflows = []
        outflows = []

        for year in range(1, int(years) + 1):

            st.markdown(f"**Year {year}**")

            col1, col2 = st.columns(2)

            with col1:

                inflow = st.number_input(
                    f"Cash inflow — Year {year}",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    key=f"inflow_{year}"
                )

            with col2:

                outflow = st.number_input(
                    f"Cash outflow — Year {year}",
                    min_value=0.0,
                    value=0.0,
                    step=1000.0,
                    key=f"outflow_{year}"
                )

            inflows.append(inflow)
            outflows.append(outflow)

        # ----------------------------------------------------
        # CALCULATION OPTIONS
        # ----------------------------------------------------

        st.markdown("### Choose Calculations")

        calculate_npv = st.checkbox(
            "Calculate NPV",
            value=True
        )

        calculate_irr = st.checkbox(
            "Calculate IRR",
            value=True
        )

        calculate_payback = st.checkbox(
            "Calculate simple payback period",
            value=True
        )

        calculate_discounted_payback = st.checkbox(
            "Calculate discounted payback",
            value=True
        )

        show_discounted_cashflows = st.checkbox(
            "Show discounted cash flows in the schedule",
            value=True
        )

        needs_discount = (
            calculate_npv
            or calculate_discounted_payback
            or show_discounted_cashflows
        )

        use_discount = st.checkbox(
            "Enter a discount rate",
            value=True
        )

        discount_pct = st.number_input(
            "Discount rate (%)",
            min_value=-99.99,
            max_value=10000.0,
            value=10.0,
            step=0.5,
            disabled=not use_discount
        )

        submitted = st.form_submit_button(
            "Calculate Results",
            type="primary",
            use_container_width=True
        )

    # ========================================================
    # CALCULATE RESULTS
    # ========================================================

    if submitted:

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        rate = discount_pct / 100

        if needs_discount and not use_discount:

            st.error(
                "Enable the discount-rate option to calculate "
                "discounted cash flows, NPV or discounted payback."
            )

        elif needs_discount and rate <= -1:

            st.error(
                "The discount rate must be greater than -100%."
            )

        else:

            # ------------------------------------------------
            # NET CASH FLOWS
            # ------------------------------------------------

            net_flows = [
                inflows[i] - outflows[i]
                for i in range(int(years))
            ]

            # Year 0 is included only when initial investment
            # is selected.

            if include_initial:

                cash_flows = (
                    [-initial_investment] + net_flows
                )

                periods = (
                    ["Year 0"]
                    + [
                        f"Year {i}"
                        for i in range(1, int(years) + 1)
                    ]
                )

                displayed_inflows = [0.0] + inflows

                displayed_outflows = (
                    [initial_investment] + outflows
                )

                displayed_flows = (
                    [-initial_investment] + net_flows
                )

                year_numbers = list(
                    range(0, int(years) + 1)
                )

            else:

                cash_flows = net_flows

                periods = [
                    f"Year {i}"
                    for i in range(1, int(years) + 1)
                ]

                displayed_inflows = inflows
                displayed_outflows = outflows
                displayed_flows = net_flows

                year_numbers = list(
                    range(1, int(years) + 1)
                )

            # ------------------------------------------------
            # DISCOUNT FACTORS AND DISCOUNTED CASH FLOWS
            # ------------------------------------------------

            if use_discount:

                discount_factors = [
                    1 / ((1 + rate) ** year)
                    for year in year_numbers
                ]

                discounted_flows = [
                    flow * factor
                    for flow, factor in zip(
                        displayed_flows,
                        discount_factors
                    )
                ]

            else:

                discount_factors = [None] * len(periods)
                discounted_flows = [None] * len(periods)

            # ------------------------------------------------
            # BUILD CASH-FLOW SCHEDULE
            # ------------------------------------------------

            results_data = {
                "Period": periods,
                "Cash Inflow": displayed_inflows,
                "Cash Outflow": displayed_outflows,
                "Net Cash Flow": displayed_flows
            }

            if show_discounted_cashflows and use_discount:

                results_data["Discount Factor"] = (
                    discount_factors
                )

                results_data["Discounted Net Cash Flow"] = (
                    discounted_flows
                )

            results_df = pd.DataFrame(results_data)

            # ------------------------------------------------
            # DISPLAY CASH-FLOW SCHEDULE
            # ------------------------------------------------

            st.markdown("### Cash-Flow Schedule")

            st.caption(
                "Discounted net cash flow = Net cash flow × "
                "Discount factor. Year 0 is not discounted."
            )

            # Apply readable number formatting.
            format_columns = {
                "Cash Inflow": "{:,.2f}",
                "Cash Outflow": "{:,.2f}",
                "Net Cash Flow": "{:,.2f}"
            }

            if (
                show_discounted_cashflows
                and use_discount
            ):

                format_columns["Discount Factor"] = "{:.4f}"

                format_columns[
                    "Discounted Net Cash Flow"
                ] = "{:,.2f}"

            st.dataframe(
                results_df.style.format(format_columns),
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # TOTAL CASH-FLOW METRICS
            # ------------------------------------------------

            st.markdown("### Cash-Flow Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Total Cash Inflows",
                money(sum(inflows))
            )

            col2.metric(
                "Total Annual Outflows",
                money(sum(outflows))
            )

            col3.metric(
                "Total Net Cash Flow",
                money(sum(displayed_flows))
            )

            # ------------------------------------------------
            # NPV
            # ------------------------------------------------

            npv_value = None

            if calculate_npv and use_discount:

                # Discount each cash flow using its actual year.
                # This correctly handles Year 0 and does not
                # accidentally treat Year 1 as Year 0.

                npv_value = sum(discounted_flows)

                st.markdown("### Net Present Value")

                st.metric(
                    "Net Present Value (NPV)",
                    money(npv_value)
                )

                if npv_value > 0:

                    st.success(
                        "Positive NPV: the discounted inflows "
                        "exceed the initial investment."
                    )

                elif npv_value < 0:

                    st.warning(
                        "Negative NPV: the discounted inflows "
                        "are below the initial investment."
                    )

                else:

                    st.info(
                        "NPV is zero: discounted inflows equal "
                        "the investment."
                    )

            # ------------------------------------------------
            # IRR
            # ------------------------------------------------

            if calculate_irr:

                st.markdown("### Internal Rate of Return")

                try:

                    irr = float(npf.irr(cash_flows))

                    if (
                        any(x < 0 for x in cash_flows)
                        and any(x > 0 for x in cash_flows)
                        and pd.notna(irr)
                        and abs(irr) != float("inf")
                    ):

                        st.metric(
                            "Internal Rate of Return (IRR)",
                            f"{irr * 100:.2f}%"
                        )

                    else:

                        st.warning(
                            "IRR requires both negative and positive "
                            "cash flows. A unique IRR may not exist."
                        )

                except (
                    ValueError,
                    OverflowError,
                    ZeroDivisionError
                ):

                    st.warning(
                        "IRR could not be calculated for these cash flows."
                    )

            # ------------------------------------------------
            # SIMPLE PAYBACK
            # ------------------------------------------------

            if calculate_payback:

                st.markdown("### Simple Payback Period")

                if (
                    not include_initial
                    or initial_investment <= 0
                ):

                    st.info(
                        "Simple payback requires a positive "
                        "initial investment at Year 0."
                    )

                else:

                    cumulative = -initial_investment
                    payback = None

                    if cumulative >= 0:
                        payback = 0.0

                    else:

                        for i, flow in enumerate(
                            net_flows,
                            start=1
                        ):

                            previous = cumulative
                            cumulative += flow

                            if cumulative >= 0 and flow > 0:

                                payback = (
                                    i - 1
                                    + (0 - previous) / flow
                                )

                                break

                    if payback is None:

                        st.metric(
                            "Simple Payback",
                            "Not recovered in forecast"
                        )

                    else:

                        st.metric(
                            "Simple Payback",
                            f"{payback:.2f} years"
                        )

            # ------------------------------------------------
            # DISCOUNTED PAYBACK
            # ------------------------------------------------

            if calculate_discounted_payback:

                st.markdown("### Discounted Payback Period")

                if not use_discount:

                    st.warning(
                        "Enable the discount rate to calculate "
                        "discounted payback."
                    )

                elif (
                    not include_initial
                    or initial_investment <= 0
                ):

                    st.info(
                        "Discounted payback requires a positive "
                        "initial investment at Year 0."
                    )

                else:

                    cumulative = -initial_investment
                    discounted_payback = None

                    if cumulative >= 0:
                        discounted_payback = 0.0

                    else:

                        for year, flow in enumerate(
                            net_flows,
                            start=1
                        ):

                            pv_flow = (
                                flow / ((1 + rate) ** year)
                            )

                            previous = cumulative
                            cumulative += pv_flow

                            if (
                                cumulative >= 0
                                and pv_flow > 0
                            ):

                                discounted_payback = (
                                    year - 1
                                    + (0 - previous) / pv_flow
                                )

                                break

                    if discounted_payback is None:

                        st.metric(
                            "Discounted Payback",
                            "Not recovered in forecast"
                        )

                    else:

                        st.metric(
                            "Discounted Payback",
                            f"{discounted_payback:.2f} years"
                        )

            # ------------------------------------------------
            # CASH-FLOW CHART
            # ------------------------------------------------

            st.markdown("### Cash-Flow Chart")

            chart_columns = ["Net Cash Flow"]

            if (
                show_discounted_cashflows
                and use_discount
            ):

                chart_columns.append(
                    "Discounted Net Cash Flow"
                )

            chart_df = results_df.copy()

            chart_df["Period"] = pd.Categorical(
                chart_df["Period"],
                categories=periods,
                ordered=True
            )

            st.bar_chart(
                chart_df.set_index("Period")[chart_columns]
            )

            # ------------------------------------------------
            # FORMULA EXPLANATION
            # ------------------------------------------------

            with st.expander(
                "How are discounted cash flows calculated?"
            ):

                st.markdown("""
                **Discount Factor**

                Discount Factor = 1 / (1 + discount rate) ^ year

                **Discounted Net Cash Flow**

                Discounted Net Cash Flow = Net Cash Flow ×
                Discount Factor

                **Net Present Value**

                NPV = Sum of all discounted net cash flows,
                including the initial investment at Year 0.

                The Year 0 discount factor is 1, so the initial
                investment is not discounted.
                """)


# ============================================================
# CONSTANT-GROWTH DCF
# ============================================================

elif analysis == "Constant-Growth DCF":

    st.subheader("Constant-Growth DCF Valuation")

    st.write(
        "Forecast free cash flow using a constant annual growth assumption."
    )

    with st.form("dcf_form"):

        col1, col2 = st.columns(2)

        with col1:

            current_fcf = st.number_input(
                "Current free cash flow",
                value=10000.0,
                step=1000.0
            )

            growth_pct = st.number_input(
                "Annual growth rate (%)",
                min_value=-99.99,
                max_value=10000.0,
                value=8.0,
                step=0.5
            )

        with col2:

            discount_pct = st.number_input(
                "Discount rate (%)",
                min_value=-99.99,
                max_value=10000.0,
                value=12.0,
                step=0.5
            )

            forecast_years = st.number_input(
                "Forecast years",
                min_value=1,
                max_value=100,
                value=5,
                step=1
            )

        include_terminal = st.checkbox(
            "Include terminal value",
            value=False
        )

        perpetual_growth_pct = st.number_input(
            "Perpetual growth rate (%)",
            min_value=-99.99,
            max_value=10000.0,
            value=2.0,
            step=0.5,
            disabled=not include_terminal
        )

        submitted = st.form_submit_button(
            "Run DCF Valuation",
            type="primary",
            use_container_width=True
        )

    if submitted:

        growth = growth_pct / 100
        discount = discount_pct / 100
        perpetual_growth = perpetual_growth_pct / 100

        if discount <= -1:

            st.error(
                "Discount rate must be greater than -100%."
            )

        elif (
            include_terminal
            and discount <= perpetual_growth
        ):

            st.error(
                "Discount rate must be greater than perpetual "
                "growth for the Gordon Growth terminal value."
            )

        else:

            records = []
            fcf = current_fcf
            total_pv = 0.0

            for year in range(
                1,
                int(forecast_years) + 1
            ):

                fcf = fcf * (1 + growth)

                factor = 1 / ((1 + discount) ** year)

                pv = fcf * factor

                total_pv += pv

                records.append({
                    "Year": year,
                    "Forecast FCF": fcf,
                    "Discount Factor": factor,
                    "Present Value": pv
                })

            df = pd.DataFrame(records)

            st.markdown("### Forecast Results")

            st.dataframe(
                df.style.format({
                    "Forecast FCF": "{:,.2f}",
                    "Discount Factor": "{:.4f}",
                    "Present Value": "{:,.2f}"
                }),
                use_container_width=True,
                hide_index=True
            )

            st.metric(
                "Present Value of Forecast Cash Flows",
                money(total_pv)
            )

            if include_terminal:

                final_fcf = records[-1]["Forecast FCF"]

                next_fcf = (
                    final_fcf * (1 + perpetual_growth)
                )

                terminal_value = (
                    next_fcf
                    / (discount - perpetual_growth)
                )

                pv_terminal = (
                    terminal_value
                    / ((1 + discount) ** int(forecast_years))
                )

                st.metric(
                    "Terminal Value",
                    money(terminal_value)
                )

                st.metric(
                    "Present Value of Terminal Value",
                    money(pv_terminal)
                )

                st.metric(
                    "Total Indicative Enterprise Value",
                    money(total_pv + pv_terminal)
                )

            st.line_chart(
                df.set_index("Year")[[
                    "Forecast FCF",
                    "Present Value"
                ]]
            )

            st.caption(
                "Simplified DCF model. Enterprise value is not the "
                "same as equity value; a full valuation may require "
                "net debt and other adjustments."
            )


# ============================================================
# ARR CALCULATOR
# ============================================================

elif analysis == "ARR Calculator":

    st.subheader("Accounting Rate of Return (ARR)")

    st.write(
        "ARR uses accounting profit, not cash flow. "
        "Enter the accounting profit and investment assumptions."
    )

    with st.form("arr_form"):

        average_profit = st.number_input(
            "Average annual accounting profit",
            value=12000.0,
            step=1000.0
        )

        initial_investment = st.number_input(
            "Initial investment",
            min_value=0.0,
            value=50000.0,
            step=1000.0
        )

        use_residual = st.checkbox(
            "Include residual / salvage value",
            value=False
        )

        residual_value = st.number_input(
            "Residual value",
            min_value=0.0,
            value=0.0,
            step=1000.0,
            disabled=not use_residual
        )

        method = st.selectbox(
            "Investment denominator",
            [
                "Average Investment",
                "Initial Investment"
            ]
        )

        submitted = st.form_submit_button(
            "Calculate ARR",
            type="primary",
            use_container_width=True
        )

    if submitted:

        residual = (
            residual_value if use_residual else 0.0
        )

        if initial_investment <= 0:

            st.error(
                "Initial investment must be greater than zero."
            )

        else:

            if method == "Average Investment":

                denominator = (
                    initial_investment + residual
                ) / 2

            else:

                denominator = initial_investment

            if denominator <= 0:

                st.error(
                    "Investment denominator must be greater than zero."
                )

            else:

                arr = average_profit / denominator

                st.metric(
                    "Accounting Rate of Return",
                    f"{arr * 100:.2f}%"
                )

                st.caption(
                    "ARR methods differ across textbooks and "
                    "organizations. Confirm the method required "
                    "for your analysis."
                )
