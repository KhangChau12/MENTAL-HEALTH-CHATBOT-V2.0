"""
Export Service - Complete implementation for PDF and JSON export
Generates professional assessment reports with charts and recommendations
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from io import BytesIO
import base64

# For PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.platypus import PageBreak, Image as RLImage
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logging.warning("ReportLab not available. PDF export will be disabled.")

logger = logging.getLogger(__name__)

class ExportService:
    """Service for exporting assessment results to various formats"""
    
    def __init__(self):
        self.supported_formats = ['json']
        if REPORTLAB_AVAILABLE:
            self.supported_formats.append('pdf')
        
        # Vietnamese translations for export
        self.translations = {
            'assessment_types': {
                'phq9': 'Đánh giá Trầm cảm (PHQ-9)',
                'gad7': 'Đánh giá Lo âu (GAD-7)',
                'dass21_stress': 'Đánh giá Căng thẳng (DASS-21)',
                'suicide_risk': 'Đánh giá Nguy cơ Tự tử',
                'initial_screening': 'Sàng lọc Ban đầu'
            },
            'severity_levels': {
                'minimal': 'Tối thiểu',
                'mild': 'Nhẹ',
                'moderate': 'Trung bình',
                'moderately_severe': 'Trung bình nặng',
                'severe': 'Nặng',
                'extremely_severe': 'Cực kỳ nặng'
            },
            'categories': {
                'mood': 'Tâm trạng',
                'interest': 'Sở thích',
                'anxiety': 'Lo âu',
                'sleep': 'Giấc ngủ',
                'energy': 'Năng lượng',
                'appetite': 'Ăn uống',
                'self_worth': 'Tự đánh giá',
                'concentration': 'Tập trung',
                'psychomotor': 'Vận động'
            }
        }
    
    def export_assessment_results(
        self, 
        assessment_data: Dict, 
        export_format: str = 'json',
        include_chat_history: bool = False
    ) -> Dict[str, Any]:
        """
        Export assessment results to specified format
        
        Args:
            assessment_data: Complete assessment data
            export_format: 'pdf' or 'json'
            include_chat_history: Whether to include chat conversation
            
        Returns:
            Dictionary with export result
        """
        try:
            if export_format not in self.supported_formats:
                raise ValueError(f"Unsupported format: {export_format}")
            
            # Validate assessment data
            validated_data = self._validate_assessment_data(assessment_data)
            
            if export_format == 'json':
                return self._export_json(validated_data, include_chat_history)
            elif export_format == 'pdf':
                return self._export_pdf(validated_data, include_chat_history)
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Không thể xuất kết quả. Vui lòng thử lại.'
            }
    
    def _validate_assessment_data(self, data: Dict) -> Dict:
        """Validate and clean assessment data"""
        required_fields = ['assessment_type', 'total_score', 'completed_at']
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Ensure numeric fields are proper numbers
        if 'total_score' in data:
            data['total_score'] = int(data['total_score'])
        
        if 'max_score' in data:
            data['max_score'] = int(data['max_score'])
        
        # Add missing fields with defaults
        data.setdefault('session_id', 'unknown')
        data.setdefault('severity', {'level': 'unknown', 'label': 'Không xác định'})
        data.setdefault('recommendations', [])
        data.setdefault('category_scores', {})
        
        return data
    
    def _export_json(self, data: Dict, include_chat: bool) -> Dict[str, Any]:
        """Export to JSON format"""
        try:
            export_data = {
                'export_info': {
                    'format': 'json',
                    'exported_at': datetime.now().isoformat(),
                    'version': '1.0',
                    'include_chat_history': include_chat
                },
                'assessment': self._prepare_assessment_data(data),
                'results': self._prepare_results_data(data),
                'recommendations': data.get('recommendations', [])
            }
            
            if include_chat and 'chat_history' in data:
                export_data['chat_history'] = data['chat_history']
            
            # Convert to JSON string
            json_string = json.dumps(export_data, ensure_ascii=False, indent=2)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            assessment_type = data.get('assessment_type', 'assessment')
            filename = f"ket_qua_{assessment_type}_{timestamp}.json"
            
            return {
                'success': True,
                'format': 'json',
                'data': json_string,
                'filename': filename,
                'size': len(json_string.encode('utf-8')),
                'mime_type': 'application/json'
            }
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise
    
    def _export_pdf(self, data: Dict, include_chat: bool) -> Dict[str, Any]:
        """Export to PDF format"""
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("PDF export not available - ReportLab not installed")
        
        try:
            buffer = BytesIO()
            
            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )
            
            # Build PDF content
            story = []
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkblue
            )
            
            # Header
            story.append(Paragraph("BÁO CÁO KẾT QUẢ ĐÁNH GIÁ SỨC KHỎE TÂM THẦN", title_style))
            story.append(Spacer(1, 20))
            
            # Assessment info
            story.extend(self._build_assessment_info_section(data, styles))
            
            # Results section
            story.extend(self._build_results_section(data, styles))
            
            # Category breakdown
            if data.get('category_scores'):
                story.extend(self._build_category_breakdown(data, styles))
            
            # Recommendations
            if data.get('recommendations'):
                story.extend(self._build_recommendations_section(data, styles))
            
            # Chat history (if requested)
            if include_chat and data.get('chat_history'):
                story.extend(self._build_chat_history_section(data, styles))
            
            # Footer
            story.append(PageBreak())
            story.extend(self._build_footer_section(styles))
            
            # Build PDF
            doc.build(story)
            
            # Get PDF data
            pdf_data = buffer.getvalue()
            buffer.close()
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            assessment_type = data.get('assessment_type', 'assessment')
            filename = f"bao_cao_{assessment_type}_{timestamp}.pdf"
            
            return {
                'success': True,
                'format': 'pdf',
                'data': base64.b64encode(pdf_data).decode('utf-8'),
                'filename': filename,
                'size': len(pdf_data),
                'mime_type': 'application/pdf'
            }
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            raise
    
    def _prepare_assessment_data(self, data: Dict) -> Dict:
        """Prepare assessment metadata for export"""
        assessment_type = data.get('assessment_type', 'unknown')
        assessment_title = self.translations['assessment_types'].get(
            assessment_type, assessment_type
        )
        
        return {
            'type': assessment_type,
            'title': assessment_title,
            'completed_at': data.get('completed_at'),
            'session_id': data.get('session_id'),
            'total_questions': len(data.get('answers', {})),
            'completion_time': self._calculate_completion_time(data)
        }
    
    def _prepare_results_data(self, data: Dict) -> Dict:
        """Prepare results data for export"""
        severity = data.get('severity', {})
        severity_label = self.translations['severity_levels'].get(
            severity.get('level', 'unknown'), 
            severity.get('label', 'Không xác định')
        )
        
        return {
            'total_score': data.get('total_score', 0),
            'max_score': data.get('max_score', 0),
            'percentage': data.get('percentage', 0),
            'severity': {
                'level': severity.get('level', 'unknown'),
                'label': severity_label,
                'color': severity.get('color', '#6b7280')
            },
            'interpretation': self._generate_score_interpretation(data)
        }
    
    def _build_assessment_info_section(self, data: Dict, styles) -> List:
        """Build assessment information section for PDF"""
        elements = []
        
        # Assessment info table
        assessment_info = [
            ['Loại đánh giá:', self.translations['assessment_types'].get(
                data.get('assessment_type'), data.get('assessment_type', 'Không xác định')
            )],
            ['Ngày thực hiện:', self._format_datetime(data.get('completed_at'))],
            ['Mã phiên:', data.get('session_id', 'Không có')],
            ['Số câu hỏi:', str(len(data.get('answers', {})))],
        ]
        
        table = Table(assessment_info, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_results_section(self, data: Dict, styles) -> List:
        """Build results section for PDF"""
        elements = []
        
        # Results heading
        elements.append(Paragraph("KẾT QUẢ ĐÁNH GIÁ", styles['Heading2']))
        
        # Score summary
        total_score = data.get('total_score', 0)
        max_score = data.get('max_score', 0)
        severity = data.get('severity', {})
        
        score_info = [
            ['Điểm số tổng:', f"{total_score}/{max_score}"],
            ['Phần trăm:', f"{data.get('percentage', 0)}%"],
            ['Mức độ nghiêm trọng:', severity.get('label', 'Không xác định')],
        ]
        
        score_table = Table(score_info, colWidths=[2*inch, 2*inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        
        elements.append(score_table)
        elements.append(Spacer(1, 15))
        
        # Interpretation
        interpretation = self._generate_score_interpretation(data)
        elements.append(Paragraph("Giải thích kết quả:", styles['Heading3']))
        elements.append(Paragraph(interpretation, styles['Normal']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_category_breakdown(self, data: Dict, styles) -> List:
        """Build category breakdown section"""
        elements = []
        category_scores = data.get('category_scores', {})
        
        if not category_scores:
            return elements
        
        elements.append(Paragraph("PHÂN TÍCH THEO DANH MỤC", styles['Heading2']))
        
        # Category table
        category_data = [['Danh mục', 'Điểm số', 'Tỷ lệ']]
        
        for category, score_data in category_scores.items():
            if category.startswith('_'):  # Skip metadata
                continue
                
            category_name = self.translations['categories'].get(category, category)
            score = score_data.get('score', 0) if isinstance(score_data, dict) else score_data
            count = score_data.get('count', 1) if isinstance(score_data, dict) else 1
            avg_score = score / count if count > 0 else 0
            percentage = min(avg_score * 25, 100)  # Rough percentage conversion
            
            category_data.append([
                category_name,
                f"{score:.1f}",
                f"{percentage:.0f}%"
            ])
        
        category_table = Table(category_data, colWidths=[2.5*inch, 1*inch, 1*inch])
        category_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ]))
        
        elements.append(category_table)
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_recommendations_section(self, data: Dict, styles) -> List:
        """Build recommendations section"""
        elements = []
        recommendations = data.get('recommendations', [])
        
        if not recommendations:
            return elements
        
        elements.append(Paragraph("KHUYẾN NGHỊ VÀ HƯỚNG DẪN", styles['Heading2']))
        
        for i, rec in enumerate(recommendations, 1):
            rec_title = rec.get('title', f'Khuyến nghị {i}')
            rec_content = rec.get('content', 'Không có nội dung')
            rec_type = rec.get('type', 'general')
            
            # Add type indicator
            type_labels = {
                'urgent': '🚨 KHẨN CẤP',
                'professional': '👨‍⚕️ CHUYÊN NGHIỆP',
                'lifestyle': '💡 THAY ĐỔI LỐI SỐNG',
                'technique': '🧘 KỸ THUẬT',
                'general': '📋 TỔNG QUÁT'
            }
            
            type_label = type_labels.get(rec_type, '📋 TỔNG QUÁT')
            
            elements.append(Paragraph(f"{type_label} {rec_title}", styles['Heading3']))
            elements.append(Paragraph(rec_content, styles['Normal']))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_chat_history_section(self, data: Dict, styles) -> List:
        """Build chat history section"""
        elements = []
        chat_history = data.get('chat_history', [])
        
        if not chat_history:
            return elements
        
        elements.append(PageBreak())
        elements.append(Paragraph("LỊCH SỬ CUỘC TRÒ CHUYỆN", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        for msg in chat_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            # Format role
            role_display = '👤 Bạn:' if role == 'user' else '🤖 Trợ lý:'
            
            # Add message
            elements.append(Paragraph(f"<b>{role_display}</b>", styles['Normal']))
            elements.append(Paragraph(content, styles['Normal']))
            
            if timestamp:
                time_str = self._format_datetime(timestamp, include_time=True)
                elements.append(Paragraph(f"<i>{time_str}</i>", styles['Normal']))
            
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _build_footer_section(self, styles) -> List:
        """Build footer section"""
        elements = []
        
        elements.append(Paragraph("THÔNG TIN QUAN TRỌNG", styles['Heading2']))
        
        disclaimer = """
        <b>Lưu ý quan trọng:</b><br/>
        • Kết quả này chỉ mang tính chất sàng lọc và tham khảo<br/>
        • Không thay thế cho việc chẩn đoán y tế chuyên nghiệp<br/>
        • Nếu bạn có các triệu chứng nghiêm trọng, hãy tìm kiếm sự hỗ trợ từ chuyên gia<br/>
        • Trong trường hợp khẩn cấp, hãy gọi đường dây nóng: 1800-0011<br/><br/>
        
        <b>Liên hệ hỗ trợ:</b><br/>
        • Đường dây nóng sức khỏe tâm thần: 1900-6048<br/>
        • Cấp cứu: 113<br/>
        • Website: https://mentalhealth.gov.vn<br/><br/>
        
        Báo cáo được tạo tự động vào {export_time}
        """.format(export_time=datetime.now().strftime('%d/%m/%Y lúc %H:%M'))
        
        elements.append(Paragraph(disclaimer, styles['Normal']))
        
        return elements
    
    def _generate_score_interpretation(self, data: Dict) -> str:
        """Generate interpretation text for the score"""
        total_score = data.get('total_score', 0)
        max_score = data.get('max_score', 1)
        assessment_type = data.get('assessment_type', '')
        severity = data.get('severity', {}).get('level', 'unknown')
        
        percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Type-specific interpretations
        if assessment_type == 'phq9':
            if severity == 'minimal':
                return f"Điểm số {total_score}/27 ({percentage:.0f}%) cho thấy các triệu chứng trầm cảm ở mức tối thiểu. Tình trạng sức khỏe tâm thần hiện tại khá tốt."
            elif severity == 'mild':
                return f"Điểm số {total_score}/27 ({percentage:.0f}%) cho thấy các triệu chứng trầm cảm nhẹ. Nên chú ý theo dõi và áp dụng các biện pháp chăm sóc bản thân."
            elif severity == 'moderate':
                return f"Điểm số {total_score}/27 ({percentage:.0f}%) cho thấy các triệu chứng trầm cảm ở mức trung bình. Khuyến nghị tham khảo ý kiến chuyên gia."
            else:
                return f"Điểm số {total_score}/27 ({percentage:.0f}%) cho thấy các triệu chứng trầm cảm nghiêm trọng. Cần tìm kiếm sự hỗ trợ chuyên nghiệp ngay lập tức."
        
        elif assessment_type == 'gad7':
            if severity == 'minimal':
                return f"Điểm số {total_score}/21 ({percentage:.0f}%) cho thấy mức độ lo âu tối thiểu. Tình trạng lo âu hiện tại trong giới hạn bình thường."
            elif severity == 'mild':
                return f"Điểm số {total_score}/21 ({percentage:.0f}%) cho thấy mức độ lo âu nhẹ. Có thể áp dụng các kỹ thuật thư giãn và quản lý căng thẳng."
            else:
                return f"Điểm số {total_score}/21 ({percentage:.0f}%) cho thấy mức độ lo âu đáng quan ngại. Nên tìm kiếm sự hỗ trợ từ chuyên gia tâm lý."
        
        else:
            # Generic interpretation
            if percentage <= 25:
                return f"Điểm số {total_score}/{max_score} ({percentage:.0f}%) cho thấy tình trạng tốt với ít dấu hiệu đáng lo ngại."
            elif percentage <= 50:
                return f"Điểm số {total_score}/{max_score} ({percentage:.0f}%) cho thấy một số dấu hiệu cần chú ý và theo dõi."
            elif percentage <= 75:
                return f"Điểm số {total_score}/{max_score} ({percentage:.0f}%) cho thấy các dấu hiệu đáng quan ngại, nên tìm kiếm hỗ trợ."
            else:
                return f"Điểm số {total_score}/{max_score} ({percentage:.0f}%) cho thấy tình trạng nghiêm trọng, cần hỗ trợ chuyên nghiệp ngay lập tức."
    
    def _calculate_completion_time(self, data: Dict) -> Optional[str]:
        """Calculate assessment completion time"""
        started_at = data.get('started_at')
        completed_at = data.get('completed_at')
        
        if not started_at or not completed_at:
            return None
        
        try:
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            duration = end_time - start_time
            
            minutes = int(duration.total_seconds() / 60)
            seconds = int(duration.total_seconds() % 60)
            
            if minutes > 0:
                return f"{minutes} phút {seconds} giây"
            else:
                return f"{seconds} giây"
        except:
            return None
    
    def _format_datetime(self, dt_string: Optional[str], include_time: bool = False) -> str:
        """Format datetime string for display"""
        if not dt_string:
            return 'Không có thông tin'
        
        try:
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
            dt = dt.replace(tzinfo=None)  # Remove timezone for local display
            
            if include_time:
                return dt.strftime('%d/%m/%Y lúc %H:%M')
            else:
                return dt.strftime('%d/%m/%Y')
        except:
            return str(dt_string)
    
    def get_export_preview(self, assessment_data: Dict, export_format: str) -> Dict:
        """
        Generate a preview of export data
        
        Args:
            assessment_data: Assessment data
            export_format: Format to preview ('pdf' or 'json')
            
        Returns:
            Preview data or None if failed
        """
        try:
            assessment = assessment_data
            
            preview = {
                'export_format': export_format,
                'assessment_type': assessment.get('assessment_type'),
                'assessment_title': self.translations['assessment_types'].get(
                    assessment.get('assessment_type'), 
                    assessment.get('assessment_type', 'Không xác định')
                ),
                'completion_status': 'completed' if assessment.get('completed_at') else 'in_progress',
                'total_score': assessment.get('total_score'),
                'max_score': assessment.get('max_score'),
                'severity': assessment.get('severity'),
                'question_count': len(assessment.get('answers', {})),
                'has_recommendations': bool(assessment.get('recommendations')),
                'has_chat_history': bool(assessment.get('chat_history')),
                'estimated_file_size': self._estimate_file_size(assessment, export_format)
            }
            
            return preview
            
        except Exception as e:
            logger.error(f"Error generating preview: {e}")
            return None
    
    def _estimate_file_size(self, assessment_data: Dict, export_format: str) -> str:
        """Estimate file size for export"""
        try:
            # Base size estimation
            base_size = 5000  # 5KB base
            
            # Add size for answers
            answers_size = len(assessment_data.get('answers', {})) * 100
            
            # Add size for recommendations
            rec_size = len(assessment_data.get('recommendations', [])) * 200
            
            # Add size for chat history
            chat_size = 0
            if assessment_data.get('chat_history'):
                chat_messages = assessment_data['chat_history']
                chat_size = sum(len(msg.get('content', '')) for msg in chat_messages) * 2
            
            total_size = base_size + answers_size + rec_size + chat_size
            
            # PDF is typically larger
            if export_format == 'pdf':
                total_size *= 3
            
            # Format size
            if total_size < 1024:
                return f"{total_size} bytes"
            elif total_size < 1024 * 1024:
                return f"{total_size / 1024:.1f} KB"
            else:
                return f"{total_size / (1024 * 1024):.1f} MB"
                
        except:
            return "Không xác định"
    
    def validate_export_data(self, assessment_data: Dict) -> Dict[str, Any]:
        """
        Validate data before export
        
        Returns:
            Validation result with any issues found
        """
        issues = []
        warnings = []
        
        # Check required fields
        required_fields = ['assessment_type', 'total_score', 'completed_at']
        for field in required_fields:
            if field not in assessment_data:
                issues.append(f"Thiếu trường bắt buộc: {field}")
        
        # Check data quality
        if assessment_data.get('total_score') is None:
            warnings.append("Điểm số không được xác định")
        
        if not assessment_data.get('answers'):
            warnings.append("Không có câu trả lời được lưu")
        
        if not assessment_data.get('recommendations'):
            warnings.append("Không có khuyến nghị")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'can_export': len(issues) == 0
        }

# Factory function for easy usage
def create_export_service() -> ExportService:
    """Create and return an ExportService instance"""
    return ExportService()

# Utility function for quick export
def export_assessment(
    assessment_data: Dict, 
    format: str = 'json',
    include_chat: bool = False
) -> Dict[str, Any]:
    """
    Quick utility function for exporting assessment results
    
    Args:
        assessment_data: Assessment data to export
        format: Export format ('json' or 'pdf')
        include_chat: Whether to include chat history
        
    Returns:
        Export result dictionary
    """
    service = create_export_service()
    return service.export_assessment_results(assessment_data, format, include_chat)