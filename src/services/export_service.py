"""
Export Service - Generate PDF and JSON exports of assessment results
"""

import logging
import json
from datetime import datetime
from io import BytesIO
from typing import Dict, Optional

# PDF generation imports
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("PDF generation not available - install reportlab")

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting assessment results in various formats"""
    
    def __init__(self):
        self.pdf_available = PDF_AVAILABLE
    
    def generate_pdf_report(self, assessment_data: Dict, format_options: Dict = None) -> Optional[BytesIO]:
        """
        Generate a professional PDF report of assessment results
        
        Args:
            assessment_data: Complete assessment data
            format_options: PDF formatting options
            
        Returns:
            BytesIO buffer containing PDF data or None if failed
        """
        if not self.pdf_available:
            logger.error("PDF generation not available")
            return None
        
        try:
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#14B8A6'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#0F766E'),
                spaceAfter=12
            )
            
            # Title
            story.append(Paragraph("Báo Cáo Sàng Lọc Sức Khỏe Tâm Thần", title_style))
            story.append(Spacer(1, 20))
            
            # Patient info section
            story.append(Paragraph("Thông Tin Chung", heading_style))
            
            info_data = [
                ['Ngày thực hiện:', datetime.now().strftime('%d/%m/%Y %H:%M')],
                ['Mã phiên:', assessment_data.get('session_id', 'N/A')],
                ['Loại đánh giá:', self._get_assessment_title(assessment_data)],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Results section
            assessment = assessment_data.get('assessment', {})
            results = assessment.get('results', {})
            
            if results:
                story.append(Paragraph("Kết Quả Đánh Giá", heading_style))
                
                # Score summary
                score_data = [
                    ['Tổng điểm:', str(results.get('total_score', 0))],
                    ['Mức độ:', self._translate_severity(results.get('severity', 'unknown'))],
                    ['Đánh giá rủi ro:', self._translate_risk_level(results.get('risk_level', 'unknown'))]
                ]
                
                score_table = Table(score_data, colWidths=[2*inch, 3*inch])
                score_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ]))
                
                story.append(score_table)
                story.append(Spacer(1, 20))
                
                # Interpretation
                if results.get('interpretation'):
                    story.append(Paragraph("Giải Thích Kết Quả", heading_style))
                    story.append(Paragraph(results['interpretation'], styles['Normal']))
                    story.append(Spacer(1, 15))
                
                # Recommendations
                if results.get('recommendations'):
                    story.append(Paragraph("Khuyến Nghị", heading_style))
                    for i, recommendation in enumerate(results['recommendations'], 1):
                        story.append(Paragraph(f"{i}. {recommendation}", styles['Normal']))
                    story.append(Spacer(1, 15))
            
            # Disclaimer
            story.append(Paragraph("Lưu Ý Quan Trọng", heading_style))
            disclaimer_text = """
            Kết quả này chỉ mang tính chất sàng lọc sơ bộ và không phải là chẩn đoán y tế chính thức. 
            Nếu bạn có những lo ngại về sức khỏe tâm thần, vui lòng tham khảo ý kiến từ chuyên gia 
            sức khỏe tâm thần có trình độ.
            """
            story.append(Paragraph(disclaimer_text, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            buffer.seek(0)
            
            logger.info("PDF report generated successfully")
            return buffer
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            return None
    
    def generate_json_export(self, assessment_data: Dict, format_options: Dict = None) -> Optional[Dict]:
        """
        Generate JSON export of assessment results
        
        Args:
            assessment_data: Complete assessment data
            format_options: JSON formatting options
            
        Returns:
            Dictionary containing formatted data or None if failed
        """
        try:
            options = format_options or {}
            
            # Base export structure
            export_data = {
                'export_info': {
                    'generated_at': datetime.now().isoformat(),
                    'export_version': '2.0.0',
                    'format': 'json'
                },
                'session_info': {
                    'session_id': assessment_data.get('session_id'),
                    'started_at': assessment_data.get('started_at'),
                    'language': assessment_data.get('language', 'vi'),
                    'mode': assessment_data.get('mode', 'ai')
                }
            }
            
            # Add assessment data
            assessment = assessment_data.get('assessment', {})
            if assessment:
                export_data['assessment'] = {
                    'type': assessment.get('type'),
                    'title': self._get_assessment_title(assessment_data),
                    'started_at': assessment.get('started_at'),
                    'completed_at': assessment.get('completed_at'),
                    'total_questions': assessment.get('total_questions', 0)
                }
                
                # Add responses if requested
                if options.get('include_raw_responses', True):
                    export_data['responses'] = assessment.get('responses', {})
                
                # Add results
                results = assessment.get('results', {})
                if results:
                    export_data['results'] = {
                        'total_score': results.get('total_score'),
                        'severity': results.get('severity'),
                        'risk_level': results.get('risk_level'),
                        'interpretation': results.get('interpretation'),
                        'recommendations': results.get('recommendations', [])
                    }
                    
                    if options.get('include_metadata', True):
                        export_data['results']['breakdown'] = results.get('breakdown', {})
            
            # Add conversation summary if available
            if assessment_data.get('conversation_summary'):
                export_data['conversation_summary'] = assessment_data['conversation_summary']
            
            # Add scores if available
            if assessment_data.get('scores'):
                export_data['conversation_scores'] = assessment_data['scores']
            
            logger.info("JSON export generated successfully")
            return export_data
            
        except Exception as e:
            logger.error(f"Error generating JSON export: {e}")
            return None
    
    def generate_export_preview(self, assessment_data: Dict, export_format: str) -> Optional[Dict]:
        """
        Generate a preview of export data
        
        Args:
            assessment_data: Assessment data
            export_format: Format to preview ('pdf' or 'json')
            
        Returns:
            Preview data or None if failed
        """
        try:
            assessment = assessment_data.get('assessment', {})
            results = assessment.get('results', {})
            
            preview = {
                'export_format': export_format,
                'assessment_type': assessment.get('type'),
                'assessment_title': self._get_assessment_title(assessment_data),
                'completion_status': 'completed' if assessment.get('completed_at') else 'in_progress',
                'total_score': results.get('total_score'),
                'severity': results.get('severity'),
                'question_count': assessment.get('total_questions', 0),
                'response_count': len(assessment.get('responses', {})),
                'has_recommendations': bool(results.get('recommendations')),
                'estimated_file_size': self._estimate_file_size(assessment_data, export_format)
            }
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return None
    
    def _get_assessment_title(self, assessment_data: Dict) -> str:
        """Get human-readable assessment title"""
        assessment_type = assessment_data.get('assessment', {}).get('type', 'unknown')
        
        title_mapping = {
            'phq9': 'PHQ-9 - Sàng lọc Trầm cảm',
            'gad7': 'GAD-7 - Sàng lọc Lo âu',
            'dass21_stress': 'DASS-21 - Sàng lọc Căng thẳng',
            'suicide_risk': 'Đánh giá Nguy cơ Tự tử',
            'initial': 'Sàng lọc Ban đầu'
        }
        
    def _translate_severity(self, severity: str) -> str:
        """Translate severity to Vietnamese"""
        severity_mapping = {
            'minimal': 'Tối thiểu',
            'mild': 'Nhẹ',
            'moderate': 'Trung bình',
            'moderately_severe': 'Trung bình nặng',
            'severe': 'Nặng',
            'extremely_severe': 'Cực kỳ nặng',
            'normal': 'Bình thường',
            'unknown': 'Chưa xác định'
        }
        return severity_mapping.get(severity, severity)
    
    def _translate_risk_level(self, risk_level: str) -> str:
        """Translate risk level to Vietnamese"""
        risk_mapping = {
            'minimal': 'Tối thiểu',
            'low': 'Thấp',
            'moderate': 'Trung bình',
            'high': 'Cao',
            'unknown': 'Chưa xác định'
        }
        return risk_mapping.get(risk_level, risk_level)
    
    def _estimate_file_size(self, assessment_data: Dict, export_format: str) -> str:
        """Estimate file size for export"""
        if export_format == 'pdf':
            # PDF typically larger due to formatting
            base_size = 150  # KB
            assessment = assessment_data.get('assessment', {})
            response_count = len(assessment.get('responses', {}))
            estimated_kb = base_size + (response_count * 5)
            return f"{estimated_kb} KB"
        
        elif export_format == 'json':
            # JSON typically smaller
            base_size = 10  # KB
            assessment = assessment_data.get('assessment', {})
            response_count = len(assessment.get('responses', {}))
            estimated_kb = base_size + (response_count * 2)
            return f"{estimated_kb} KB"
        
        return "Unknown"