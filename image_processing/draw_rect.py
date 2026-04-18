import cv2

if __name__ == "__main__":
    img_path = "GX010609_5495_fn_49770.jpg"
    img = cv2.imread(img_path)
    x_min = 11
    y_min = 989
    x_max = 356
    y_max = 1220

    cv2.imshow("Before", img)

    cv2.waitKey (0)

    img_with_box = cv2.rectangle(img, (x_min,y_min),(x_min + x_max, y_min + y_max), (0, 255, 0), 5)

    cv2.imshow("After", img_with_box)

    cv2.waitKey (0)

    cv2.destroyAllWindows()