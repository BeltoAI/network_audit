from net_audit import NetworkScanner
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os

# Ensure the correct absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_pdf_report(results, client_name, address, isp):
    """Generates a PDF report and ensures all images and tables are included properly."""

    # Get current date for timestamp
    scan_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Ensure belto_reports directory exists on Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    reports_dir = os.path.join(desktop_path, "belto_reports")
    os.makedirs(reports_dir, exist_ok=True)  # Create the folder if it doesn't exist

    # Sanitize file name to remove spaces and special characters
    sanitized_client_name = client_name.replace(" ", "_").replace("/", "-")
    sanitized_address = address.replace(" ", "_").replace("/", "-")

    # Generate the unique PDF file name
    pdf_filename = f"Belto_Report_{sanitized_client_name}_{sanitized_address}_{scan_date}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)

    print(f"📄 Saving report to: {pdf_path}")

    # Set the correct paths for images inside belto_reports
    bell_curve_path = os.path.join(reports_dir, "bell_curve.png")
    image_1_path = os.path.join(reports_dir, "ping-table1.png")
    image_2_path = os.path.join(reports_dir, "ping-table2.png")

    # Copy static images to the reports directory to ensure they exist
    os.system(f"cp {os.path.join(BASE_DIR, 'ping-table1.png')} {image_1_path}")
    os.system(f"cp {os.path.join(BASE_DIR, 'ping-table2.png')} {image_2_path}")

    # Generate Bell Curve Graph and save it in the reports directory
    ping_values = [res["Avg Ping"] for res in results if "Avg Ping" in res]

    if len(ping_values) > 1:
        mean_ping = np.mean(ping_values)
        std_dev_ping = np.std(ping_values)
        x = np.linspace(mean_ping - 3 * std_dev_ping, mean_ping + 3 * std_dev_ping, 100)
        y = (1 / (std_dev_ping * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean_ping) / std_dev_ping) ** 2)

        plt.figure(figsize=(6, 4))
        plt.plot(x, y, color="blue", linewidth=2, label="Ping Distribution")
        plt.axvline(mean_ping, color="red", linestyle="--", label=f"Mean Ping: {mean_ping:.2f} ms")
        plt.fill_between(x, y, alpha=0.3, color="blue")
        plt.xlabel("Ping Time (ms)")
        plt.ylabel("Probability Density")
        plt.title("Bell Curve of Ping Times")
        plt.legend()
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

    # **Introduction Section**
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Report Overview", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, "This report provides an overview of the network scan results, "
                         "including ping statistics and a visual representation of the data distribution.", align="L")
    pdf.ln(5)

    # **Privacy & Disclosure Section**
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Privacy & Data Policy", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 7, "At Belto, we respect your privacy. We do not sell, share, or distribute your data. "
                         "All collected information is strictly used for internal analysis and reporting purposes only.", align="L")
    pdf.ln(10)

    # **Network Scan Results Table**
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, "Network Scan Results", ln=True, align="L")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(30, 10, "IP Address", border=1, align="C")
    pdf.cell(20, 10, "Min", border=1, align="C")
    pdf.cell(20, 10, "Avg", border=1, align="C")
    pdf.cell(20, 10, "Max", border=1, align="C")
    pdf.cell(20, 10, "Range", border=1, align="C")
    pdf.cell(20, 10, "Median", border=1, align="C")
    pdf.cell(30, 10, "Std Dev", border=1, align="C")
    pdf.cell(30, 10, "Variance", border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 10)
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

    # Add Images
    if os.path.exists(bell_curve_path):
        pdf.ln(10)
        pdf.cell(200, 10, "Ping Time Distribution", ln=True, align="C")
        pdf.ln(5)
        pdf.image(bell_curve_path, x=30, w=150)

    if os.path.exists(image_1_path):
        pdf.ln(10)
        pdf.cell(200, 10, "Ping Speed Comparison Table", ln=True, align="C")
        pdf.ln(5)
        pdf.image(image_1_path, x=30, w=150)

    if os.path.exists(image_2_path):
        pdf.ln(10)
        pdf.cell(200, 10, "Device Ping Expectancy", ln=True, align="C")
        pdf.ln(5)
        pdf.image(image_2_path, x=30, w=150)

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
