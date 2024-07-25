import cv2
import pytesseract

# Caminho da imagem
image_path = r"L:\Documentos\Scrapping\Cp.png"

# Lendo a imagem com OpenCV
imagem = cv2.imread(image_path)

# Verificando se a imagem foi lida corretamente
if imagem is None:
    print(f"Erro ao ler a imagem em {image_path}")
else:
    # Caminho para o executável do Tesseract
    tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    # Verificando se o Tesseract está acessível
    try:
        txt = pytesseract.image_to_string(imagem)
        print(txt)
    except pytesseract.TesseractNotFoundError as e:
        print(f"Tesseract não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
