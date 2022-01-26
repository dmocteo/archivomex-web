from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, CreateView
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from django.contrib import messages

from .forms import BookForm, RowsForm, SensitivityForm, ColumnsForm, SensitivityColumnForm
from .models import Book, Rows, Sensitivity, Columns, SensitivityColumn

from PIL import Image
import fitz

import cv2
import numpy as np
import urllib.request
import base64
import os
import pytesseract

import uuid

from numba import njit, jit

import csv
import pandas as pd

from django.http import HttpResponse

import cloudinary.uploader

# Create your views here.
class Home(TemplateView):
    template_name = 'home.html'

def upload_book(request):
    context = {}

    request.session['sensibilidad'] = 0.50

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            if request.FILES['pdf'].name.lower().endswith(('.pdf')) and form.cleaned_data['page'] is not None:
                page = form.cleaned_data['page']

                doc = fitz.open('pdf', request.FILES['pdf'].read())

                Pagina = int(page) - 1
                page = doc.loadPage(Pagina)

                zoom = 5
                mat = fitz.Matrix(zoom, zoom)
                pix = page.getPixmap(matrix=mat)

                id = uuid.uuid4()
                output = str(id) + '.png'
                pix.writePNG(output)

                try:
                    res = cloudinary.uploader.upload(output, timeout=60)['secure_url']
                    request.session['imagen'] = res

                except Exception as e:
                    messages.error(request, 'Surgió un error inesperado. Inténtalo de nuevo.')
                    os.remove(output)
                    return redirect('upload_book')

                os.remove(output)

            else:
                try:
                    res = cloudinary.uploader.upload(request.FILES['pdf'], timeout=60)['secure_url']
                    request.session['imagen'] = res
                except:
                    messages.error(request, 'Surgió un error inesperado. Inténtalo de nuevo.')
                    return redirect('upload_book')

            return redirect('upload_book_rows')
    else:
        form = BookForm()
    return render(request, 'upload_book.html', {
        'form': form
    })

def upload_book_rows(request):

    context = {}

    if 'sensibilidad' not in request.session:
        return redirect('upload_book')

    sensibilidad = request.session['sensibilidad']

    form1 = RowsForm()

    form2 = SensitivityForm()
    form2.fields["value"].initial = sensibilidad

    imagen = request.session['imagen']

    url_response = urllib.request.urlopen(imagen)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)

    if request.method == 'POST' and 'rows_csv' in request.POST:
        form1 = RowsForm(request.POST)

        if form1.is_valid():

            value = form1.cleaned_data['rowscsv']

            rows = value.split(',')
            if len(rows) == 2:
                begin = int(rows[0]) - 1
                end = int(rows[1]) - 1

                filascont = len(request.session['rows'])

                if begin > -1 and end > -1:
                    if begin < filascont and end < filascont:

                        y1 = request.session['rows'][begin]
                        y2 = request.session['rows'][end]
                        x2 = image.shape[1]

                        image_crop = image[y1+10:y2-10, 150:x2-150]

                        id = uuid.uuid4()
                        output = 'img_' + str(id) + '.png'

                        cv2.imwrite(output, image_crop)

                        try:
                            res = cloudinary.uploader.upload(output, timeout=60)['secure_url']
                            request.session['imagecrop'] = res

                        except Exception as e:
                            messages.error(request, 'Surgió un error inesperado. Inténtalo de nuevo.')
                            os.remove(output)
                            return redirect('upload_book_rows')

                        os.remove(output)
                        request.session['sensibilidadcolumnas'] = 0.20

                        return redirect('upload_book_columns')

                    else:
                        messages.error(request, 'Asegúrate que las filas existan en la imagen procesada')
                        return redirect('upload_book_rows')
                else:
                    messages.error(request, 'Asegúrate que las filas existan en la imagen procesada')
                    return redirect('upload_book_rows')

            elif len(rows) == 1:
                begin = int(rows[0]) - 1

                filascont = len(request.session['rows'])

                if begin > -1:
                    if begin < filascont:

                        y1 = request.session['rows'][begin] + 10

                        y2 = image.shape[0]
                        x2 = image.shape[1]

                        image_crop = image[y1+10:y2-10, 150:x2-150]

                        id = uuid.uuid4()
                        output = 'img_' + str(id) + '.png'

                        cv2.imwrite(output, image_crop)

                        try:
                            res = cloudinary.uploader.upload(output, timeout=60)['secure_url']
                            request.session['imagecrop'] = res

                        except Exception as e:
                            messages.error(request, 'Surgió un error inesperado. Inténtalo de nuevo.')
                            os.remove(output)
                            return redirect('upload_book_rows')

                        os.remove(output)
                        request.session['sensibilidadcolumnas'] = 0.20

                        return redirect('upload_book_columns')

                    else:
                        messages.error(request, 'Asegúrate que la fila exista en la imagen procesada')
                        return redirect('upload_book_rows')
                else:
                    messages.error(request, 'Asegúrate que la fila exista en la imagen procesada')
                    return redirect('upload_book_rows')

    if request.method == 'POST' and 'sensitivity_change' in request.POST:
        form2 = SensitivityForm(request.POST)
        if form2.is_valid():
            sensibilidad = float(form2.cleaned_data['value'])
            request.session['sensibilidad'] = sensibilidad

    image2, filas = linesfull(image, sensibilidad)

    request.session['rows'] = filas

    src = base64.b64encode(cv2.imencode('.png', image2)[1]).decode('ascii')

    return render(request, 'upload_book_rows.html', {
        'src': src,
        'form1': form1,
        'form2': form2,
    })

def upload_book_columns(request):

    context = {}

    if 'sensibilidadcolumnas' not in request.session:
        return redirect('upload_book_rows')

    sensibilidad = request.session['sensibilidadcolumnas']

    form1 = ColumnsForm()

    form2 = SensitivityColumnForm()
    form2.fields["value"].initial = sensibilidad

    imagen = request.session['imagecrop']

    url_response = urllib.request.urlopen(imagen)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)

    if request.method == 'POST' and 'columns_csv' in request.POST:
        form1 = ColumnsForm(request.POST)

        if form1.is_valid():

            value = form1.cleaned_data['columnscsv']
            columns = value.split(',')

            columnasimagen = request.session['columns']

            for column in columns:

                valorcolumna = int(column)-1

                if valorcolumna > -1 and valorcolumna < len(columnasimagen):
                    pass
                else:
                    messages.error(request, 'Asegúrate que las columnas existan imagen procesada')
                    return redirect('upload_book_columns')

            request.session['columnscsv'] = columns

            return redirect('download_book')

        else:
            messages.error(request, 'Asegúrate de separar por comas las columnas')
            return redirect('upload_book_columns')

    if request.method == 'POST' and 'sensitivity_change' in request.POST:
        form2 = SensitivityForm(request.POST)
        if form2.is_valid():
            sensibilidad = float(form2.cleaned_data['value'])
            request.session['sensibilidad'] = sensibilidad

    image2, columnas = columnsfull(image, sensibilidad)

    request.session['columns'] = columnas

    src = base64.b64encode(cv2.imencode('.png', image2)[1]).decode('ascii')

    return render(request, 'upload_book_columns.html', {
        'src': src,
        'form1': form1,
        'form2': form2,
    })

def download_book(request):

    context = {}

    if 'columns' not in request.session:
        messages.error(request, 'Parece que no hay nada que procesar. Asegúrate de haber cargado una imagen.')
        return redirect('upload_book')

    return render(request, 'download.html', {
    })

def export_csv(request):

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="extracción.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    row = []
    col = []

    imagen = request.session['imagecrop']

    url_response = urllib.request.urlopen(imagen)
    img_array = np.array(bytearray(url_response.read()), dtype=np.uint8)
    image = cv2.imdecode(img_array, -1)

    y2 = image.shape[0]
    x2 = image.shape[1]
    prev = 0

    pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
    #pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\VAIO\\Desktop\\CIDE\\ArchivoMex Xtractor\\Windows\\Xtractor\\Tesseract-OCR\\tesseract.exe'

    columnasimagen = request.session['columns']
    columns = request.session['columnscsv']

    for column in columns:
        valorcolumna = int(column) - 1

    for i in range(0, len(columns)):
        x1 = int(columnasimagen[int(columns[i]) - 1])

        if i == len(columns) - 1:
            x2 = image.shape[1]
        else:
            x2 = int(columnasimagen[int(columns[i + 1]) - 1])

        columncrop = image[0:y2, x1:x2]

        img = columncrop[:, :, 0]
        ret, thresh1 = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)

        height = thresh1.shape[0]
        width = thresh1.shape[1]

        img_crop_row_aux = np.sum(thresh1, axis=1)

        flag = True
        prev = 0

        for i in range(0, height):
            if img_crop_row_aux[i] < width * 255:
                flag = False
            else:
                if flag == False:
                    cellcrop = image[prev: i + 5, x1:x2]
                    img = Image.fromarray(cellcrop)

                    text = pytesseract.image_to_string(cellcrop, lang='spa')
                    if len(text) == 0 or text == '':
                        text = pytesseract.image_to_string(cellcrop, lang='spa',
                                                           config='--psm 10 --oem 3 -c tessedit_char_whitelist=.0123456789')
                    prev = i + 5
                    flag = True

                    if is_number(text[:-2]):
                        col.append(float(text[:-2].replace(' ','')))
                    else:
                        col.append(text[:-2])

        row.append(col.copy())
        col.clear()

    f = pd.DataFrame(row)
    f.drop([0, 0])

    for r in row:
        f.append(r)

    f2 = f.transpose()

    f2.to_csv(path_or_buf=response, index=False, header=False)

    return response

def is_number(s):
    s = s.replace(' ','')
    try:
        float(s)
        return True
    except ValueError:
        return False


def columnsfull(image, Sensibilidad):

    img = image[:, :, 0]
    ret, thresh1 = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)

    height = thresh1.shape[0]
    width = thresh1.shape[1]

    listadirectriz = lines2(thresh1, Sensibilidad)

    tablas = []

    for k in range(0, len(listadirectriz) - 1):
        if abs(listadirectriz[k] - listadirectriz[k + 1]) > 25:
            tablas.append(listadirectriz[k])

    if len(listadirectriz) > 0:
        tablas.append(listadirectriz[len(listadirectriz) - 1])

        lineasHorizontal = tablas

        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 3
        fontColor = (0, 0, 255)
        lineType = 10

        c = 1

        for t in lineasHorizontal:
            cv2.line(thresh1, (t, 0), (t, height), (0, 255, 0), 3)
            if c % 2 != 0:
                cv2.putText(thresh1, str(c), (t, 80), font, fontScale, fontColor, lineType)
            else:
                cv2.putText(thresh1, str(c), (t, height - 20), font, fontScale, fontColor, lineType)
            c += 1


    result = thresh1

    return result, tablas

@jit(nopython=True)
def lines2(thresh1, Sensibilidad):

    Sensibilidad = int(Sensibilidad * 100)

    height = thresh1.shape[0]
    width = thresh1.shape[1]

    listadirectriz = []

    img_crop_col_aux = np.sum(thresh1, axis=0)
    flag = False
    aux = 1
    total = 255 * height
    c = 0

    for i in range(0, width):
        if img_crop_col_aux[i] == total:
            if flag == False:
                aux = i
                flag = True
            else:
                c += 1
        else:
            if flag:
                flag = False
                if c > Sensibilidad:
                    listadirectriz.append(i - int((i - aux) / 2))
                    c = 0
            c = 0


    return listadirectriz

def linesfull(image, Sensibilidad):

    img = image[:, :, 0]
    ret, thresh1 = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY)

    height = thresh1.shape[0]
    width = thresh1.shape[1]

    listadirectriz = lines(thresh1, Sensibilidad)

    tablas = []

    for k in range(0, len(listadirectriz) - 1):
        if abs(listadirectriz[k] - listadirectriz[k + 1]) > 25:
            tablas.append(listadirectriz[k])

    if len(listadirectriz) > 0:
        tablas.append(listadirectriz[len(listadirectriz) - 1])

        lineasHorizontal = tablas

        font = cv2.FONT_HERSHEY_SIMPLEX
        fontScale = 3
        fontColor = (0, 0, 255)
        lineType = 10

        c = 1

        for t in tablas:
            cv2.line(thresh1, (0, t), (width, t), (0, 255, 0), 10)
            if c % 2 != 0:
                cv2.putText(thresh1, str(c), (0, t), font, fontScale, fontColor, lineType)
            else:
                cv2.putText(thresh1, str(c), (width - 70, t), font, fontScale, fontColor, lineType)
            c += 1

    result = cv2.resize(thresh1, (700, 700))

    return result, tablas

@jit(nopython=True)
def lines(thresh1, Sensibilidad):

    height = thresh1.shape[0]
    width = thresh1.shape[1]

    listadirectriz = []

    for i in range(0, height - 20):

        img_crop = thresh1[i:i + 20, 0:width]
        img_crop_col_aux = np.sum(img_crop, axis=0)

        c = 0
        for k in range(0, width):
            if img_crop_col_aux[k] < 255 * 20:
                c += 1

        if c > width * Sensibilidad:
            listadirectriz.append(i)

        c = 0

    return listadirectriz

class UploadBookView(CreateView):
    model = Book
    form_class = BookForm
    success_url = reverse_lazy('class_book_list')
    template_name = 'upload_book.html'
