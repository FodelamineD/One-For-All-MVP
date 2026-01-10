from fpdf import FPDF
import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'One For All - Compte Rendu Assistant', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(history):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, f"Date : {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
    pdf.ln(10)
    
    for msg in history:
        role = "MOI" if msg.type == "human" else "ASSISTANT"
        content = msg.content
        
        # Nettoyage basique des caractères non supportés par latin-1 (FPDF est capricieux)
        content = content.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, f"{role} :", 0, 1)
        
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 10, content)
        pdf.ln(5)
        
    filename = "recap_one_for_all.pdf"
    pdf.output(filename)
    return filename