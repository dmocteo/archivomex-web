def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('El archivo no es válido. Asegúrate que sea .PDF, .PNG, .JPG o .JPEG')

def validate_sensivity(value):
    from django.core.exceptions import ValidationError
    try:
        number = float(value)

        if number < 0 and number > 1:
            raise ValidationError('El número debe de estar entre 0.0 y 1.0')

    except ValueError:
        raise ValidationError('El número debe de estar entre 0.0 y 1.0')

def validate_rows(value):
    from django.core.exceptions import ValidationError
    try:
        rows = value.split(',')
        if len(rows) == 2:
            n = int(rows[0])
            n = int(rows[1])
        elif len(rows) == 1:
            n = int(rows[0])
    except ValueError:
        raise ValidationError('Asegúrate de separar las filas por coma, o solo ingresar la fila inicial.')

def validate_columns(value):
    from django.core.exceptions import ValidationError

    for i in range(0, len(value)):
        if value[i].isdigit() or value[i] == ',':
            pass
        else:
            raise ValidationError('Asegúrate de separar las filas por coma, o solo ingresar la fila inicial.')
            break
