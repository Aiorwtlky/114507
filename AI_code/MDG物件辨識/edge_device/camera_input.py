import cv2

def get_camera(cap_index=0):
    cap = cv2.VideoCapture(cap_index)
    if not cap.isOpened():
        raise RuntimeError(f"無法開啟攝影機: {cap_index}")
    return cap

def read_frame(cap):
    ret, frame = cap.read()
    if not ret:
        raise RuntimeError("無法讀取影格")
    return frame

def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()
