import cv2
import pytesseract

# โหลดรูป
img = cv2.imread('/home/sain/vs code/Med_project/vision-med/src/images/Messenger_creation_AF5AA839-1EB0-4B19-890A-4EDD98795A96.jpg')

# Preprocess
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5,5), 0)
thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY_INV)[1]

# หา contour
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# หาฉลากที่ใหญ่ที่สุด
label_contour = None
max_area = 0

for cnt in contours:
    area = cv2.contourArea(cnt)
    if area > max_area:
        max_area = area
        label_contour = cnt

# ถ้ามีเจอ
if label_contour is not None:
    x, y, w, h = cv2.boundingRect(label_contour)
    label_roi = img[y:y+h, x:x+w]  # ตัดเฉพาะฉลากออกมา

    # OCR เฉพาะฉลาก
    label_text = pytesseract.image_to_string(label_roi, lang='tha+eng')
    print(label_text)

else:
    print("ไม่เจอฉลากยาในภาพ")


    