import cv2
import numpy as np
import time

# Create background subtractor
subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)

# Capture video from webcam
cap = cv2.VideoCapture(0)

# Initialize HOG descriptor for people detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

prev_gray = None
object_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect people
    boxes, weights = hog.detectMultiScale(frame, winStride=(8,8), padding=(32,32), scale=1.05)
    people_count = len(boxes)

    # Draw people boxes on frame
    for (x, y, w, h) in boxes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Apply background subtraction
    fg_mask = subtractor.apply(frame)

    # Remove shadows (optional, shadows are marked as 127)
    fg_mask[fg_mask == 127] = 0

    # Find contours in the foreground mask
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes for contours larger than a threshold
    current_objects = 0
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Adjust this threshold as needed
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            current_objects += 1

    object_count = current_objects  # Update count

    # Convert to thermal-like image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thermal = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

    # Create night vision effect: brighten and apply green tint
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    night_gray = clahe.apply(gray)
    night = cv2.merge([night_gray // 4, night_gray, night_gray // 4])
    night = cv2.addWeighted(night, 1.0, np.zeros_like(night), 0, 0)

    # Draw people boxes on thermal and night vision
    for (x, y, w, h) in boxes:
        cv2.rectangle(thermal, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.rectangle(night, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Add optical flow for motion vectors
    if prev_gray is not None:
        flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        h, w = flow.shape[:2]
        step = 16
        for y in range(0, h, step):
            for x in range(0, w, step):
                fx, fy = flow[y, x]
                if abs(fx) > 1 or abs(fy) > 1:  # Only draw significant motion
                    cv2.arrowedLine(thermal, (x, y), (int(x + fx), int(y + fy)), (255, 255, 255), 1, tipLength=0.3)
                    cv2.arrowedLine(night, (x, y), (int(x + fx), int(y + fy)), (0, 255, 0), 1, tipLength=0.3)

    prev_gray = gray.copy()

    # Add text overlays
    cv2.putText(thermal, f'People: {people_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(thermal, f'Moving Objects: {current_objects}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(thermal, time.strftime("%H:%M:%S"), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Display the frames
    cv2.imshow('Motion Tracking', frame)
    cv2.imshow('Thermal Motion Tracking', thermal)
    cv2.imshow('Night Vision', night)
    cv2.imshow('Foreground Mask', fg_mask)

    # Exit on 'q' key press
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()