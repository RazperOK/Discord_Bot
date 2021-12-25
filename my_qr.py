import PIL
import qrcode

def make_qr(arg):
    value_qr = str(arg)
    print('Запрошен: ' + value_qr)
    img = qrcode.make(value_qr) # Создание qr-кода
    img.save('myqrcode.png') # Сохранение qr-кода
    return arg
