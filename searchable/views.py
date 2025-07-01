
# Create your views here.
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib import messages

import os
import tempfile
import uuid
import ocrmypdf #type: ignore
from pathlib import Path

def home(request):
    """Home page with PDF upload form"""
    return render(request, 'home.html')

def convert_pdf(request):
    """Process the uploaded PDF and convert to searchable format"""
    if request.method == 'POST' and request.FILES.get('pdf_file'):
        # Get the uploaded file
        pdf_file = request.FILES['pdf_file']
        
        # Validate file is PDF
        if not pdf_file.name.endswith('.pdf'):
            messages.error(request, "Please upload a PDF file.")
            return redirect('home')
            
        # Create a unique filename
        unique_id = uuid.uuid4().hex
        original_filename = pdf_file.name
        base_name = os.path.splitext(original_filename)[0]
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save paths
        input_path = os.path.join(temp_dir, f"{unique_id}_input.pdf")
        output_path = os.path.join(temp_dir, f"{unique_id}_searchable.pdf")
        
        # Save the uploaded file
        fs = FileSystemStorage(location=temp_dir)
        fs.save(f"{unique_id}_input.pdf", pdf_file)
        
        try:
            # Convert PDF using OCRmyPDF
            ocrmypdf.ocr(input_path, output_path, deskew=True)
            
            # Store the output path in the session for download
            request.session['output_pdf_path'] = output_path
            request.session['output_filename'] = f"{base_name}_searchable.pdf"
            
            return render(request, 'searchable/success.html', {
                'original_filename': original_filename,
                'searchable_filename': f"{base_name}_searchable.pdf"
            })
            
        except Exception as e:
            # Clean up files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
                
            messages.error(request, f"Error processing PDF: {str(e)}")
            return redirect('home')
    else:
        return redirect('home')

def download_pdf(request):
    """Download the converted searchable PDF"""
    if 'output_pdf_path' in request.session and os.path.exists(request.session['output_pdf_path']):
        output_path = request.session['output_pdf_path']
        filename = request.session['output_filename']
        
        # Serve the file
        response = FileResponse(open(output_path, 'rb'), 
                              content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Clean up after sending (optional - you might want to keep files for caching)
        # os.remove(output_path)
        
        return response
    else:
        messages.error(request, "File not found or processing error occurred.")
        return redirect('home')