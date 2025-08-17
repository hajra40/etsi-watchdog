from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from datetime import datetime
import os

def generate_drift_pdf(results, output_path="drift_summary.pdf"):
    """
    Generate a PDF report of drift detection results.

    Parameters
    ----------
    results : dict
        Dictionary mapping feature name -> DriftResult object.
    output_path : str, optional
        Path to save the generated PDF.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []

    # Title
    story.append(Paragraph("<b>ETSI Watchdog Drift Summary Report</b>", style=None))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", style=None))
    story.append(Spacer(1, 12))

    # Table data
    data = [["Feature", "Method", "Score", "Threshold", "KS Stat", "P-Value", "Flagged Drift"]]
    for feat, res in results.items():
        details = res.details
        flagged = "Yes" if res.score > res.threshold else "No"
        data.append([
            feat, res.method, round(res.score, 3), res.threshold,
            round(details.get("ks_statistic", 0), 3),
            round(details.get("p_value", 0), 4),
            flagged
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 24))

    # Optional: Save plots for each feature and add them to the PDF
    for feat, res in results.items():
        try:
            plot_path = f"{feat}_drift_plot.png"
            res.plot(save_path=plot_path)  # Assuming your DriftResult has .plot()
            story.append(Paragraph(f"<b>{feat}</b>", style=None))
            story.append(Image(plot_path, width=400, height=300))
            story.append(Spacer(1, 12))
        except Exception as e:
            print(f"Could not generate plot for {feat}: {e}")

    doc.build(story)
    print(f"✅ Drift summary PDF saved to: {os.path.abspath(output_path)}")
