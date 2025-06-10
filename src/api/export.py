"""
Export API - Handles result export functionality
"""

import logging
import json
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from io import BytesIO

from ..services.export_service import ExportService
from ..utils.validators import validate_export_request

logger = logging.getLogger(__name__)

# Create blueprint
export_bp = Blueprint('export', __name__)

# Initialize export service
export_service = ExportService()

@export_bp.route('/pdf', methods=['POST'])
def export_pdf():
    """
    Export assessment results as PDF
    
    Expected JSON:
    {
        "assessment_data": {...},
        "format_options": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu để xuất'
            }), 400
        
        assessment_data = data.get('assessment_data')
        format_options = data.get('format_options', {})
        
        # Validate export request
        if not validate_export_request(assessment_data, 'pdf'):
            return jsonify({
                'error': 'Invalid export data',
                'message': 'Dữ liệu xuất không hợp lệ'
            }), 400
        
        # Generate PDF
        pdf_buffer = export_service.generate_pdf_report(assessment_data, format_options)
        
        if not pdf_buffer:
            return jsonify({
                'error': 'PDF generation failed',
                'message': 'Không thể tạo file PDF'
            }), 500
        
        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        assessment_type = assessment_data.get('assessment', {}).get('type', 'assessment')
        filename = f"mental_health_{assessment_type}_{timestamp}.pdf"
        
        logger.info(f"PDF export generated: {filename}")
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        return jsonify({
            'error': 'Export failed',
            'message': 'Không thể xuất file PDF'
        }), 500

@export_bp.route('/json', methods=['POST'])
def export_json():
    """
    Export assessment results as JSON
    
    Expected JSON:
    {
        "assessment_data": {...},
        "format_options": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Vui lòng cung cấp dữ liệu để xuất'
            }), 400
        
        assessment_data = data.get('assessment_data')
        format_options = data.get('format_options', {})
        
        # Validate export request
        if not validate_export_request(assessment_data, 'json'):
            return jsonify({
                'error': 'Invalid export data',
                'message': 'Dữ liệu xuất không hợp lệ'
            }), 400
        
        # Generate JSON export
        json_data = export_service.generate_json_export(assessment_data, format_options)
        
        if not json_data:
            return jsonify({
                'error': 'JSON generation failed',
                'message': 'Không thể tạo file JSON'
            }), 500
        
        # Prepare filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        assessment_type = assessment_data.get('assessment', {}).get('type', 'assessment')
        filename = f"mental_health_{assessment_type}_{timestamp}.json"
        
        # Create JSON buffer
        json_buffer = BytesIO()
        json_buffer.write(json.dumps(json_data, indent=2, ensure_ascii=False).encode('utf-8'))
        json_buffer.seek(0)
        
        logger.info(f"JSON export generated: {filename}")
        
        return send_file(
            json_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error exporting JSON: {e}")
        return jsonify({
            'error': 'Export failed',
            'message': 'Không thể xuất file JSON'
        }), 500

@export_bp.route('/preview', methods=['POST'])
def preview_export():
    """
    Get a preview of export data without generating file
    
    Expected JSON:
    {
        "assessment_data": {...},
        "export_format": "pdf" | "json"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided'
            }), 400
        
        assessment_data = data.get('assessment_data')
        export_format = data.get('export_format', 'json')
        
        # Validate data
        if not validate_export_request(assessment_data, export_format):
            return jsonify({
                'error': 'Invalid export data',
                'message': 'Dữ liệu xuất không hợp lệ'
            }), 400
        
        # Generate preview
        preview_data = export_service.generate_export_preview(assessment_data, export_format)
        
        return jsonify({
            'preview': preview_data,
            'export_format': export_format,
            'can_export': True
        })
        
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        return jsonify({
            'error': 'Preview generation failed',
            'message': 'Không thể tạo bản xem trước'
        }), 500

@export_bp.route('/formats', methods=['GET'])
def get_export_formats():
    """
    Get available export formats and their specifications
    """
    try:
        formats = {
            'pdf': {
                'name': 'PDF Report',
                'description': 'Báo cáo PDF chuyên nghiệp với biểu đồ và khuyến nghị',
                'mime_type': 'application/pdf',
                'features': [
                    'Biểu đồ điểm số',
                    'Giải thích chi tiết',
                    'Khuyến nghị cá nhân',
                    'Thông tin liên hệ hỗ trợ'
                ],
                'options': {
                    'include_charts': {'type': 'boolean', 'default': True},
                    'include_recommendations': {'type': 'boolean', 'default': True},
                    'language': {'type': 'string', 'default': 'vi', 'options': ['vi', 'en']}
                }
            },
            'json': {
                'name': 'JSON Data',
                'description': 'Dữ liệu thô ở định dạng JSON để phân tích thêm',
                'mime_type': 'application/json',
                'features': [
                    'Dữ liệu thô đầy đủ',
                    'Cấu trúc dễ đọc',
                    'Thông tin timestamp',
                    'Metadata chi tiết'
                ],
                'options': {
                    'include_raw_responses': {'type': 'boolean', 'default': True},
                    'include_metadata': {'type': 'boolean', 'default': True},
                    'pretty_format': {'type': 'boolean', 'default': True}
                }
            }
        }
        
        return jsonify({
            'formats': formats,
            'default_format': 'pdf'
        })
        
    except Exception as e:
        logger.error(f"Error getting export formats: {e}")
        return jsonify({
            'error': 'Failed to get export formats'
        }), 500

@export_bp.route('/history', methods=['GET'])
def get_export_history():
    """
    Get export history (in production, this would query a database)
    """
    try:
        # Mock export history - in production, this would come from database
        history = [
            {
                'id': 'export_001',
                'assessment_type': 'phq9',
                'format': 'pdf',
                'created_at': '2024-06-10T10:30:00Z',
                'file_size': '245 KB',
                'status': 'completed'
            },
            {
                'id': 'export_002',
                'assessment_type': 'gad7',
                'format': 'json',
                'created_at': '2024-06-09T14:15:00Z',
                'file_size': '12 KB',
                'status': 'completed'
            }
        ]
        
        return jsonify({
            'history': history,
            'total_exports': len(history)
        })
        
    except Exception as e:
        logger.error(f"Error getting export history: {e}")
        return jsonify({
            'error': 'Failed to get export history'
        }), 500

@export_bp.route('/validate', methods=['POST'])
def validate_export_data():
    """
    Validate data before export
    
    Expected JSON:
    {
        "assessment_data": {...},
        "export_format": "pdf" | "json"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'valid': False,
                'errors': ['No data provided']
            })
        
        assessment_data = data.get('assessment_data')
        export_format = data.get('export_format', 'json')
        
        # Perform validation
        is_valid = validate_export_request(assessment_data, export_format)
        
        validation_result = {
            'valid': is_valid,
            'export_format': export_format
        }
        
        if is_valid:
            validation_result['message'] = 'Dữ liệu hợp lệ, có thể xuất file'
        else:
            validation_result['errors'] = [
                'Thiếu dữ liệu đánh giá',
                'Định dạng xuất không được hỗ trợ',
                'Dữ liệu không đầy đủ'
            ]
        
        return jsonify(validation_result)
        
    except Exception as e:
        logger.error(f"Error validating export data: {e}")
        return jsonify({
            'valid': False,
            'errors': ['Validation failed']
        }), 500