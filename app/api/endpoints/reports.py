import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from fpdf import FPDF
from app.api import deps
from app.models.analysis import Analysis
from app.models.user import User

router = APIRouter()

class PDFReport(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(15, 23, 42) # Lumine primary navy
        self.cell(0, 10, 'Lumine AI - Skin Analysis Report', new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        disclaimer = "Disclaimer: Lumine AI provides informational insights only. This is not a medical diagnosis. Please consult a certified dermatologist."
        self.cell(0, 10, disclaimer, align='C')

@router.get("/{analysis_id}/pdf")
def generate_pdf_report(
    analysis_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found or unauthorized")

    pdf = PDFReport()
    pdf.add_page()
    
    # Body font
    pdf.set_font('helvetica', '', 12)
    pdf.set_text_color(0, 0, 0)
    
    # Metadata
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(50, 10, "Date of Analysis:")
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 10, analysis.timestamp.strftime("%Y-%m-%d %H:%M"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # Prediction
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "Visual Match", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 12)
    prediction_text = f"Condition: {analysis.predicted_class or 'Unknown'} (Confidence: {analysis.confidence}%)"
    pdf.cell(0, 10, prediction_text, new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(5)
    
    # Text symptom
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "Symptom Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 12)
    pdf.multi_cell(0, 8, f"Detected: {analysis.text_condition}")
    
    pdf.ln(5)
    
    # AI Insight
    if analysis.ai_summary:
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(59, 130, 246) # Blue
        pdf.cell(0, 10, "Lumine AI Insight", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 12)
        pdf.set_text_color(0, 0, 0)
        # multi_cell handles line breaks automatically
        pdf.multi_cell(0, 8, analysis.ai_summary.replace('\u2728', '*').encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(5)
    
    # Recommendations
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "General Recommendations", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', '', 12)
    pdf.multi_cell(0, 8, analysis.recommendations.encode('latin-1', 'replace').decode('latin-1'))

    # Save to temp file
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    pdf.output(temp_path)
    background_tasks.add_task(os.unlink, temp_path)
    
    return FileResponse(
        temp_path, 
        media_type="application/pdf", 
        filename=f"LumineAI_Report_{analysis.timestamp.strftime('%Y%m%d')}.pdf"
    )
