from PyPDF2 import PdfWriter, PdfReader
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
from pdfplumber import open as plumbopen
from PIL import Image
from pdf2image import convert_from_path
from pytesseract import image_to_string
from os import remove
def text_extraction(element):
    line_text = element.get_text()
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            for character in text_line:
                if isinstance(character, LTChar):
                    line_formats.append(character.fontname)
                    line_formats.append(character.size)
    format_per_line = list(set(line_formats))
    return (line_text, format_per_line)
def crop_image(element, pageObj):
    [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1] 
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    cropped_pdf_writer = PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)
def convert_to_images(input_file,):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")
def image_to_text(image_path):
    img = Image.open(image_path)
    text = image_to_string(img, lang='rus')
    return text

def extract_table(pdf_path, page_num, table_num):
    pdf = plumbopen(pdf_path)
    table_page = pdf.pages[page_num]
    table = table_page.extract_tables()[table_num]
    return table
def table_converter(table):
    table_string = ''
    for row_num in range(len(table)):
        row = table[row_num]
        cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
        table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
    table_string = table_string[:-1]
    return table_string
def convert(pdf_path:str):    
    label.configure(text='Страницы: ')
    pdfFileObj = open(pdf_path, 'rb')
    pdfReaded = PdfReader(pdfFileObj)
    text_per_page = {}
    text_file = open(pdf_path.replace(pdf_path[len(pdf_path) - 3:], "txt"), 'w')
    result=''
    for pagenum, page in enumerate(extract_pages(pdf_path, maxpages=100)):
        show_page(pagenum)
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        table_num = 0
        first_element= True
        table_extraction_flag= False
        pdf = plumbopen(pdf_path)
        page_tables = pdf.pages[pagenum]
        tables = page_tables.find_tables()
        page_elements = [(element.y1, element) for element in page._objs]
        page_elements.sort(key=lambda a: a[0], reverse=True)

        for i,component in enumerate(page_elements):
            pos= component[0]
            element = component[1]
            if isinstance(element, LTTextContainer):
                if table_extraction_flag == False:
                    (line_text, format_per_line) = text_extraction(element)
                    page_text.append(line_text)
                    line_format.append(format_per_line)
                    page_content.append(line_text)
                else:
                    pass
            if isinstance(element, LTFigure):
                pass
                crop_image(element, pageObj)
                convert_to_images('cropped_image.pdf')
                image_text = image_to_text('PDF_image.png')
                text_from_images.append(image_text)
                page_content.append(image_text)
                page_text.append('image')
                line_format.append('image')
            if isinstance(element, LTRect):
                if first_element == True and (table_num+1) <= len(tables):
                    lower_side = page.bbox[3] - tables[table_num].bbox[3]
                    upper_side = element.y1 
                    table = extract_table(pdf_path, pagenum, table_num)
                    table_string = table_converter(table)
                    text_from_tables.append(table_string)
                    page_content.append(table_string)
                    table_extraction_flag = True
                    first_element = False
                    page_text.append('table')
                    line_format.append('table')
                if element.y0 >= lower_side and element.y1 <= upper_side:
                    pass
                elif not isinstance(page_elements[i+1][1], LTRect):
                    table_extraction_flag = False
                    first_element = True
                    table_num+=1
        dctkey = 'Page_'+str(pagenum)
        text_per_page[dctkey]= [page_text, line_format, text_from_images,text_from_tables, page_content]
        #print(str(text_per_page[dctkey]))
        num=0

        for item in text_per_page[dctkey]:
            for sub_item in item:
                if(type(sub_item) is list):
                    for sub_sub_item in sub_item:
                        if(type(sub_sub_item) is list):
                            for sub_sub_sub_item in sub_sub_item:
                                result+=str(sub_sub_sub_item)
                        else:
                            result+=str(sub_sub_item)
                else:
                    result += str(sub_item)            
    text_file.write(result)
    pdfFileObj.close()
    remove('cropped_image.pdf')
    remove('PDF_image.png')
    #result = ''.join(text_per_page['Page_0'][4])
    #print(pdf_path.replace(pdf_path[len(pdf_path) - 3:], "txt"))
    text_file.close()
    label.configure(text='Файл конвертирован')
    window.update()




# Python program to create 
# a file explorer in Tkinter

# import all components
# from the tkinter library
from tkinter import Button, Tk, Label

# import filedialog module
from tkinter import filedialog


																								
# Create the root window
window = Tk()

# Set window title
window.title('Scan Converter')

# Set window size
window.geometry("200x100")

#Set window background color
window.config(background = "white")
# Function for opening the 
# file explorer window
def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",title = "Select a File", filetypes = (("Text files", "*.pdf*"), ("all files", "*.*")))
    if(type(filename)==str):
        convert(filename)
label = Label(window, text = 'Выберите файл')
window.current_page = -1
def show_page(page:int):
    if(window.current_page<=page):
        window.current_page = page
        label.configure(text=label.cget("text")+" "+str(page))
        window.update()
    else:
        window.current_page = page
        label.configure(text='Страницы: '+str(page))
        window.update()


	
button_explore = Button(window, 
						text = "Выбрать файл",
						command = browseFiles) 


# Grid method is chosen for placing
# the widgets at respective positions 
# in a table like structure by
# specifying rows and columns
button_explore.pack(anchor= "center", pady = 10)
label.pack(anchor='center')

# Let the window wait for any events
if __name__ == '__main__':
    window.mainloop()
#  /home/kuznetsov/projects/input_scans/Осидак_Л_В_ 2013 Арбидол_и_тамифлю_лечение_гриппа_как_пре.pdf