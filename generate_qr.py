import qrcode

website_url = "http://172.20.10.13:5000"

qr = qrcode.QRCode(
    version=1,
    box_size=10,
    border=4
)

qr.add_data(website_url)
qr.make(fit=True)

image = qr.make_image(
    fill_color="black",
    back_color="white"
)

image.save("library_qr.png")

print("QR Code successfully created!")
print("File name: library_qr.png")