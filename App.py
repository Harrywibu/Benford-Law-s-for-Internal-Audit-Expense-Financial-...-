import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from scipy.stats import chisquare, ttest_1samp

st.set_page_config(page_title="Benford's Law Audit Tool", layout="wide")
st.title("📊 Benford's Law Analysis Tool")

# Upload file
uploaded_file = st.file_uploader("Upload your data file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Read file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

    st.subheader("📋 Preview of Uploaded Data")
    st.dataframe(df.head(), height=300)
    st.markdown(f"**Total rows in dataset:** {len(df)}")

    # Select numeric column
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if not numeric_cols:
        st.error("No numeric columns found.")
    else:
        selected_col = st.selectbox("Select the numeric column to test with Benford's Law", numeric_cols)

        raw_values = df[selected_col]
        total_rows = len(raw_values)
        nan_rows = df[df[selected_col].isna()]
        nan_count = raw_values.isna().sum()
        zero_count = (raw_values == 0).sum()
        valid_values = raw_values.dropna()
        valid_values = valid_values[valid_values != 0]
        valid_count = len(valid_values)

        # Data Validation Summary
        st.subheader("Data Validation Information ")

        st.markdown(f"""
        **Total rows in selected column:** {total_rows}  
        **NaN values:** {nan_count}  
        **Zero values:** {zero_count}  
        **Valid rows used for analysis:** {valid_count}
        """)

        if nan_count > 0:
            st.subheader("🔍 Rows with NaN Values")
            st.dataframe(nan_rows)

        # Extract first digit and first two digits
        first_digits = []
        first_two_digits = []
        for x in valid_values:
            try:
                abs_x = abs(float(x))
                str_x = str(int(abs_x))
                first_digit = int(str_x[0])
                first_digits.append(first_digit)
                if len(str_x) >= 2:
                    first_two = int(str_x[:2])
                    first_two_digits.append(first_two)
            except (ValueError, TypeError):
                continue

        # First Digit Analysis
        actual_counts_fd = Counter(first_digits)
        total_fd = sum(actual_counts_fd.values())
        actual_dist_fd = {d: actual_counts_fd.get(d, 0) / total_fd for d in range(1, 10)}
        benford_dist_fd = {d: np.log10(1 + 1/d) for d in range(1, 10)}
        variance_fd = {d: (actual_dist_fd.get(d, 0) - benford_dist_fd[d]) * 100 for d in range(1, 10)}
        chi_test_fd = np.mean([abs(actual_dist_fd.get(d, 0)*100 - benford_dist_fd[d]*100) for d in range(1, 10)])

        dist_df_fd = pd.DataFrame({
            'Digit': list(range(1, 10)),
            'Actual %': [actual_dist_fd.get(d, 0)*100 for d in range(1, 10)],
            'Benford %': [benford_dist_fd[d]*100 for d in range(1, 10)],
            'Variance %': [variance_fd[d] for d in range(1, 10)]
        })

        # First Two Digit Analysis
        actual_counts_ftd = Counter(first_two_digits)
        total_ftd = sum(actual_counts_ftd.values())
        benford_dist_ftd = {d: np.log10(1 + 1/d) for d in range(10, 100)}
        actual_dist_ftd = {d: actual_counts_ftd.get(d, 0) / total_ftd for d in range(10, 100)}
        variance_ftd = {d: (actual_dist_ftd.get(d, 0) - benford_dist_ftd.get(d, 0)) * 100 for d in range(10, 100)}
        chi_test_ftd = np.mean([abs(actual_dist_ftd.get(d, 0)*100 - benford_dist_ftd[d]*100) for d in range(10, 100)])

        dist_df_ftd = pd.DataFrame({
            'Digit': list(range(10, 100)),
            'Actual %': [actual_dist_ftd.get(d, 0)*100 for d in range(10, 100)],
            'Benford %': [benford_dist_ftd[d]*100 for d in range(10, 100)],
            'Variance %': [variance_ftd[d] for d in range(10, 100)]
        })

        col1, col2 = st.columns(2)

        # First Digit Column
        with col1:
            st.subheader("🔢 First Digit Analysis")
            st.markdown(f"**Total rows used in First Digit analysis:** {total_fd}")
            st.dataframe(dist_df_fd.style.format("{:.2f}"), height=300)

            st.subheader("📊 First Digit Bar Chart")
            fig1, ax1 = plt.subplots(figsize=(8, 4))
            ax1.bar(dist_df_fd['Digit'], dist_df_fd['Actual %'], label="Actual %", alpha=0.7)
            ax1.plot(dist_df_fd['Digit'], dist_df_fd['Benford %'], 'r--', label="Benford %", linewidth=2)
            ax1.set_xlabel("First Digit")
            ax1.set_ylabel("Percentage")
            ax1.set_title("First Digit Distribution")
            ax1.legend()
            ax1.grid(True)
            st.pyplot(fig1)

            observed_fd = [actual_counts_fd.get(d, 0) for d in range(1, 10)]
            expected_fd = [benford_dist_fd[d] * total_fd for d in range(1, 10)]
            chi2_fd, p_fd = chisquare(f_obs=observed_fd, f_exp=expected_fd)
            t_fd, pval_fd = ttest_1samp([actual_dist_fd.get(d, 0)*100 for d in range(1, 10)],
                                        np.mean([benford_dist_fd[d]*100 for d in range(1, 10)]))

            st.subheader("🧪 First Digit Statistical Test")
            st.markdown(f"""
            **Chi-squared statistic**: `{chi2_fd:.2f}` ▸ Critical value (df=8, α=0.05): `15.51`  
            **p-value**: `{p_fd:.4f}` ▸ If ≤ 0.05 → significant deviation  
            **T-test statistic**: `{t_fd:.2f}` ▸ If |t| > 2 → deviation in mean %  
            **T-test p-value**: `{pval_fd:.4f}` ▸ If ≤ 0.05 → statistically significant  
            **Chi-test comparison (avg % deviation)**: `{chi_test_fd:.2f}%` ▸ < 1% → good fit; > 5% → anomaly
            """)

            st.subheader("📉 Risk Assessment")
            if p_fd <= 0.05:
                st.warning("⚠️ Chi-squared test indicates significant deviation from Benford's Law.")
            else:
                st.success("✅ Chi-squared test suggests data conforms to Benford's Law.")

            if abs(t_fd) > 2:
                st.warning("⚠️ T-test shows deviation in average percentage distribution.")
            else:
                st.success("✅ T-test shows no significant deviation in average percentage.")

            if chi_test_fd > 5:
                st.warning("⚠️ Average deviation exceeds 5%, possible localized anomalies.")
            elif chi_test_fd < 1:
                st.success("✅ Average deviation < 1%, data fits Benford's Law well.")

            st.subheader("📝 Audit Recommendation")
            st.markdown("""
            - Review transactions with first digits showing high variance.
            - Consider segmenting data by time, department, or transaction type.
            - Validate suspicious entries with source documents or system logs.
            """)

            if any(abs(v) > 5 for v in variance_fd.values()):
                st.subheader("📦 First Digit Variance Boxplot")
                fig_fd_box, ax_fd_box = plt.subplots(figsize=(8, 2))
                ax_fd_box.boxplot(list(variance_fd.values()))
                ax_fd_box.set_title("First Digit Variance %")
                ax_fd_box.set_ylabel("Variance %")
                st.pyplot(fig_fd_box)

            suspicious_digits = [d for d, v in variance_fd.items() if abs(v) > 5]
            suspicious_info = [f"[{d}]: {variance_fd[d]:.2f}%" for d in suspicious_digits]
            st.warning(f"⚠️ Suspicious first digits (variance > ±5%): {', '.join(suspicious_info)}")

            st.subheader("🔍 Transactions with Suspicious First Digits")
            def extract_first_digit_safe(value):
                try:
                    abs_val = abs(float(value))
                    return int(str(int(abs_val))[0])
                except:
                    return None

            df['first_digit'] = df[selected_col].apply(extract_first_digit_safe)
            suspicious_rows_fd = df[df['first_digit'].isin(suspicious_digits)]
            
            st.markdown(f"**Total suspicious rows:** {len(suspicious_rows_fd)} ({len(suspicious_rows_fd)/total_rows*100:.2f}%)")

            if not suspicious_rows_fd.empty:
                min_val = suspicious_rows_fd[selected_col].min()
                max_val = suspicious_rows_fd[selected_col].max()
                st.markdown(f"**Suspicious value range:** {min_val:,.2f} to {max_val:,.2f}")
                value_range = st.slider("Filter suspicious value range", float(min_val), float(max_val), (float(min_val), float(max_val)),key="slider_fd")
                filtered_rows_fd = suspicious_rows_fd[(suspicious_rows_fd[selected_col] >= value_range[0]) & (suspicious_rows_fd[selected_col] <= value_range[1])]
                st.dataframe(filtered_rows_fd)
            else:
                st.info("No suspicious transactions found for First Digit.")

    
if min_val != max_val:
    value_range = st.slider("Filter suspicious value range", float(min_val), float(max_val), (float(min_val), float(max_val)), key="slider_fd")
    filtered_rows_fd = suspicious_rows_fd[(suspicious_rows_fd[selected_col] >= value_range[0]) & (suspicious_rows_fd[selected_col] <= value_range[1])]
    st.dataframe(filtered_rows_fd)
        else:
    st.info("Suspicious value range is a single value. No slider needed.")
    st.dataframe(suspicious_rows_fd)

                filtered_rows_fd = suspicious_rows_fd[(suspicious_rows_fd[selected_col] >= value_range[0]) & (suspicious_rows_fd[selected_col] <= value_range[1])]
                st.dataframe(filtered_rows_fd)
        else:
                st.info("No suspicious transactions found for First Digit.")
                
        # First Two Digit Column
        with col2:
            st.subheader("🔢 First Two Digit Analysis")
            st.markdown(f"**Total rows used in First Two Digit analysis:** {total_ftd}")
            st.dataframe(dist_df_ftd.style.format("{:.2f}"), height=300)

            st.subheader("📊 First Two Digit Bar Chart")
            fig2, ax2 = plt.subplots(figsize=(8, 4))
            ax2.bar(dist_df_ftd['Digit'], dist_df_ftd['Actual %'], label="Actual %", alpha=0.7)
            ax2.plot(dist_df_ftd['Digit'], dist_df_ftd['Benford %'], 'r--', label="Benford %", linewidth=1)
            ax2.set_xlabel("First Two Digits")
            ax2.set_ylabel("Percentage")
            ax2.set_title("First Two Digit Distribution")
            ax2.legend()
            ax2.grid(True)
            st.pyplot(fig2)

            observed_ftd = [actual_counts_ftd.get(d, 0) for d in range(10, 100)]
            expected_ftd = [benford_dist_ftd[d] * total_ftd for d in range(10, 100)]
            chi2_ftd, p_ftd = chisquare(f_obs=observed_ftd, f_exp=expected_ftd)
            t_ftd, pval_ftd = ttest_1samp([actual_dist_ftd.get(d, 0)*100 for d in range(10, 100)],
                                          np.mean([benford_dist_ftd[d]*100 for d in range(10, 100)]))

            st.subheader("🧪 First Two Digit Statistical Test")
            st.markdown(f"""
            **Chi-squared statistic**: `{chi2_ftd:.2f}` ▸ Critical value (df=89, α=0.05): `112.02`  
            **p-value**: `{p_ftd:.4f}` ▸ If ≤ 0.05 → significant deviation  
            **T-test statistic**: `{t_ftd:.2f}` ▸ If |t| > 2 → deviation in mean %  
            **T-test p-value**: `{pval_ftd:.4f}` ▸ If ≤ 0.05 → statistically significant  
            **Chi-test comparison (avg % deviation)**: `{chi_test_ftd:.2f}%` ▸ < 1% → good fit; > 5% → anomaly
            """)

            st.subheader("📉 Risk Assessment")
            if p_ftd <= 0.05:
                st.warning("⚠️ Chi-squared test indicates significant deviation from Benford's Law.")
            else:
                st.success("✅ Chi-squared test suggests data conforms to Benford's Law.")

            if abs(t_ftd) > 2:
                st.warning("⚠️ T-test shows deviation in average percentage distribution.")
            else:
                st.success("✅ T-test shows no significant deviation in average percentage.")

            if chi_test_ftd > 5:
                st.warning("⚠️ Average deviation exceeds 5%, possible localized anomalies.")
            elif chi_test_ftd < 1:
                st.success("✅ Average deviation < 1%, data fits Benford's Law well.")

            st.subheader("📝 Audit Recommendation")
            st.markdown("""
            - Review transactions with first two digits showing high variance.
            - Consider segmenting data by time, department, or transaction type.
            - Validate suspicious entries with source documents or system logs.
            """)

            if any(abs(v) > 5 for v in variance_ftd.values()):
                st.subheader("📦 First Two Digit Variance Boxplot")
                fig_ftd_box, ax_ftd_box = plt.subplots(figsize=(8, 2))
                ax_ftd_box.boxplot(list(variance_ftd.values()))
                ax_ftd_box.set_title("First Two Digit Variance %")
                ax_ftd_box.set_ylabel("Variance %")
                st.pyplot(fig_ftd_box)

            suspicious_digits_ftd = [d for d, v in variance_ftd.items() if abs(v) > 5]
            suspicious_info_ftd = [f"[{d}]: {variance_ftd[d]:.2f}%" for d in suspicious_digits_ftd]
            st.warning(f"⚠️ Suspicious first two digits (variance > ±5%): {', '.join(suspicious_info_ftd)}")

            st.subheader("🔍 Transactions with Suspicious First Two Digits")
            def extract_first_two_digits_safe(value):
                try:
                    abs_val = abs(float(value))
                    str_val = str(int(abs_val))
                    if len(str_val) >= 2:
                        return int(str_val[:2])
                    elif len(str_val) == 1:
                        return int(str_val)
                except:
                    return None

            df['first_two_digits'] = df[selected_col].apply(extract_first_two_digits_safe)
            suspicious_rows_ftd = df[df['first_two_digits'].isin(suspicious_digits_ftd)]
            
            
            st.markdown(f"**Total suspicious rows:** {len(suspicious_rows_ftd)} ({len(suspicious_rows_ftd)/total_rows*100:.2f}%)")
            
            if not suspicious_rows_ftd.empty:
                min_val_ftd = suspicious_rows_ftd[selected_col].min()
                max_val_ftd = suspicious_rows_ftd[selected_col].max()
                st.markdown(f"**Suspicious value range:** {min_val:,.2f} to {max_val:,.2f}")
                value_range_ftd = st.slider("Filter suspicious value range", float(min_val_ftd), float(max_val_ftd), (float(min_val_ftd), float(max_val_ftd)),key="slider_ftd")
                filtered_rows_ftd = suspicious_rows_ftd[(suspicious_rows_ftd[selected_col] >= value_range_ftd[0]) & (suspicious_rows_ftd[selected_col] <= value_range_ftd[1])]
                st.dataframe(filtered_rows_ftd)
            else:
                st.info("No suspicious transactions found for First Two Digit.")

