from net_audit import NetworkScanner
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import datetime

# Define the output PDF path
pdf_path = "network_audit_report.pdf"

# Placeholder image paths (Replace these with actual image paths)
image_1_path = "ping-table1.png"  # Replace with actual path
image_2_path = "ping-table2.png"  # Replace with actual path

def generate_pdf_report(results, client_name, address, isp):
    """Generates a PDF report from the network scan results and includes extra images."""

    # Get the current date
    scan_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract ping values for the bell curve
    ping_values = [res["Avg Ping"] for res in results if "Avg Ping" in res]

    if len(ping_values) > 1:
        mean_ping = np.mean(ping_values)
        std_dev_ping = np.std(ping_values)
        x = np.linspace(mean_ping - 3 * std_dev_ping, mean_ping + 3 * std_dev_ping, 100)
        y = (1 / (std_dev_ping * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean_ping) / std_dev_ping) ** 2)

        # Generate the Bell Curve Graph
        plt.figure(figsize=(6, 4))
        plt.plot(x, y, color="blue", linewidth=2, label="Ping Distribution")
        plt.axvline(mean_ping, color="red", linestyle="--", label=f"Mean Ping: {mean_ping:.2f} ms")
        plt.fill_between(x, y, alpha=0.3, color="blue")
        plt.xlabel("Ping Time (ms)")
        plt.ylabel("Probability Density")
        plt.title("Bell Curve of Ping Times")
        plt.legend()
        bell_curve_path = "bell_curve.png"
        plt.savefig(bell_curve_path)
        plt.close()
    else:
        bell_curve_path = None

    # Create the PDF Report
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Company Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Belto - Network Audit Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "I", 12)
    pdf.cell(200, 10, "Website: beltoss.world | Email: info@beltoss.com | Phone: 559-579-9487", ln=True, align="C")
    pdf.ln(10)

    # Date of Scan
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, f"Date of Scan: {scan_date}", ln=True, align="C")
    pdf.ln(10)

    # Client Information
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Client Information:", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Client Name: {client_name}", ln=True, align="L")
    pdf.cell(200, 10, f"Address: {address}", ln=True, align="L")
    pdf.cell(200, 10, f"Internet Service Provider: {isp}", ln=True, align="L")
    pdf.ln(10)

    # Introduction Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Report Overview", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, "This report provides an overview of the network scan results, "
                         "including ping statistics and a visual representation of the data distribution.", align="L")
    pdf.ln(5)

    # Privacy & Disclosure Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Privacy & Data Policy", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, "At Belto, we respect your privacy. We do not sell, share, or distribute your data. "
                         "All collected information is strictly used for internal analysis and reporting purposes only.", align="L")
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(30, 10, "IP Address", border=1, align="C")
    pdf.cell(20, 10, "Min", border=1, align="C")
    pdf.cell(20, 10, "Avg", border=1, align="C")
    pdf.cell(20, 10, "Max", border=1, align="C")
    pdf.cell(20, 10, "Range", border=1, align="C")
    pdf.cell(20, 10, "Median", border=1, align="C")
    pdf.cell(30, 10, "Std Dev", border=1, align="C")
    pdf.cell(30, 10, "Variance", border=1, align="C")
    pdf.ln()

    # Insert Dynamic Data from Scan Results
    pdf.set_font("Arial", "", 12)
    for res in results:
        pdf.cell(30, 10, res["IP"], border=1, align="C")
        pdf.cell(20, 10, f"{res['Min Ping']:.2f} ms", border=1, align="C")
        pdf.cell(20, 10, f"{res['Avg Ping']:.2f} ms", border=1, align="C")
        pdf.cell(20, 10, f"{res['Max Ping']:.2f} ms", border=1, align="C")
        pdf.cell(20, 10, f"{res['Range']:.2f} ms", border=1, align="C")
        pdf.cell(20, 10, f"{res['Median Ping']:.2f} ms", border=1, align="C")
        pdf.cell(30, 10, f"{res['Std Dev Ping']:.2f} ms", border=1, align="C")
        pdf.cell(30, 10, f"{res['Variance Ping']:.2f} ms", border=1, align="C")
        pdf.ln()

    pdf.ln(10)

    # Add Bell Curve Image Dynamically
    if bell_curve_path:
        pdf.cell(200, 10, "Ping Time Distribution", ln=True, align="C")
        pdf.ln(5)
        pdf.image(bell_curve_path, x=30, w=150)

    # Add Placeholder Images
    if image_1_path:
        pdf.ln(10)
        pdf.cell(200, 10, "Ping Speed Comparison Table", ln=True, align="C")
        pdf.ln(5)
        pdf.image(image_1_path, x=30, w=150)

    if image_2_path:
        pdf.ln(10)
        pdf.cell(200, 10, "Device Ping Expectnacy", ln=True, align="C")
        pdf.ln(5)
        pdf.image(image_2_path, x=30, w=150)

    # Save PDF
    pdf.output(pdf_path)
    return pdf_path

def main():
    """Runs the network scan and generates a PDF report with user-provided details."""
    client_name = input("Enter Client Name: ")
    address = input("Enter Address: ")
    isp = input("Enter Internet Service Provider: ")

    print("🔍 Running network scan...")
    scanner = NetworkScanner()
    results = scanner.run_scan()

    print("📄 Generating PDF report...")
    pdf_path = generate_pdf_report(results, client_name, address, isp)

    print(f"✅ PDF report generated successfully: {pdf_path}")

if __name__ == "__main__":
    main()
