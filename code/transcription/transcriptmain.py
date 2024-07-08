from . import textdocs

def transcript_file(filename):
    # Get the file extension:
    extension = filename.split('.')[-1]
    
    # Call the appropriate function:
    if extension == 'docx':
        return textdocs.read_docx(filename)
    elif extension == 'pdf':
        return textdocs.read_pdf(filename)
    elif extension == 'txt':
        return textdocs.read_txt(filename)
    else:
        return "File type not supported."