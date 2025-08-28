import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# File path
EXCEL_FILE = "farm_data.xlsx"

# Initialize file with proper schema (removed Category from Classification)
if not os.path.exists(EXCEL_FILE):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl") as writer:
        pd.DataFrame(columns=["Tag", "Amount", "Date"]).to_excel(writer, sheet_name="Revenue", index=False)
        pd.DataFrame(columns=["Tag", "Amount", "Date"]).to_excel(writer, sheet_name="Expenditure", index=False)
        pd.DataFrame(columns=["Name", "Gender", "Breed", "New Borns",
                              "Weight", "Dead Count", "Vaccination Date", "Details", "Date"]).to_excel(writer, sheet_name="Classification", index=False)


def load_data(sheet_name):
    return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)


def save_data(df, sheet_name):
    with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)


def add_record(sheet_name, record):
    df = load_data(sheet_name)
    df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    save_data(df, sheet_name)


def delete_record(sheet_name, index):
    df = load_data(sheet_name)
    df = df.drop(index).reset_index(drop=True)
    save_data(df, sheet_name)


def edit_record(sheet_name, index, updated_record):
    df = load_data(sheet_name)
    df.loc[index] = updated_record
    save_data(df, sheet_name)


def calculate_profit_loss():
    """Calculate total profit or loss"""
    try:
        df_revenue = load_data("Revenue")
        df_expenditure = load_data("Expenditure")
        
        total_revenue = df_revenue["Amount"].sum() if not df_revenue.empty else 0
        total_expenditure = df_expenditure["Amount"].sum() if not df_expenditure.empty else 0
        
        return total_revenue - total_expenditure, total_revenue, total_expenditure
    except:
        return 0, 0, 0


def filter_data_by_date(df, start_date, end_date):
    """Filter dataframe by date range"""
    if df.empty:
        return df
    
    df['Date_parsed'] = pd.to_datetime(df['Date'], format='%Y-%m-%d %H:%M:%S').dt.date
    filtered_df = df[(df['Date_parsed'] >= start_date) & (df['Date_parsed'] <= end_date)]
    return filtered_df.drop('Date_parsed', axis=1)


def create_pdf_report(report_type, start_date, end_date):
    """Generate PDF report with proper formatting"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Farm Report - {report_type}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Date range
    date_range = Paragraph(f"Period: {start_date} to {end_date}", styles['Normal'])
    story.append(date_range)
    story.append(Spacer(1, 20))
    
    # Summary
    profit_loss, total_revenue, total_expenditure = calculate_profit_loss()
    summary = Paragraph(f"<b>Financial Summary:</b><br/>Total Revenue: ₹{total_revenue:,.2f}<br/>Total Expenditure: ₹{total_expenditure:,.2f}<br/>Profit/Loss: ₹{profit_loss:,.2f}", styles['Normal'])
    story.append(summary)
    story.append(Spacer(1, 30))
    
    if report_type in ["Revenue", "All"]:
        # Revenue section
        revenue_title = Paragraph("Revenue Records", styles['Heading2'])
        story.append(revenue_title)
        story.append(Spacer(1, 10))
        
        df_revenue = load_data("Revenue")
        filtered_revenue = filter_data_by_date(df_revenue, start_date, end_date)
        
        if not filtered_revenue.empty:
            revenue_data = [['Name', 'Amount (₹)', 'Date']]
            for _, row in filtered_revenue.iterrows():
                revenue_data.append([row['Tag'], f"{row['Amount']:,.2f}", row['Date']])
            
            revenue_table = Table(revenue_data)
            revenue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(revenue_table)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("No revenue records found for this period.", styles['Normal']))
            story.append(Spacer(1, 20))
    
    if report_type in ["Expenditure", "All"]:
        # Expenditure section
        expenditure_title = Paragraph("Expenditure Records", styles['Heading2'])
        story.append(expenditure_title)
        story.append(Spacer(1, 10))
        
        df_expenditure = load_data("Expenditure")
        filtered_expenditure = filter_data_by_date(df_expenditure, start_date, end_date)
        
        if not filtered_expenditure.empty:
            expenditure_data = [['Name', 'Amount (₹)', 'Date']]
            for _, row in filtered_expenditure.iterrows():
                expenditure_data.append([row['Tag'], f"{row['Amount']:,.2f}", row['Date']])
            
            expenditure_table = Table(expenditure_data)
            expenditure_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(expenditure_table)
            story.append(Spacer(1, 20))
        else:
            story.append(Paragraph("No expenditure records found for this period.", styles['Normal']))
            story.append(Spacer(1, 20))
    
    if report_type in ["Classification", "All"]:
        # Classification section
        classification_title = Paragraph("Classification Records", styles['Heading2'])
        story.append(classification_title)
        story.append(Spacer(1, 10))
        
        df_classification = load_data("Classification")
        filtered_classification = filter_data_by_date(df_classification, start_date, end_date)
        
        if not filtered_classification.empty:
            classification_data = [['Name', 'Gender', 'Breed', 'Weight (kg)', 'New Borns', 'Dead Count', 'Vaccination Date']]
            for _, row in filtered_classification.iterrows():
                classification_data.append([
                    row['Name'], row['Gender'], row['Breed'], 
                    f"{row['Weight']}", f"{row['New Borns']}", 
                    f"{row['Dead Count']}", row['Vaccination Date']
                ])
            
            classification_table = Table(classification_data)
            classification_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(classification_table)
        else:
            story.append(Paragraph("No classification records found for this period.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# ----------- Streamlit UI -----------
st.title("Farm Dashboard")

# ---------------- Profit/Loss Display -----------------
profit_loss, total_revenue, total_expenditure = calculate_profit_loss()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
with col2:
    st.metric("Total Expenditure", f"₹{total_expenditure:,.2f}")
with col3:
    if profit_loss >= 0:
        st.markdown(f"<h3 style='color: green;'>Profit: ₹{profit_loss:,.2f} 📈</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 style='color: red;'>Loss: ₹{abs(profit_loss):,.2f} 📉</h3>", unsafe_allow_html=True)

st.divider()

# Initialize session state for editing
if 'editing' not in st.session_state:
    st.session_state.editing = {'sheet': None, 'index': None}


# ---------------- Revenue -----------------
st.header("💰 Revenue")

# Add revenue form
with st.form("add_revenue"):
    tag = st.text_input("Name")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f", step=1.0)
    submitted = st.form_submit_button("➕ Add Revenue")
    if submitted and tag:
        add_record("Revenue", {"Tag": tag, "Amount": amount, "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.success("Revenue added!")
        st.rerun()

# Display revenue data with edit/delete functionality
df_revenue = load_data("Revenue")

if not df_revenue.empty:
    st.subheader("Revenue Records")
    for i, row in df_revenue.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['Tag']}**")
        with col2:
            st.write(f"₹{row['Amount']:,.2f}")
        with col3:
            st.write(row['Date'])
        with col4:
            if st.button("✏️", key=f"edit_revenue_{i}", help="Edit"):
                st.session_state.editing = {'sheet': 'Revenue', 'index': i}
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"delete_revenue_{i}", help="Delete"):
                delete_record("Revenue", i)
                st.success("Record deleted!")
                st.rerun()

    # Edit form for revenue
    if st.session_state.editing['sheet'] == 'Revenue' and st.session_state.editing['index'] is not None:
        st.subheader("Edit Revenue Record")
        edit_index = st.session_state.editing['index']
        if edit_index < len(df_revenue):
            current_record = df_revenue.iloc[edit_index]
            
            with st.form("edit_revenue_form"):
                new_tag = st.text_input("Name", value=current_record['Tag'])
                new_amount = st.number_input("Amount", min_value=0.0, value=float(current_record['Amount']), format="%.2f", step=1.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        edit_record("Revenue", edit_index, {
                            "Tag": new_tag, 
                            "Amount": new_amount, 
                            "Date": current_record['Date']
                        })
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.success("Record updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.rerun()
else:
    st.info("No revenue records found.")


# ---------------- Expenditure -----------------
st.header("📉 Expenditure")

# Add expenditure form
with st.form("add_expenditure"):
    tag = st.text_input("Name")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f", step=1.0)
    submitted = st.form_submit_button("➕ Add Expenditure")
    if submitted and tag:
        add_record("Expenditure", {"Tag": tag, "Amount": amount, "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        st.success("Expenditure added!")
        st.rerun()

# Display expenditure data with edit/delete functionality
df_expenditure = load_data("Expenditure")

if not df_expenditure.empty:
    st.subheader("Expenditure Records")
    for i, row in df_expenditure.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 2, 1, 1])
        
        with col1:
            st.write(f"**{row['Tag']}**")
        with col2:
            st.write(f"₹{row['Amount']:,.2f}")
        with col3:
            st.write(row['Date'])
        with col4:
            if st.button("✏️", key=f"edit_expenditure_{i}", help="Edit"):
                st.session_state.editing = {'sheet': 'Expenditure', 'index': i}
                st.rerun()
        with col5:
            if st.button("🗑️", key=f"delete_expenditure_{i}", help="Delete"):
                delete_record("Expenditure", i)
                st.success("Record deleted!")
                st.rerun()

    # Edit form for expenditure
    if st.session_state.editing['sheet'] == 'Expenditure' and st.session_state.editing['index'] is not None:
        st.subheader("Edit Expenditure Record")
        edit_index = st.session_state.editing['index']
        if edit_index < len(df_expenditure):
            current_record = df_expenditure.iloc[edit_index]
            
            with st.form("edit_expenditure_form"):
                new_tag = st.text_input("Name", value=current_record['Tag'])
                new_amount = st.number_input("Amount", min_value=0.0, value=float(current_record['Amount']), format="%.2f", step=1.0)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        edit_record("Expenditure", edit_index, {
                            "Tag": new_tag, 
                            "Amount": new_amount, 
                            "Date": current_record['Date']
                        })
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.success("Record updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.rerun()
else:
    st.info("No expenditure records found.")


# ---------------- Classification -----------------
st.header(" Classification")

# Add classification form (removed Category field)
with st.form("add_classification"):
    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female", "Unknown"])
    breed = st.text_input("Breed")
    new_borns = st.number_input("New Borns", min_value=0, step=1, format="%d")
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, format="%.1f")
    dead_count = st.number_input("Dead Count", min_value=0, step=1, format="%d")
    vaccination_date = st.date_input("Vaccination Date")
    details = st.text_area("Details")
    submitted = st.form_submit_button("➕ Add Classification")
    if submitted and name:
        add_record("Classification", {
            "Name": name,
            "Gender": gender,
            "Breed": breed,
            "New Borns": new_borns,
            "Weight": weight,
            "Dead Count": dead_count,
            "Vaccination Date": vaccination_date.strftime("%Y-%m-%d"),
            "Details": details,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success("Classification added!")
        st.rerun()

# Display classification data with edit/delete functionality
df_classification = load_data("Classification")

if not df_classification.empty:
    st.subheader("Classification Records")
    for i, row in df_classification.iterrows():
        with st.expander(f"{row['Name']} ({row['Gender']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Breed:** {row['Breed']}")
                st.write(f"**Weight:** {row['Weight']} kg")
                st.write(f"**New Borns:** {row['New Borns']}")
                st.write(f"**Dead Count:** {row['Dead Count']}")
            with col2:
                st.write(f"**Vaccination Date:** {row['Vaccination Date']}")
                st.write(f"**Added On:** {row['Date']}")
                if row['Details']:
                    st.write(f"**Details:** {row['Details']}")
            
            col3, col4 = st.columns(2)
            with col3:
                if st.button("✏️ Edit", key=f"edit_classification_{i}"):
                    st.session_state.editing = {'sheet': 'Classification', 'index': i}
                    st.rerun()
            with col4:
                if st.button("🗑️ Delete", key=f"delete_classification_{i}"):
                    delete_record("Classification", i)
                    st.success("Record deleted!")
                    st.rerun()

    # Edit form for classification
    if st.session_state.editing['sheet'] == 'Classification' and st.session_state.editing['index'] is not None:
        st.subheader("Edit Classification Record")
        edit_index = st.session_state.editing['index']
        if edit_index < len(df_classification):
            current_record = df_classification.iloc[edit_index]
            
            with st.form("edit_classification_form"):
                new_name = st.text_input("Name", value=current_record['Name'])
                new_gender = st.selectbox("Gender", ["Male", "Female", "Unknown"], 
                                        index=["Male", "Female", "Unknown"].index(current_record['Gender']))
                new_breed = st.text_input("Breed", value=current_record['Breed'])
                new_new_borns = st.number_input("New Borns", min_value=0, step=1, value=int(current_record['New Borns']), format="%d")
                new_weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1, value=float(current_record['Weight']), format="%.1f")
                new_dead_count = st.number_input("Dead Count", min_value=0, step=1, value=int(current_record['Dead Count']), format="%d")
                new_vaccination_date = st.date_input("Vaccination Date", value=pd.to_datetime(current_record['Vaccination Date']).date())
                new_details = st.text_area("Details", value=current_record['Details'] if pd.notna(current_record['Details']) else "")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 Save Changes"):
                        edit_record("Classification", edit_index, {
                            "Name": new_name,
                            "Gender": new_gender,
                            "Breed": new_breed,
                            "New Borns": new_new_borns,
                            "Weight": new_weight,
                            "Dead Count": new_dead_count,
                            "Vaccination Date": new_vaccination_date.strftime("%Y-%m-%d"),
                            "Details": new_details,
                            "Date": current_record['Date']
                        })
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.success("Record updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("❌ Cancel"):
                        st.session_state.editing = {'sheet': None, 'index': None}
                        st.rerun()
else:
    st.info("No classification records found.")


# ---------------- Reports -----------------
st.header("📑 Reports")

# Date filter for reports
col1, col2, col3 = st.columns(3)
with col1:
    start_date = st.date_input("Start Date", value=date.today().replace(day=1))
with col2:
    end_date = st.date_input("End Date", value=date.today())
with col3:
    report_type = st.selectbox("Select Report Type", ["Revenue", "Expenditure", "Classification", "All"])

if start_date > end_date:
    st.error("Start date must be before end date!")
else:
    if st.button("Generate Report"):
        with st.spinner("Generating PDF report..."):
            pdf_buffer = create_pdf_report(report_type, start_date, end_date)
            
            st.download_button(
                label="⬇️ Download Report",
                data=pdf_buffer,
                file_name=f"{report_type}_report_{start_date}_to_{end_date}.pdf",
                mime="application/pdf",
            )
            st.success("Report generated successfully!")